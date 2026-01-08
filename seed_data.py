import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import bcrypt
import uuid
from datetime import datetime, timezone

# Load environment
ROOT_DIR = Path(__file__).parent.parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def seed_data():
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🌱 Seeding database...")
    
    # Check if admin exists
    existing_admin = await db.users.find_one({'email': 'admin@cineplex.com'})
    if existing_admin:
        print("✅ Admin user already exists")
    else:
        # Create admin user
        admin = {
            'id': str(uuid.uuid4()),
            'email': 'admin@cineplex.com',
            'password': hash_password('admin123'),
            'name': 'Admin User',
            'role': 'admin',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(admin)
        print("✅ Admin user created (email: admin@cineplex.com, password: admin123)")
    
    # Create sample user
    existing_user = await db.users.find_one({'email': 'user@example.com'})
    if not existing_user:
        user = {
            'id': str(uuid.uuid4()),
            'email': 'user@example.com',
            'password': hash_password('user123'),
            'name': 'John Doe',
            'role': 'user',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user)
        print("✅ Sample user created (email: user@example.com, password: user123)")
    
    # Create sample screens
    screen_count = await db.screens.count_documents({})
    if screen_count == 0:
        screens = [
            {
                'id': str(uuid.uuid4()),
                'name': 'Screen 1',
                'rows': 8,
                'columns': 10,
                'vip_seats': ['A1', 'A2', 'A9', 'A10'],
                'total_seats': 80,
                'created_at': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Screen 2 - IMAX',
                'rows': 10,
                'columns': 12,
                'vip_seats': ['A1', 'A2', 'A11', 'A12', 'B1', 'B2', 'B11', 'B12'],
                'total_seats': 120,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
        ]
        await db.screens.insert_many(screens)
        print("✅ Sample screens created")
    
    # Create sample movies
    movie_count = await db.movies.count_documents({})
    if movie_count == 0:
        movies = [
            {
                'id': str(uuid.uuid4()),
                'title': 'The Matrix Resurrections',
                'description': 'Return to a world of two realities: one, everyday life; the other, what lies behind it.',
                'poster_url': 'https://images.unsplash.com/photo-1762356121454-877acbd554bb?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwxfHxjaW5lbWF0aWMlMjBtb3ZpZSUyMHBvc3RlciUyMGFjdGlvbnxlbnwwfHx8fDE3Njc3NzQxNTF8MA&ixlib=rb-4.1.0&q=85',
                'duration': 148,
                'genre': 'Action/Sci-Fi',
                'language': 'English',
                'rating': 'PG-13',
                'now_showing': True,
                'created_at': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Inception',
                'description': 'A thief who steals corporate secrets through dream-sharing technology.',
                'poster_url': 'https://images.unsplash.com/photo-1745564371387-7707cc41e958?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHw0fHxjaW5lbWF0aWMlMjBtb3ZpZSUyMHBvc3RlciUyMGFjdGlvbnxlbnwwfHx8fDE3Njc3NzQxNTF8MA&ixlib=rb-4.1.0&q=85',
                'duration': 148,
                'genre': 'Thriller/Sci-Fi',
                'language': 'English',
                'rating': 'PG-13',
                'now_showing': True,
                'created_at': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Interstellar',
                'description': 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity survival.',
                'poster_url': 'https://images.unsplash.com/photo-1739891251370-05b62a54697b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwzfHxjaW5lbWF0aWMlMjBtb3ZpZSUyMHBvc3RlciUyMGFjdGlvbnxlbnwwfHx8fDE3Njc3NzQxNTF8MA&ixlib=rb-4.1.0&q=85',
                'duration': 169,
                'genre': 'Adventure/Sci-Fi',
                'language': 'English',
                'rating': 'PG-13',
                'now_showing': True,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
        ]
        await db.movies.insert_many(movies)
        print("✅ Sample movies created")
    
    print("✅ Database seeding completed!")
    client.close()

if __name__ == '__main__':
    asyncio.run(seed_data())
