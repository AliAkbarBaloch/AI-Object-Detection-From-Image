from app import app  # import app, not api
from flask import request
from flask_restx import Resource, fields

# Access Api via app.api
api = app.api

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os


count_parser = api.parser()
count_parser.add_argument('item_type', type=str, required=True, help='Type of item to count')
count_parser.add_argument('image', location='files', type=FileStorage, required=True, help='Image file')

correct_model = api.model('Correct', {
    'result_id': fields.String(required=True, description='ID of the result to correct'),
    'correct_count': fields.Integer(required=True, description='Corrected count'),
})

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from models.model import count_objects
from models.db import save_result, update_correction

@api.route('/api/count')
class CountResource(Resource):
    @api.expect(count_parser)
    def post(self):
        try:
            args = count_parser.parse_args()
            item_type = args.get('item_type')
            image_file = args.get('image')
            if not item_type:
                return {'error': 'Missing item_type'}, 400
            if not image_file:
                return {'error': 'No image uploaded'}, 400
            if not hasattr(image_file, 'filename') or not image_file.filename:
                return {'error': 'No image uploaded'}, 400
            if not image_file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                return {'error': 'Invalid file type'}, 400
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                image_file.save(image_path)
            except Exception as e:
                return {'error': f'Failed to save image: {str(e)}'}, 500
            try:
                result = count_objects(image_path, item_type)
            except Exception as e:
                return {'error': f'Model error: {str(e)}'}, 500
            try:
                result_id = save_result(image_path, item_type, result['count'])
            except Exception as e:
                return {'error': f'Database error: {str(e)}'}, 500
            return {
                'result_id': str(result_id),
                'count': result['count'],
                'labels': result['labels'],
                'segments': result['segments']
            }, 200
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'error': f'Unexpected error: {str(e)}'}, 500

@api.route('/api/correct')
class CorrectResource(Resource):
    @api.expect(correct_model)
    def post(self):
        try:
            data = request.json
            result_id = data.get('result_id')
            correct_count = data.get('correct_count')
            if not result_id or correct_count is None:
                return {'error': 'Missing result_id or correct_count'}, 400
            try:
                update_correction(result_id, correct_count)
            except Exception as e:
                return {'error': f'Database error: {str(e)}'}, 500
            return {'message': 'Correction saved'}, 200
        except Exception as e:
            return {'error': f'Unexpected error: {str(e)}'}, 500
