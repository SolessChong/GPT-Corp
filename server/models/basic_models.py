from flask_user import UserMixin, UserManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from models import common

# Define the User data-model.
class User(common.db.Model, UserMixin):
    id = common.db.Column(common.db.Integer, primary_key=True)

    # User authentication information
    username = common.db.Column(common.db.String(50), nullable=False, unique=True)
    password_hash = common.db.Column(common.db.String(255), nullable=False, server_default='')
    email = common.db.Column(common.db.String(255), nullable=False, unique=True)
    email_confirmed_at = common.db.Column(common.db.DateTime())

    # User information
    active = common.db.Column('is_active', common.db.Boolean(), nullable=False, server_default='0')

    # New fields for Corp association and admin flag
    corp_id = common.db.Column(common.db.Integer, nullable=True)  # Not enforced as a foreign key
    is_admin = common.db.Column(common.db.Boolean, default=False)

    # User balance and tokens used
    balance = common.db.Column(common.db.Float, nullable=False, default=0.0)
    tokens_used = common.db.Column(common.db.Integer, nullable=False, default=0)

    # Method to check the user's password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def transfer_balance(self, recipient, amount):
        # Check if the user is an admin
        if not self.is_admin:
            return False  # Or raise an exception

        # Get the corporation associated with the admin
        corp = Corp.query.get(self.corp_id)
        if not corp or corp.balance < amount:
            return False  # Or raise an exception (e.g., Corp not found or insufficient funds)

        # Check if the recipient exists and has the same corp_id
        recipient_user = User.query.filter_by(id=recipient, corp_id=self.corp_id).first()
        if not recipient_user:
            return False  # Or raise an exception

        # Perform the balance transfer
        corp.balance -= amount
        recipient_user.balance += amount
        common.db.session.commit()
        return True



class UsageRecord(common.db.Model):
    id = common.db.Column(common.db.Integer, primary_key=True)
    user_id = common.db.Column(common.db.Integer, index=True)
    model_name = common.db.Column(common.db.String(64))
    prompt_token = common.db.Column(common.db.Integer)
    reply_token = common.db.Column(common.db.Integer)
    balance = common.db.Column(common.db.Float)
    note = common.db.Column(common.db.String)


# Define the Corp data-model.
class Corp(common.db.Model):
    id = common.db.Column(common.db.Integer, primary_key=True)
    name = common.db.Column(common.db.String(128), nullable=False, unique=True)
    balance = common.db.Column(common.db.Float, nullable=False, default=0.0)
    logo = common.db.Column(common.db.String(255))  # Assuming a URL to the logo image

# Setup Flask-User
user_manager = UserManager(common.app, common.db, User)  # Initialize Flask-User
