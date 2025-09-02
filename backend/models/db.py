import os
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://aiengineeringlab:aiengineeringlab61@cluster0.xhuygpv.mongodb.net/')
DB_NAME = os.getenv('DB_NAME', 'object_counter')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'results')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
results_collection = db[COLLECTION_NAME]

def save_result(image_path, item_type, model_count, user_correction=None):
    result = {
        'timestamp': datetime.utcnow(),
        'image_path': image_path,
        'item_type': item_type,
        'model_count': model_count,
        'user_correction': user_correction
    }
    return results_collection.insert_one(result).inserted_id

def update_correction(result_id, correct_count):
    return results_collection.update_one(
        {'_id': ObjectId(result_id)},
        {'$set': {'user_correction': correct_count}}
    )

def get_result(result_id):
    return results_collection.find_one({'_id': ObjectId(result_id)})
