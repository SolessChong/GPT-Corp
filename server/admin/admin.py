from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask_basicauth import BasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

basic_auth = BasicAuth()

class AdminModelView(ModelView):
    def is_accessible(self):
        # Use BasicAuth to protect the admin interface
        return basic_auth.authenticate()

    def inaccessible_callback(self, name, **kwargs):
        # Redirect to login page if the user is not authenticated
        return basic_auth.challenge()

# Initialize Flask-Admin
admin = Admin(template_mode='bootstrap3')