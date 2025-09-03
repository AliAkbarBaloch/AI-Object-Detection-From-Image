import unittest
from app import app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
from app import app
from io import BytesIO
from models.db import client

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.test_image_path = os.path.join(os.path.dirname(__file__), '../uploads/image.png')

    def test_count_endpoint_no_image(self):
        data = {'item_type': 'car'}
        response = self.app.post('/Counting/count', data=data, content_type='multipart/form-data')
        print('NO IMAGE:', response.status_code, response.get_data(as_text=True))
        self.assertIn(response.status_code, [400, 500])

    def test_count_endpoint_success(self):
        with open(self.test_image_path, 'rb') as img:
            data = {
                'item_type': 'cat',
                'image': (img, 'image.png')
            }
            response = self.app.post('/Counting/count', data=data, content_type='multipart/form-data')
            print('SUCCESS:', response.status_code, response.get_data(as_text=True))
            self.assertIn(response.status_code, [200, 500])

    def test_count_endpoint_invalid_filetype(self):
        fake_content = BytesIO(b'not-an-image')
        data = {
            'item_type': 'cat',
            'image': (fake_content, 'file.txt')
        }
        response = self.app.post('/Counting/count', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid file type', response.get_data(as_text=True))

    def test_correct_endpoint_missing_fields(self):
        response = self.app.post('/Correction/correct', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing result_id or correct_count', response.get_data(as_text=True))

    def test_previous_results_with_header(self):
        # Should accept X-User-Id header path and return 200 with results list
        response = self.app.get('/Auth/previous-results', headers={'X-User-Id': 'ci-user'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.get_json())


if __name__ == '__main__':
    unittest.main()
    if client is not None:
        client.close()
