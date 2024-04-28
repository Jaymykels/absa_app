import unittest
from flask.testing import FlaskClient  


from app import app 

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.testing = True  
        self.client = FlaskClient(app) 

    def tearDown(self):
        # Any necessary cleanup after tests 
        pass

    # Test 1: Check if the homepage renders correctly (GET request)
    def test_index_get(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Opinion Target', response.data) # Sample check
        print("Test 1 Passed: Homepage loads successfully") 

    # Test 2: Simulate a POST request with form data
    def test_index_post(self):
        data = {'target': 'Example Target', 'category': 'Example Category'}
        response = self.client.post('/', data=data)
        self.assertEqual(response.status_code, 200)
        print("Test 2 Passed: Form submission successful") 


if __name__ == '__main__':
    unittest.main()
