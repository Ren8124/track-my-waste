from pymongo import MongoClient
import bcrypt
from datetime import datetime, timedelta
import random

# MongoDB Connection
client = MongoClient('mongodb://localhost:27017/')
db = client['trackmywaste']

# Clear existing data
print("Clearing existing data...")
db.users.delete_many({})
db.complaints.delete_many({})
db.workers.delete_many({})
db.schedules.delete_many({})
db.tips.delete_many({})

# Create admin user
print("Creating admin user...")
admin_password = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt())
admin_id = db.users.insert_one({
    'username': 'admin',
    'email': 'admin@trackmywaste.com',
    'password_hash': admin_password,
    'role': 'admin',
    'phone': '1234567890',
    'area': 'Central',
    'created_at': datetime.utcnow(),
    'updated_at': datetime.utcnow()
}).inserted_id

# Create test resident users
print("Creating resident users...")
resident_password = bcrypt.hashpw('resident123'.encode('utf-8'), bcrypt.gensalt())
areas = ['North Zone', 'South Zone', 'East Zone', 'West Zone', 'Central']

resident_ids = []
for i in range(5):
    resident_id = db.users.insert_one({
        'username': f'resident{i+1}',
        'email': f'resident{i+1}@test.com',
        'password_hash': resident_password,
        'role': 'resident',
        'phone': f'98765432{i}0',
        'area': areas[i],
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }).inserted_id
    resident_ids.append(resident_id)

# Create test worker users
print("Creating worker users...")
worker_password = bcrypt.hashpw('worker123'.encode('utf-8'), bcrypt.gensalt())

worker_ids = []
for i in range(3):
    worker_user_id = db.users.insert_one({
        'username': f'worker{i+1}',
        'email': f'worker{i+1}@test.com',
        'password_hash': worker_password,
        'role': 'worker',
        'phone': f'87654321{i}0',
        'area': areas[i],
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }).inserted_id
    
    worker_id = db.workers.insert_one({
        'user_id': worker_user_id,
        'name': f'Worker {i+1}',
        'phone': f'87654321{i}0',
        'areas_assigned': [areas[i], areas[i+1] if i+1 < len(areas) else areas[0]],
        'vehicle_info': f'Truck #{i+1}',
        'is_active': True,
        'created_at': datetime.utcnow()
    }).inserted_id
    worker_ids.append(worker_id)

# Create sample complaints
print("Creating sample complaints...")
priorities = ['low', 'medium', 'high']
statuses = ['pending', 'in_progress', 'completed']
descriptions = [
    'Garbage not collected for 3 days',
    'Overflowing bins near park',
    'Broken waste bin needs replacement',
    'Missed pickup on scheduled day',
    'Large items need special collection'
]

for i in range(15):
    days_ago = random.randint(0, 30)
    created_date = datetime.utcnow() - timedelta(days=days_ago)
    
    status = random.choice(statuses)
    assigned_worker = random.choice(worker_ids) if status != 'pending' else None
    
    db.complaints.insert_one({
        'user_id': random.choice(resident_ids),
        'description': random.choice(descriptions),
        'area': random.choice(areas),
        'priority': random.choice(priorities),
        'status': status,
        'latitude': 19.0760 + random.uniform(-0.1, 0.1),
        'longitude': 72.8777 + random.uniform(-0.1, 0.1),
        'assigned_worker_id': assigned_worker,
        'created_at': created_date,
        'updated_at': created_date,
        'resolved_at': created_date + timedelta(days=random.randint(1, 5)) if status == 'completed' else None
    })

# Create schedules
print("Creating collection schedules...")
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
times = ['08:00 AM', '09:00 AM', '10:00 AM', '02:00 PM', '03:00 PM']

for i, area in enumerate(areas):
    for j in range(2):
        db.schedules.insert_one({
            'area': area,
            'day_of_week': (i + j) % 7,
            'time': times[i % len(times)],
            'worker_id': worker_ids[i % len(worker_ids)],
            'is_active': True,
            'created_at': datetime.utcnow()
        })

# Create eco-friendly tips
print("Creating eco-friendly tips...")
tips_data = [
    {
        'title': 'Reduce Plastic Usage',
        'content': 'Use reusable bags and containers instead of single-use plastics. This helps reduce the amount of waste going to landfills.',
        'category': 'reduce'
    },
    {
        'title': 'Compost Organic Waste',
        'content': 'Start composting kitchen scraps and yard waste. This reduces landfill waste and creates nutrient-rich soil for gardening.',
        'category': 'compost'
    },
    {
        'title': 'Separate Your Waste',
        'content': 'Sort your waste into recyclables, compostables, and general waste. This makes recycling more efficient and effective.',
        'category': 'recycle'
    },
    {
        'title': 'Donate or Repair',
        'content': 'Before throwing away items, consider if they can be donated, sold, or repaired. One person\'s waste is another\'s treasure!',
        'category': 'reuse'
    },
    {
        'title': 'Use Rechargeable Batteries',
        'content': 'Switch to rechargeable batteries to reduce the number of disposable batteries ending up in landfills.',
        'category': 'reduce'
    }
]

for tip in tips_data:
    db.tips.insert_one({
        'title': tip['title'],
        'content': tip['content'],
        'category': tip['category'],
        'is_active': True,
        'created_at': datetime.utcnow()
    })

print("\n" + "="*50)
print("Database seeded successfully!")
print("="*50)
print("\nTest Accounts:")
print("-" * 50)
print("Admin:")
print("  Username: admin")
print("  Password: admin")
print("\nResident:")
print("  Username: resident1")
print("  Password: resident123")
print("\nWorker:")
print("  Username: worker1")
print("  Password: worker123")
print("="*50)

client.close()
