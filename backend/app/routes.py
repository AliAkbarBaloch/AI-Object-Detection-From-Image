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



# Single image parser
count_parser = count_ns.parser()
count_parser.add_argument('item_type', type=str, required=True, help='Type of item to count')
count_parser.add_argument('image', location='files', type=FileStorage, required=True, help='Image file')

# Batch image parser
batch_count_parser = count_ns.parser()
batch_count_parser.add_argument('item_type', type=str, required=True, help='Type of item to count')
batch_count_parser.add_argument('images', location='files', type=FileStorage, required=True, action='append', help='Image files')
@count_ns.route('/batch_count')
class BatchCountResource(Resource):
    @count_ns.expect(batch_count_parser)
    @count_ns.doc(description="Upload multiple images and get object counts for each")
    def post(self):
        try:
            try:
                args = batch_count_parser.parse_args()
            except BadRequest as e:
                return {'error': 'Input payload validation failed', 'message': str(e)}, 400
            item_type = args.get('item_type')
            # For batch, getlist is needed
            image_files = request.files.getlist('images')
            user_id = request.form.get("user_id")
            if not item_type or not image_files:
                return {'error': 'Missing item_type or images'}, 400
            results = []
            for image_file in image_files:
                if not hasattr(image_file, 'filename') or not image_file.filename:
                    continue
                if not image_file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                    continue
                filename = secure_filename(image_file.filename)
                image_path_abs = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    image_file.save(image_path_abs)
                except Exception as e:
                    results.append({'filename': filename, 'error': f'Failed to save image: {str(e)}'})
                    continue
                try:
                    result = count_objects(image_path_abs, item_type)
                except Exception as e:
                    results.append({'filename': filename, 'error': f'Model error: {str(e)}'})
                    continue
                db_image_path = f"uploads/{filename}"
                seg_filename = result.get('segmentation_filename')
                seg_image_path = f"uploads/{seg_filename}" if seg_filename else None
                matched_segment_filenames = result.get('matched_segment_filenames') or []
                matched_segment_image_paths = [f"uploads/{fn}" for fn in matched_segment_filenames]
                matched_segments_meta = result.get('matched_segments') or []
                merged_matches_filename = result.get('matched_segments_merged_filename')
                merged_matches_path = f"uploads/{merged_matches_filename}" if merged_matches_filename else None
                try:
                    result_id = save_result(db_image_path, item_type, result['count'], "", user_id, segmentation_image_path=seg_image_path, matched_segment_image_paths=matched_segment_image_paths, matched_segments=matched_segments_meta, matched_segments_merged_path=merged_matches_path, count_confidence=result.get('count_confidence'))
                except Exception as e:
                    results.append({'filename': filename, 'error': f'Database error: {str(e)}'})
                    continue
                image_url = request.host_url.rstrip('/') + f"/uploads/{filename}"
                segmentation_url = request.host_url.rstrip('/') + f"/uploads/{seg_filename}" if seg_filename else None
                matched_segment_urls = [request.host_url.rstrip('/') + f"/{p}" for p in matched_segment_image_paths]
                matched_segments = [
                    {
                        'url': request.host_url.rstrip('/') + f"/uploads/{m.get('filename')}",
                        'label': m.get('label'),
                        'predicted_class': m.get('predicted_class'),
                        'label_conf': m.get('label_conf'),
                        'class_conf': m.get('class_conf'),
                        'path': f"uploads/{m.get('filename')}"
                    }
                    for m in matched_segments_meta
                ]
                merged_matches_url = request.host_url.rstrip('/') + f"/{merged_matches_path}" if merged_matches_path else None
                results.append({
                    'filename': filename,
                    'result_id': str(result_id),
                    'count': result['count'],
                    'count_confidence': result.get('count_confidence'),
                    'labels': result['labels'],
                    'segments': result['segments'],
                    'image_url': image_url,
                    'segmentation_url': segmentation_url,
                    'matched_segment_urls': matched_segment_urls,
                    'matched_segments': matched_segments,
                    'matched_segments_merged_url': merged_matches_url
                })
            return {'results': results}, 200
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'error': f'Unexpected error: {str(e)}'}, 500

correct_model = correct_ns.model('Correct', {
    'result_id': fields.String(required=True, description='ID of the result to correct'),
    'correct_count': fields.Integer(required=True, description='Corrected count'),
})

# UPLOAD_FOLDER = 'uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
from flask import Flask, send_from_directory
import os
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
            user_id = request.form.get("user_id")
            if not item_type:
                return {'error': 'Missing item_type'}, 400
            if not image_file:
                return {'error': 'No image uploaded'}, 400
            if not hasattr(image_file, 'filename') or not image_file.filename:
                return {'error': 'No image uploaded'}, 400
            if not image_file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                return {'error': 'Invalid file type'}, 400
            filename = secure_filename(image_file.filename)
            # Use absolute path for saving
            UPLOAD_FOLDER_ABS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
            os.makedirs(UPLOAD_FOLDER_ABS, exist_ok=True)
            image_path_abs = os.path.join(UPLOAD_FOLDER_ABS, filename)
            try:
                image_file.save(image_path_abs)
            except Exception as e:
                return {'error': f'Failed to save image: {str(e)}'}, 500
            try:
                result = count_objects(image_path_abs, item_type)
            except Exception as e:
                return {'error': f'Model error: {str(e)}'}, 500
            # Store relative path in DB
            db_image_path = f"uploads/{filename}"
            seg_filename = result.get('segmentation_filename')
            seg_image_path = f"uploads/{seg_filename}" if seg_filename else None
            matched_segment_filenames = result.get('matched_segment_filenames') or []
            matched_segment_image_paths = [f"uploads/{fn}" for fn in matched_segment_filenames]
            matched_segments_meta = result.get('matched_segments') or []
            merged_matches_filename = result.get('matched_segments_merged_filename')
            merged_matches_path = f"uploads/{merged_matches_filename}" if merged_matches_filename else None
            try:
                result_id = save_result(db_image_path, item_type, result['count'],"",user_id, segmentation_image_path=seg_image_path, matched_segment_image_paths=matched_segment_image_paths, matched_segments=matched_segments_meta, matched_segments_merged_path=merged_matches_path, count_confidence=result.get('count_confidence'))
            except Exception as e:
                return {'error': f'Database error: {str(e)}'}, 500
            # Best-effort: also persist a string 'result_id' field into the same document for convenient lookups
            try:
                if results_collection is not None:
                    results_collection.update_one({'_id': result_id}, {'$set': {'result_id': str(result_id)}})
            except Exception:
                # Don't fail the request if this auxiliary update fails
                pass
            image_url = request.host_url.rstrip('/') + f"/uploads/{filename}"
            segmentation_url = request.host_url.rstrip('/') + f"/uploads/{seg_filename}" if seg_filename else None
            matched_segment_urls = [request.host_url.rstrip('/') + f"/{p}" for p in matched_segment_image_paths]
            matched_segments = [
                {
                    'url': request.host_url.rstrip('/') + f"/uploads/{m.get('filename')}",
                    'label': m.get('label'),
                    'predicted_class': m.get('predicted_class'),
                    'label_conf': m.get('label_conf'),
                    'class_conf': m.get('class_conf'),
                    'path': f"uploads/{m.get('filename')}"
                }
                for m in matched_segments_meta
            ]
            merged_matches_url = request.host_url.rstrip('/') + f"/{merged_matches_path}" if merged_matches_path else None
            print("image_url:", image_url)
            return {
                'result_id': str(result_id),
                'count': result['count'],
                'count_confidence': result.get('count_confidence'),
                'labels': result['labels'],
                'segments': result['segments'],
                'image_url': image_url,
                'segmentation_url': segmentation_url,
                'matched_segment_urls': matched_segment_urls,
                'matched_segments': matched_segments,
                'matched_segments_merged_url': merged_matches_url
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
