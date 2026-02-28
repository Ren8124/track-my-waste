from bson.objectid import ObjectId
from datetime import datetime

class Schedule:
    def __init__(self, db):
        self.collection = db.schedules
    
    def create(self, area, day_of_week, time, worker_id=None):
        schedule_data = {
            'area': area,
            'day_of_week': day_of_week,  # 0=Monday, 6=Sunday
            'time': time,
            'worker_id': ObjectId(worker_id) if worker_id else None,
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(schedule_data)
        return result.inserted_id
    
    def find_by_area(self, area):
        return list(self.collection.find({'area': area, 'is_active': True}).sort('day_of_week', 1))
    
    def get_all(self):
        return list(self.collection.find({'is_active': True}).sort([('area', 1), ('day_of_week', 1)]))
    
    def update(self, schedule_id, update_data):
        return self.collection.update_one(
            {'_id': ObjectId(schedule_id)},
            {'$set': update_data}
        )
    
    def delete(self, schedule_id):
        return self.collection.delete_one({'_id': ObjectId(schedule_id)})
