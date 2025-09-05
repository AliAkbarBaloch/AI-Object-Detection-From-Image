import unittest
from app import app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
from app import app
from io import BytesIO
from models.db import client
from unittest.mock import patch

class APITestCase(unittest.TestCase):

    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # self.test_image_path = os.path.join(os.path.dirname(__file__), '../uploads/image.png')
        self.test_image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads', 'image.png'))

    def test_count_endpoint_no_image(self):
        data = {'item_type': 'car'}
        response = self.app.post('/Counting/count', data=data, content_type='multipart/form-data')
        print('NO IMAGE:', response.status_code, response.get_data(as_text=True))
        self.assertIn(response.status_code, [400, 500])

    @unittest.skipIf(os.getenv("CI") == "true", "Skip in CI")
    def test_count_endpoint_success(self):
        with patch('app.routes.save_result'):
            with open(self.test_image_path, 'rb') as img:
                data = {
                    'item_type': 'cat',
                    'image': (img, 'image.png')
                }
                response = self.app.post('/Counting/count', data=data, content_type='multipart/form-data')
                print('SUCCESS:', response.status_code, response.get_data(as_text=True))
                self.assertEqual(response.status_code, 200)
                body = response.get_json()
                self.assertIn('labels', body)
                self.assertIn('segments', body)

    def test_correct_endpoint_missing_fields(self):
        response = self.app.post('/Correction/correct', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing result_id or correct_count', response.get_data(as_text=True))

    def test_count_endpoint_missing_item_type(self):
        with open(self.test_image_path, 'rb') as img:
            data = {
                # 'item_type' intentionally missing
                'image': (img, 'image.png')
            }
            response = self.app.post('/Counting/count', data=data, content_type='multipart/form-data')
            print('MISSING ITEM TYPE:', response.status_code, response.get_data(as_text=True))
            self.assertEqual(response.status_code, 400)

    def test_count_endpoint_invalid_file_type(self):
        fake_file = BytesIO(b'not-an-image')
        data = {
            'item_type': 'dog',
            'image': (fake_file, 'file.txt')
        }
        response = self.app.post('/Counting/count', data=data, content_type='multipart/form-data')
        print('INVALID FILE:', response.status_code, response.get_data(as_text=True))
        self.assertEqual(response.status_code, 400)

    def test_correct_endpoint_invalid_id_error(self):
        payload = { 'result_id': 'not-an-objectid', 'correct_count': 2 }
        with patch('app.routes.update_correction', side_effect=Exception('invalid ObjectId')):
            response = self.app.post('/Correction/correct', json=payload)
            print('CORRECT INVALID ID:', response.status_code, response.get_data(as_text=True))
            self.assertEqual(response.status_code, 500)
            self.assertIn('Database error', response.get_data(as_text=True))
    @unittest.skipIf(os.getenv("CI") == "true", "Skip in CI")
    def test_batch_count_endpoint_success(self):
        # Patch save_result to avoid DB dependency
        with patch('app.routes.save_result'):
            with open(self.test_image_path, 'rb') as img1, open(self.test_image_path, 'rb') as img2:
                data = {
                    'item_type': 'cat',
                    'images': [
                        (img1, 'image1.png'),
                        (img2, 'image2.png')
                    ]
                }
                response = self.app.post('/Counting/batch_count', data=data, content_type='multipart/form-data')
                print('BATCH SUCCESS:', response.status_code, response.get_data(as_text=True))
                self.assertEqual(response.status_code, 200)
                body = response.get_json()
                self.assertIn('results', body)
                self.assertIsInstance(body['results'], list)
                self.assertGreaterEqual(len(body['results']), 2)

    def test_batch_count_endpoint_missing_fields(self):
        response = self.app.post('/Counting/batch_count', data={}, content_type='multipart/form-data')
        print('BATCH MISSING FIELDS:', response.status_code, response.get_data(as_text=True))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Input payload validation failed', response.get_data(as_text=True))

    def test_batch_count_endpoint_invalid_file_type(self):
        fake_file = BytesIO(b'not-an-image')
        data = {
            'item_type': 'cat',
            'images': [
                (fake_file, 'file.txt')
            ]
        }
        response = self.app.post('/Counting/batch_count', data=data, content_type='multipart/form-data')
        print('BATCH INVALID FILE:', response.status_code, response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertIn('results', body)
        self.assertIsInstance(body['results'], list)
        # Should skip invalid file, so results may be empty or contain error
        if body['results']:
            self.assertIn('error', body['results'][0])

if __name__ == '__main__':
    unittest.main()
    if client is not None:
        client.close()
