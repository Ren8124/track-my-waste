from pymongo import ASCENDING
from bson.objectid import ObjectId
import bcrypt
from datetime import datetime

class User:
    def __init__(self, db):
        self.collection = db.users
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        try:
            self.collection.create_index([('username', ASCENDING)], unique=True)
            self.collection.create_index([('email', ASCENDING)], unique=True)
        except Exception:
            pass
    
    def create(self, username, email, password, role='resident', phone='', area=''):
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'phone': phone,
            'area': area,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(user_data)
        return result.inserted_id
    
    def find_by_username(self, username):
        return self.collection.find_one({'username': username})
    
    def find_by_id(self, user_id):
        return self.collection.find_one({'_id': ObjectId(user_id)})
    
    def verify_password(self, username, password):
        user = self.find_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            return user
        return None
    
    def update(self, user_id, update_data):
        update_data['updated_at'] = datetime.utcnow()
        return self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
    
    def delete(self, user_id):
        return self.collection.delete_one({'_id': ObjectId(user_id)})
    
    def get_all(self, role=None):
        query = {'role': role} if role else {}
        return list(self.collection.find(query))
