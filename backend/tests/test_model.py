import unittest
from models.model import count_objects
import os
from models.db import client
import os

@unittest.skipIf(os.getenv("CI") == "true", "Skip heavy model pipeline test in CI environment")
class ModelPipelineTestCase(unittest.TestCase):
    def test_count_objects(self):
        test_image_path = os.path.join(os.path.dirname(__file__), '../uploads/image.png')
        result = count_objects(test_image_path, 'car')
        self.assertIn('count', result)
        self.assertIn('labels', result)
        self.assertIn('segments', result)
        self.assertIsInstance(result['count'], int)
        self.assertIsInstance(result['labels'], list)
        self.assertIsInstance(result['segments'], int)

if __name__ == '__main__':
    unittest.main()
    if client is not None:
        client.close()
