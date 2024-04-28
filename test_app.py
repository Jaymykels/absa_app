import unittest
from flask.testing import FlaskClient  
from bs4 import BeautifulSoup


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

    def test_positive_polarity(self):
     data = {'target': 'This product is fantastic!', 'category': 'Service'}  # Positive sentiment
     response = self.client.post('/', data=data)
     self.assertEqual(response.status_code, 200)

    # Extract and assert the result (adjust parsing based on your HTML structure)
     soup = BeautifulSoup(response.data, 'html.parser')
     result_span = soup.find('span', class_='badge')

     if result_span:
        result = result_span.text.strip()
        self.assertEqual(result, 'positive') 
        print("Test 3 Passed: Positive polarity detected") 
     else:
        self.fail("Result not found in the response")


    def test_negative_polarity(self):
     data = {'target': 'The product is bad!, terrible, do not patronize', 'category': 'Service'}  # Positive sentiment
     response = self.client.post('/', data=data)
     self.assertEqual(response.status_code, 200)

    # Extract and assert the result (adjust parsing based on your HTML structure)
     soup = BeautifulSoup(response.data, 'html.parser')
     result_span = soup.find('span', class_='badge')

     if result_span:
        result = result_span.text.strip()
        self.assertEqual(result, 'negative') 
        print("Test 4 Passed: Negative polarity detected") 
     else:
        self.fail("Result not found in the response")


if __name__ == '__main__':
    unittest.main()
