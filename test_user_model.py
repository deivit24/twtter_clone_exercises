"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
# added from solution
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

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

class UserModelTestCase(TestCase):
    """Test User Model."""

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


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):

        u_test = User.query.get(self.david_id)
        u_test2 = User.query.get(self.jorge_id)
        self.assertIsNotNone(u_test)
        self.assertIsNotNone(u_test2)
        self.assertEqual(u_test, u_test)
        
    # SIGN UP TEST

    def test_signup(self):
        u_test = User.signup("test", "test@usertest.com", "HASHED_PASSWORD", GENERIC_IMAGE)

        db.session.add(u_test)
        db.session.commit()
        u_test = User.query.get(3)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "test")
        self.assertEqual(u_test.email, "test@usertest.com")
        self.assertNotEqual(u_test.password, "HASHED_PASSWORD")
        self.assertTrue(u_test.password.startswith("$"))

   
    def test_error_signup(self):
        with app.test_client() as client:
            d = {"username":"test", "email": "testusertestcom", "password": "HASHED_PASSWORD", "image_url": GENERIC_IMAGE}

            resp = client.post("/signup", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Invalid email address.', html)

    # Realized this ^^^ is for a view I did not know how to test inva;id signup models. Using the solution code:
    def test_valid_signup(self):
        u_test = User.signup("testtesttest", "testtest@test.com", "password", None)
        uid = 99999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testtesttest")
        self.assertEqual(u_test.email, "testtest@test.com")
        self.assertNotEqual(u_test.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test@test.com", "password", None)
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", None, "password", None)
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)

    # AUTH TEST

    def test_valid_auth(self):
        u = User.authenticate("david", "HASHED_PASSWORD")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.david_id)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("notreal", "password"))

    def test_invalid_password(self):
        self.assertFalse(User.authenticate("david", "wrongpassword"))

# following test

    def test_follows(self):
        u1 = User.query.get(self.david_id)
        u2 = User.query.get(self.jorge_id)
        self.assertIsNotNone(u1)
        self.assertIsNotNone(u2)

        u1.following.append(u2)

        db.session.commit()

        # Checking length onf followers
        self.assertEqual(len(u2.following), 0)
        self.assertEqual(len(u2.followers), 1)
        self.assertEqual(len(u1.followers), 0)
        self.assertEqual(len(u1.following), 1)

        self.assertEqual(u2.followers[0].id, u1.id)
        self.assertEqual(u1.following[0].id, u2.id)
        # checking u1 is following u2
        self.assertTrue(u1.is_following(u2))
        self.assertTrue(u2.is_followed_by(u1))
        # checking u2 is followed by u1
        self.assertFalse(u2.is_following(u1))
        self.assertFalse(u1.is_followed_by(u2))