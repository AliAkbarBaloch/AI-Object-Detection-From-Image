import os
from datetime import datetime, timezone
from pymongo import MongoClient
from bson.objectid import ObjectId

MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://aiengineeringlab:aiengineeringlab61@cluster0.xhuygpv.mongodb.net/')
DB_NAME = os.getenv('DB_NAME', 'object_counter')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'results')

if not os.environ.get("CI") == "true":
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    results_collection = db[COLLECTION_NAME]
    users_collection = db.get_collection('users')
else:
    client = None
    db = None
    results_collection = None
    users_collection = None


def save_result(image_path, item_type, model_count, user_correction=None, user_id: str | None = None):
    if results_collection is None:
        return "ci-dummy-id"
    result = {
        'timestamp': datetime.now(timezone.utc),
        'image_path': image_path,
        'item_type': item_type,
        'model_count': model_count,
        'user_id': user_id,
        'user_correction': user_correction
    }
   # return results_collection.insert_one(result).inserted_id
    inserted_id = results_collection.insert_one(result).inserted_id
    try:
        results_collection.update_one({'_id': inserted_id}, {'$set': {'result_id': str(inserted_id)}})
    except Exception:
        # Best-effort; insertion already succeeded
        pass
    return inserted_id

def update_correction(result_id, correct_count):
    if results_collection is None:
        return None
    return results_collection.update_one(
        {'_id': ObjectId(result_id)},
        {'$set': {'user_correction': correct_count}}
    )

def get_result(result_id):
    if results_collection is None:
        return None
    return results_collection.find_one({'_id': ObjectId(result_id)})


# ---------------------
# User management utils
# ---------------------

def get_user_by_email(email: str):
    if users_collection is None:
        return None
    return users_collection.find_one({'email': email})


def create_user(email: str, password: str):
    """
    Creates a user document with email and password stored in plaintext (per requirement).
    Returns inserted ObjectId.
    """
    if users_collection is None:
        # Return a dummy id in CI to avoid DB dependency
        return "ci-user-id"
    existing = users_collection.find_one({'email': email})
    if existing:
        return None
    doc = {
        'email': email,
        'password': password,  # plaintext as requested
        'created_at': datetime.now(timezone.utc),
    }
    return users_collection.insert_one(doc).inserted_id


def verify_user(email: str, password: str):
    if users_collection is None:
        return None
    user = users_collection.find_one({'email': email, 'password': password})
    return user


def get_password_for_email(email: str):
    if users_collection is None:
        return None
    user = users_collection.find_one({'email': email})
    if not user:
        return None
    return user.get('password')


# def get_results_for_user(user_id: str, limit: int = 50):
#     if results_collection is None:
#         return []
#     cursor = results_collection.find({'item_type': "cat"}).sort('timestamp', -1).limit(limit)
#     return list(cursor)


def get_results_for_user(user_id: str, limit: int = 50):
    user_id = user_id.strip().strip('"').strip("'")
    if results_collection is None:
        return []
    print("user_id in db:", user_id)
    cursor = results_collection.find({'user_id': user_id}).sort('timestamp', -1).limit(limit)
    results = []

    for doc in cursor:
        doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
        if 'timestamp' in doc and doc['timestamp']:
            doc['timestamp'] = doc['timestamp'].isoformat()  # Convert datetime to ISO string
        results.append(doc)
    print("results:", results)
    return results

