import os
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://aiengineeringlab:aiengineeringlab61@cluster0.xhuygpv.mongodb.net/')
DB_NAME = os.getenv('DB_NAME', 'object_counter')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'results')

if not os.environ.get("CI") == "true":
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    results_collection = db[COLLECTION_NAME]
else:
    client = None
    db = None
    results_collection = None


def save_result(image_path, item_type, model_count, user_correction=None):
    if results_collection is None:
        return "ci-dummy-id"
    result = {
        'timestamp': datetime.utcnow(),
        'image_path': image_path,
        'item_type': item_type,
        'model_count': model_count,
        'user_correction': user_correction
    }
    return results_collection.insert_one(result).inserted_id

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

