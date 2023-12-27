from flask import request, jsonify, session
from app_common import create_app
from models.basic_models import User, Corp
from models.common import db

# Create an instance of the Flask application
app = create_app('development')

# Function to initialize app-related tasks
def init_app():
    with app.app_context():
        # Create database tables
        db.create_all()

        # Create a new user
        new_user = User(username='testuser', email='a@a.com', balance=1000)
        new_user.set_password('testpassword')


        # Create a corporation
        new_corp = Corp(name='TestCorp', balance=10000)
        db.session.add(new_corp)
        db.session.commit()

        # Create a corp admin user
        corp_admin = User(
            username='corpadmin',
            email='admin@corp.com',
            balance=0,
            is_admin=True,
            corp_id=new_corp.id  # Associate the admin with the corporation
        )
        corp_admin.set_password('adminpassword')
        db.session.add(corp_admin)

        # Create a list of test users associated with the corporation
        test_users = [
            User(username='testuser1', email='user1@corp.com', balance=1000, corp_id=new_corp.id),
            User(username='testuser2', email='user2@corp.com', balance=1500, corp_id=new_corp.id),
            User(username='testuser3', email='user3@corp.com', balance=2000, corp_id=new_corp.id),
        ]

        # Set passwords for test users
        for user in test_users:
            user.set_password('testpassword')
            db.session.add(user)

        # Add the user to the session and commit to the database
        db.session.add(new_user)
        db.session.commit()

# Run the app
if __name__ == '__main__':
    # init_app()  # Initialize app-related tasks before running the app
    with app.app_context():
        users = User.query.all()
        for u in users:
            print(u.username)
    app.run(debug=True, host='0.0.0.0', port=5005)
