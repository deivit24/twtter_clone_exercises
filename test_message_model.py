"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


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


class MessageModelTestCase(TestCase):
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

    def test_message_model(self):
        """Does basic model work?"""
        
        u = User.query.get(self.david_id)

        m = Message(
            text="test test",
            user_id=u.id
        )

        db.session.add(m)
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(u.messages), 1)
        self.assertEqual(u.messages[0].text, "test test")

    def test_user_message_likes(self):
        u1 = User.query.get(self.david_id)
        u2 = User.query.get(self.jorge_id)

        m1 = Message(
            text="test test",
            user_id=u1.id
        )

        m2 = Message(
            text="test test test",
            user_id=u1.id 
        )

        db.session.add_all([m1, m2])
        db.session.commit()

        u2.likes.append(m1)
        db.session.commit()

        like = Likes.query.filter(Likes.user_id == u2.id).all()

        self.assertEqual(len(like), 1)
        self.assertEqual(like[0].message_id, m1.id)