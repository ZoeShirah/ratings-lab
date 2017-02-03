import unittest

from server import app
from model import db, example_data, connect_to_db


class RatingTests(unittest.TestCase):
    """Tests for our rating site."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_homepage(self):
        result = self.client.get("/")
        self.assertIn("View all movies", result.data)

    def test_all_movies(self):
        # FIXME: Add a test to show we see the RSVP form, but NOT the
        # party details
        result = self.client.get('/movies')
        self.assertIn('101 Dalmations', result.data)
        self.assertNotIn('franzi@franzi.com', result.data)

    def test_sign_in(self):
        result = self.client.post("/sign-in",
                                  data={"username": "eye@judgeyou.com",
                                        "password": "usuk"},
                                  follow_redirects=True)
        # FIXME: Once we RSVP, we should see the party details, but
        # not the RSVP form
        self.assertNotIn('Movies', result.data)
        self.assertIn('Sign In', result.data)


class PartyTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database (uncomment when testing database)
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data (uncomment when testing database)
        db.create_all()
        example_data()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = True

    def tearDown(self):
        """Do at end of every test."""

        # (uncomment when testing database)
        db.session.close()
        db.drop_all()

    # def test_g(self):
    #     #FIXME: test that the games page displays the game from example_data()
    #     result = self.client.get('/')
    #     self.assertIn('test game 1', result.data)



if __name__ == "__main__":
    unittest.main()
