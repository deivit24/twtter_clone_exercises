"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

GENERIC_IMAGE = "https://mylostpetalert.com/wp-content/themes/mlpa-child/images/nophoto.gif"

class MessageViewTestCase(TestCase):
    """Test views for messages."""

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

    def test_add_message(self):
        """Can use add a message?"""


        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.david_id

            res = client.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(res.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_message_noauth(self):
        """Can use add a message while not signedup"""

        with app.test_client() as client:
            res = client.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn("Access unauthorized", html)

    def test_add_message_invalid_auth(self):
        """Can use add a message with invalid user"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1000
            
            res = client.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn("Access unauthorized", html)

    # Displaying Messages:
    def test_message_show(self):

        m = Message(
            id=1000,
            text="test test",
            user_id=self.david_id
        )
        
        db.session.add(m)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.david_id
            
            m = Message.query.get(1000)

            res = client.get(f'/messages/{m.id}', follow_redirects=True)
            
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn("test test", html)
    
    def test_message_invalid_show(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.david_id
            
            res = client.get('/messages/1234', follow_redirects=True)

            self.assertEqual(res.status_code, 404)
    
    def test_delete_message(self):
        m = Message(
            id=1000,
            text="test test",
            user_id=self.david_id
        )
        
        db.session.add(m)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.david_id
            
            m = Message.query.get(1000)

            res = client.post('/messages/1000/delete', follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            m = Message.query.get(1000)
            self.assertIsNone(m)
            self.assertIn("Message deleted", html)

    def test_delete_message_unaut(self): 
        m = Message(
            id=1000,
            text="test test",
            user_id=self.david_id
        )
        db.session.add(m)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.jorge_id

            res = client.post('/messages/1000/delete', follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            self.assertIn("Access unauthorized", html)
            m = Message.query.get(1000)
            self.assertIsNotNone(m)

    def test_delete_message_no_aut(self): 
        m = Message(
            id=1000,
            text="test test",
            user_id=self.david_id
        )
        db.session.add(m)
        db.session.commit()

        with app.test_client() as client:
            res = client.post('/messages/1000/delete', follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            self.assertIn("Access unauthorized", html)

            m = Message.query.get(1000)
            self.assertIsNotNone(m)