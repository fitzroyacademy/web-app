from app import app
import unittest

class TestModels(unittest.TestCase):

    def test_homepage(self):
        s = app.test_client()
        response = s.get('/')
        self.assertEqual(response.status_code, 200)
