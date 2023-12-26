from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin, UserManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myapp.db'  # Use SQLite for simplicity
app.config['USER_ENABLE_EMAIL'] = True  # Enable email authentication
app.config['USER_REQUIRE_RETYPE_PASSWORD'] = True  # Require the user to retype the password at registration
app.config['SECRET_KEY'] = 'thisisasecretkey'  # Replace with a real secret key
app.config['CSRF_ENABLED'] = True  # Enable CSRF protection

app.config['USER_EMAIL_SENDER_EMAIL'] = 'your-email@example.com'

# Initialize SQLAlchemy
db = SQLAlchemy(app)