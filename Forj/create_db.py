import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Flask app and models
try:
    from web.app import app, db, User, Dataset
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)

def init_db():
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Create a test user if it doesn't exist
        if not User.query.filter_by(email='test@example.com').first():
            user = User(
                name='Test User',
                email='test@example.com',
                password=generate_password_hash('password', method='pbkdf2:sha256')
            )
            db.session.add(user)
            db.session.commit()
            print("Created test user with email: test@example.com and password: password")
        
        # Create a test dataset if none exist
        if not Dataset.query.first():
            user = User.query.filter_by(email='test@example.com').first()
            if user:
                dataset = Dataset(
                    name='Sample Dataset',
                    description='A sample dataset for testing',
                    columns='[{"name": "id", "type": "integer"}, {"name": "name", "type": "string"}]',
                    row_count=10,
                    status='pending',
                    progress=0.0,
                    user_id=user.id
                )
                db.session.add(dataset)
                db.session.commit()
                print("Created sample dataset")
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    # Ensure the instance directory exists
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # Ensure the datasets directory exists
    datasets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets')
    os.makedirs(datasets_path, exist_ok=True)
    
    init_db()
