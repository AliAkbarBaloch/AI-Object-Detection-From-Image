import os
import unittest
from unittest.mock import patch, MagicMock

os.environ.setdefault('CI', 'true')

from app import app


class RoutesBranchTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_count_missing_item_type_via_mock(self):
        with patch('app.routes.count_parser.parse_args', return_value={'item_type': '', 'image': None}):
            resp = self.client.post('/Counting/count', data={}, content_type='multipart/form-data')
            self.assertEqual(resp.status_code, 400)
            self.assertIn('Missing item_type', resp.get_data(as_text=True))

    def test_count_missing_image_via_mock(self):
        with patch('app.routes.count_parser.parse_args', return_value={'item_type': 'cat', 'image': None}):
            resp = self.client.post('/Counting/count', data={}, content_type='multipart/form-data')
            self.assertEqual(resp.status_code, 400)
            self.assertIn('No image uploaded', resp.get_data(as_text=True))

    def test_count_no_filename_via_mock(self):
        fake = MagicMock()
        fake.filename = ''
        with patch('app.routes.count_parser.parse_args', return_value={'item_type': 'cat', 'image': fake}):
            resp = self.client.post('/Counting/count', data={}, content_type='multipart/form-data')
            self.assertEqual(resp.status_code, 400)
            self.assertIn('No image uploaded', resp.get_data(as_text=True))

    def test_count_failed_save_image(self):
        fake = MagicMock()
        fake.filename = 'image.png'
        fake.save.side_effect = Exception('disk full')
        with patch('app.routes.count_parser.parse_args', return_value={'item_type': 'cat', 'image': fake}):
            resp = self.client.post('/Counting/count', data={}, content_type='multipart/form-data')
            self.assertEqual(resp.status_code, 500)
            self.assertIn('Failed to save image', resp.get_data(as_text=True))

    def test_count_db_error(self):
        fake = MagicMock()
        fake.filename = 'image.png'
        fake.save.return_value = None
        with patch('app.routes.count_parser.parse_args', return_value={'item_type': 'cat', 'image': fake}):
            with patch('app.routes.count_objects', return_value={'count': 1, 'labels': ['cat'], 'segments': 1}):
                with patch('app.routes.save_result', side_effect=Exception('db down')):
                    resp = self.client.post('/Counting/count', data={}, content_type='multipart/form-data')
                    self.assertEqual(resp.status_code, 500)
                    self.assertIn('Database error', resp.get_data(as_text=True))

    def test_count_success_mocked(self):
        fake = MagicMock()
        fake.filename = 'image.png'
        fake.save.return_value = None
        with patch('app.routes.count_parser.parse_args', return_value={'item_type': 'cat', 'image': fake}):
            with patch('app.routes.count_objects', return_value={'count': 2, 'labels': ['cat', 'dog'], 'segments': 2}):
                with patch('app.routes.save_result', return_value='id123'):
                    resp = self.client.post('/Counting/count', data={}, content_type='multipart/form-data')
                    self.assertEqual(resp.status_code, 200)
                    data = resp.get_json()
                    self.assertEqual(data['count'], 2)
                    self.assertEqual(data['result_id'], 'id123')

    def test_correct_success(self):
        with patch('app.routes.update_correction', return_value=None):
            resp = self.client.post('/Correction/correct', json={'result_id': 'abc', 'correct_count': 3})
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Correction saved', resp.get_data(as_text=True))

    def test_correct_db_error(self):
        with patch('app.routes.update_correction', side_effect=Exception('db err')):
            resp = self.client.post('/Correction/correct', json={'result_id': 'abc', 'correct_count': 3})
            self.assertEqual(resp.status_code, 500)
            self.assertIn('Database error', resp.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
