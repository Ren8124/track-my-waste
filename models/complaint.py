from bson.objectid import ObjectId
from datetime import datetime

class Complaint:
    def __init__(self, db):
        self.collection = db.complaints
    
    def create(self, user_id, description, area, priority='medium', 
               latitude=None, longitude=None):
        complaint_data = {
            'user_id': ObjectId(user_id),
            'description': description,
            'area': area,
            'priority': priority,
            'status': 'pending',
            'latitude': latitude,
            'longitude': longitude,
            'assigned_worker_id': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'resolved_at': None
        }
        
        result = self.collection.insert_one(complaint_data)
        return result.inserted_id
    
    def find_by_id(self, complaint_id):
        return self.collection.find_one({'_id': ObjectId(complaint_id)})
    
    def find_by_user(self, user_id):
        return list(self.collection.find({'user_id': ObjectId(user_id)}).sort('created_at', -1))
    
    def find_by_worker(self, worker_id):
        return list(self.collection.find({'assigned_worker_id': ObjectId(worker_id)}).sort('created_at', -1))
    
    def update(self, complaint_id, update_data):
        update_data['updated_at'] = datetime.utcnow()
        if update_data.get('status') == 'completed':
            update_data['resolved_at'] = datetime.utcnow()
        
        return self.collection.update_one(
            {'_id': ObjectId(complaint_id)},
            {'$set': update_data}
        )
    
    def delete(self, complaint_id):
        return self.collection.delete_one({'_id': ObjectId(complaint_id)})
    
    def get_all(self, filters=None):
        query = filters if filters else {}
        return list(self.collection.find(query).sort('created_at', -1))
    
    def get_analytics(self):
        pipeline = [
            {
                '$group': {
                    '_id': '$area',
                    'count': {'$sum': 1},
                    'pending': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'pending']}, 1, 0]}
                    },
                    'in_progress': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'in_progress']}, 1, 0]}
                    },
                    'completed': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'completed']}, 1, 0]}
                    }
                }
            }
        ]
        return list(self.collection.aggregate(pipeline))
