from bson.objectid import ObjectId
from datetime import datetime

class Worker:
    def __init__(self, db):
        self.collection = db.workers
    
    def create(self, user_id, name, phone, areas_assigned, vehicle_info=''):
        worker_data = {
            'user_id': ObjectId(user_id),
            'name': name,
            'phone': phone,
            'areas_assigned': areas_assigned,  # List of areas
            'vehicle_info': vehicle_info,
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(worker_data)
        return result.inserted_id
    
    def find_by_id(self, worker_id):
        return self.collection.find_one({'_id': ObjectId(worker_id)})
    
    def find_by_user_id(self, user_id):
        return self.collection.find_one({'user_id': ObjectId(user_id)})
    
    def get_all(self, active_only=False):
        query = {'is_active': True} if active_only else {}
        return list(self.collection.find(query))
    
    def update(self, worker_id, update_data):
        return self.collection.update_one(
            {'_id': ObjectId(worker_id)},
            {'$set': update_data}
        )
    
    def delete(self, worker_id):
        return self.collection.delete_one({'_id': ObjectId(worker_id)})
