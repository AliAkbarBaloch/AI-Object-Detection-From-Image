from app import app  # import app, not api
from flask import request
from flask_restx import Resource, fields
from werkzeug.exceptions import BadRequest

# Access Api via app.api
api = app.api

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os
from flask_restx import Namespace

count_ns = Namespace("Counting", path="/Counting", description="Endpoints for counting objects in images")
correct_ns = Namespace("Correction", path="/Correction", description="Endpoints for correcting object counts")
auth_ns = Namespace("Auth", path="/Auth", description="User authentication and history endpoints")

api.add_namespace(count_ns)
api.add_namespace(correct_ns)
api.add_namespace(auth_ns)


count_parser = count_ns.parser()
count_parser.add_argument('item_type', type=str, required=True, help='Type of item to count')
count_parser.add_argument('image', location='files', type=FileStorage, required=True, help='Image file')

correct_model = correct_ns.model('Correct', {
    'result_id': fields.String(required=True, description='ID of the result to correct'),
    'correct_count': fields.Integer(required=True, description='Corrected count'),
})

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from models.model import count_objects
from models.db import (
    save_result,
    update_correction,
    create_user,
    verify_user,
    get_user_by_email,
    get_password_for_email,
    get_results_for_user,
    results_collection,
)

@count_ns.route('/count')
class CountResource(Resource):
    @count_ns.expect(count_parser)
    @count_ns.doc(description="Upload an image and get object count, labels, and segments")
    def post(self):
        try:
            try:
                args = count_parser.parse_args()
            except BadRequest as e:
                return {'error': 'Input payload validation failed', 'message': str(e)}, 400
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
            # Best-effort: also persist a string 'result_id' field into the same document for convenient lookups
            try:
                if results_collection is not None:
                    results_collection.update_one({'_id': result_id}, {'$set': {'result_id': str(result_id)}})
            except Exception:
                # Don't fail the request if this auxiliary update fails
                pass
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

@correct_ns.route('/correct')
class CorrectResource(Resource):
    @correct_ns.expect(correct_model)
    @correct_ns.doc(description="Submit corrected count for a previous result")
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



# -----------------------
# Auth and user endpoints
# -----------------------

register_model = auth_ns.model('Register', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
})

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
})

forgot_model = auth_ns.model('ForgotPassword', {
    'email': fields.String(required=True, description='User email'),
})


@auth_ns.route('/register')
class RegisterResource(Resource):
    @auth_ns.expect(register_model)
    def post(self):
        data = request.json or {}
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return {'error': 'email and password are required'}, 400
        # If user exists, instruct to login
        if get_user_by_email(email):
            return {'message': 'User already exists. Please login.'}, 200
        uid = create_user(email, password)
        if uid is None:
            return {'message': 'User already exists. Please login.'}, 200
        return {'message': 'Registered successfully', 'user_id': str(uid)}, 201


@auth_ns.route('/login')
class LoginResource(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        data = request.json or {}
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return {'error': 'email and password are required'}, 400
        user = verify_user(email, password)
        if not user:
            return {'error': 'Invalid credentials'}, 401
        return {'message': 'Login successful', 'user_id': str(user.get('_id')), 'email': user.get('email')}, 200


@auth_ns.route('/forgot-password')
class ForgotPasswordResource(Resource):
    @auth_ns.expect(forgot_model)
    def post(self):
        data = request.json or {}
        email = data.get('email')
        if not email:
            return {'error': 'email is required'}, 400
        password = get_password_for_email(email)
        if password is None:
            return {'error': 'Email not found'}, 404
        # As per requirement, return plaintext password
        return {'email': email, 'password': password}, 200


@auth_ns.route('/previous-results')
class PreviousResultsResource(Resource):
    @auth_ns.doc(params={'user_id': 'The user id to fetch results for'}, description='Get previous results for the logged-in user')
    def get(self):
        user_id = request.args.get('user_id') or request.headers.get('X-User-Id')
        if not user_id:
            return {'error': 'user_id is required'}, 400
        results = get_results_for_user(user_id)
        # Convert ObjectIds to strings
        def transform(doc):
            doc = dict(doc)
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
            return doc
        payload = [transform(r) for r in results]
        return {'results': payload}, 200
