from bson.objectid import ObjectId
from datetime import datetime

class Tip:
    def __init__(self, db):
        self.collection = db.tips
    
    def create(self, title, content, category='general'):
        tip_data = {
            'title': title,
            'content': content,
            'category': category,
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(tip_data)
        return result.inserted_id
    
    def get_all(self, active_only=True):
        query = {'is_active': True} if active_only else {}
        return list(self.collection.find(query).sort('created_at', -1))
    
    def find_by_id(self, tip_id):
        return self.collection.find_one({'_id': ObjectId(tip_id)})
    
    def update(self, tip_id, update_data):
        return self.collection.update_one(
            {'_id': ObjectId(tip_id)},
            {'$set': update_data}
        )
    
    def delete(self, tip_id):
        return self.collection.delete_one({'_id': ObjectId(tip_id)})
