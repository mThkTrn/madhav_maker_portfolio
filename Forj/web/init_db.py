from .app import app, db, User

def init_db():
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Create a test user if it doesn't exist
        if not User.query.filter_by(email='test@example.com').first():
            from werkzeug.security import generate_password_hash
            user = User(
                name='Test User',
                email='test@example.com',
                password=generate_password_hash('password', method='pbkdf2:sha256')
            )
            db.session.add(user)
            db.session.commit()
            print("Created test user with email: test@example.com and password: password")
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
