from flask import request, jsonify, session
from app_common import create_app
from models.basic_models import User
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

        # Add the user to the session and commit to the database
        db.session.add(new_user)
        db.session.commit()

# Run the app
if __name__ == '__main__':
    # init_app()  # Initialize app-related tasks before running the app
    app.run(debug=True, host='0.0.0.0', port=5005)
