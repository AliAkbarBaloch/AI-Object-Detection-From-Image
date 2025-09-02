import unittest
from models.model import count_objects
from PIL import Image
import os
import numpy as np

class ModelPipelineTestCase(unittest.TestCase):
    def test_count_objects(self):
        test_image_path = os.path.join(os.path.dirname(__file__), '../uploads/image.png')
        image_np = np.array(Image.open(test_image_path)).astype(np.float32)
        # result = count_objects(test_image_path, 'car')
        result = count_objects(image_np, 'car')
        self.assertIn('count', result)
        self.assertIn('labels', result)
        self.assertIn('segments', result)
        self.assertIsInstance(result['count'], int)
        self.assertIsInstance(result['labels'], list)
        self.assertIsInstance(result['segments'], int)

if __name__ == '__main__':
    unittest.main()
