import os
from app import create_app, db
from app.models import User, Candidate
from werkzeug.security import generate_password_hash

app = create_app()

# Command to initialize database and create admin user
@app.cli.command("init-db")
def init_db():
    """Initialize the database and create admin user"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create a default admin user if none exists
        if User.query.filter_by(username='admin').first() is None:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')  # Default password - should be changed
            db.session.add(admin)
            db.session.commit()
            print('Created default admin user: admin/admin123')
            print('Please change the default password after first login!')
        
        print('Database initialized successfully.')

# Command to create a new user
@app.cli.command("create-user")
def create_user():
    """Create a new user interactively"""
    import getpass
    
    with app.app_context():
        username = input("Enter username: ")
        email = input("Enter email: ")
        password = getpass.getpass("Enter password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        
        if password != confirm_password:
            print("Passwords do not match.")
            return
        
        if User.query.filter_by(username=username).first():
            print(f"User {username} already exists.")
            return
        
        if User.query.filter_by(email=email).first():
            print(f"Email {email} already in use.")
            return
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"User {username} created successfully.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
