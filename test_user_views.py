"""User views tests."""

# run these tests like:
#
#    python -m unittest test_user_views.py


import os
from unittest import TestCase
# added from solution
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

app.config['SQLALCHEMY_ECHO'] = False
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True
# Don't req CSRF for testing
app.config['WTF_CSRF_ENABLED'] = False

db.create_all()

GENERIC_IMAGE = "https://mylostpetalert.com/wp-content/themes/mlpa-child/images/nophoto.gif"

class UserViewTestCase(TestCase):
    """Test views for Users."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        david = User.signup("david", "test@test1.com", "HASHED_PASSWORD", GENERIC_IMAGE)
        jorge = User.signup("jorge", "test@test2.com", "HASHED_PASSWORD", GENERIC_IMAGE)

        db.session.add(david)
        db.session.add(jorge)
        db.session.commit()

        
        self.david_id = david.id 
        self.jorge_id = jorge.id
      


    def tearDown(self):
        db.session.rollback()

# TESTING ROOT ROUTES

    def test_home_route_no_user(self):
        """Testiing home route as not a user"""
        with app.test_client() as client:
            res = client.get("/")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("What's Happening?", html)
    
    def test_home_route_with_user(self):
        """Testiing home route as a user"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.david_id
                
            res = client.get("/")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("@david", html)
    
    # TESTING users route
    
    def test_users_route(self):
        """Testiing users route as logged in"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.david_id    
            
            res = client.get("/users")
            html = res.get_data(as_text=True)

            self.assertIn("@david", html)
            self.assertIn("@jorge", html)
    
    def test_users_search_route(self):
        """Testing search routes"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.david_id

            res = client.get("/users?q=david")
            html = res.get_data(as_text=True)

            self.assertIn("@david", html)
            self.assertNotIn("@jorge", html)
    
    def test_users_userid_route(self):
        """ Testing users show route as user and not user"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.david_id

            res = client.get(f"/users/{self.david_id}")
            html = res.get_data(as_text=True)

            self.assertIn("Edit Profile", html)

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.jorge_id
            
            res = client.get(f"/users/{self.david_id}")
            html = res.get_data(as_text=True)

            self.assertIn("follow", html)
            self.assertNotIn("Edit Profile", html)

    # TESTING LIKE View

    def test_users_userid_with_likes(self):
        """ Testing users show route as user with likes"""
        m1 = Message(text="test test", user_id=self.david_id)
        
        db.session.add(m1)
        db.session.commit()

        like = Likes(user_id=self.david_id, message_id=m1.id)

        db.session.add(like)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.david_id

            res = client.get(f"/users/{self.david_id}")
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("@david", html)
            self.assertIn('/likes">1</a>', html)
        
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.jorge_id

            res = client.get(f"/users/{self.jorge_id}")
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("@jorge", html)
            self.assertIn('/likes">0</a>', html)

    def test_users_add_like(self):
        """Test Add a like"""
        m1 = Message(id=24, text="test test", user_id=self.david_id)
        
        db.session.add(m1)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.david_id
            
            res = client.post("/users/add_like/24", follow_redirects=True)
            self.assertEqual(res.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==24).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.david_id)

    def test_toggle_like(self):
        m1 = Message(id=500, text="test test", user_id=self.david_id)
        
        db.session.add(m1)
        db.session.commit()

        like = Likes(user_id=self.jorge_id, message_id=m1.id)

        db.session.add(like)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.jorge_id
            
            m = Message.query.filter(Message.text=="test test").one()

            self.assertIsNotNone(m)
            self.assertNotEqual(m.user_id, self.jorge_id)

            like = Likes.query.filter(
            Likes.user_id==self.jorge_id and Likes.message_id==m.id).one()

            self.assertIsNotNone(like)

            res = client.post("/users/add_like/500", follow_redirects=True)
            self.assertEqual(res.status_code, 200)

            toggle_like = Likes.query.all()

            
            self.assertEqual(len(toggle_like), 0)
    
    def test_unauth_like(self):
        m1 = Message(id=500, text="test test", user_id=self.david_id)
        
        db.session.add(m1)
        db.session.commit()

        like = Likes(user_id=self.david_id, message_id=m1.id)

        db.session.add(like)
        db.session.commit()

        m = Message.query.filter(Message.id==500).one()
        self.assertIsNotNone(m)

        with app.test_client() as client:
            
            res = client.post("/users/add_like/500", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            self.assertIn("Access unauthorized", html)

    # TESTING FOLLOWERS
    # Also just found out I have been duplication alot of code within tests the following code will speed up and make it DRY

    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.david_id, user_following_id=self.jorge_id)
        f2 = Follows(user_being_followed_id=self.jorge_id, user_following_id=self.david_id)
       

        db.session.add_all([f1,f2])
        db.session.commit()

    def test_user_show_with_follows(self):
        self.setup_followers()

        with app.test_client() as client:
            res = client.get(f"/users/{self.david_id}", follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            self.assertIn("@david", html)
            self.assertIn('following"\n                >1', html)
            self.assertIn('followers"\n                >1', html)
      
    def test_show_following_and_followers(self):

        self.setup_followers()
        with app.test_client() as client:
            with client.session_transaction() as sess:
              sess[CURR_USER_KEY] = self.david_id

            # Testing how many are following
            res = client.get(f"/users/{self.david_id}/following", follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            self.assertIn("@jorge", html)

            # Testing how many are followers
            res = client.get(f"/users/{self.david_id}/followers", follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            self.assertIn("@jorge", html)
    
    def test_following_and_followers_unauth(self):

        self.setup_followers()

        with app.test_client() as client:
            res = client.get(f"/users/{self.david_id}/following", follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            self.assertIn("Access unauthorized", html)

            res = client.get(f"/users/{self.david_id}/followers", follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            self.assertIn("Access unauthorized", html)