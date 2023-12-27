import requests
import json
from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, session, stream_with_context, Response
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, jwt_required
from llm.openai import OpenAIConfig
from flask_cors import CORS
from models.basic_models import *
from models.common import db
from api.user import user_blueprint

def create_app(config_name):
    app = Flask(__name__)
    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(user_blueprint, url_prefix='/api/users')

    # Configure the app (e.g., from a config object or class)
    if config_name == 'development':
        app.config.from_object('config.DevelopmentConfig')
    elif config_name == 'testing':
        app.config.from_object('config.TestingConfig')
    elif config_name == 'production':
        app.config.from_object('config.ProductionConfig')

    # Initialize extensions
    db.init_app(app)
    CORS(app)  # You can also initialize CORS here if you prefer

    # Register Blueprints or define routes here
    # Define the login endpoint
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        print(f"Login: user.id: {user.id}")
        if user and user.check_password(password):
            # Create a new token with the user's ID inside
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token), 200

        return jsonify({"message": "Invalid credentials"}), 401

    @app.route('/v1/chat/completions', methods=['POST'])
    @jwt_required()
    def chat_completions():
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"message": "Unauthorized"}), 401
        
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"message": "User not found"}), 404

        # Check if the user has enough balance
        if user.balance <= 0:
            return jsonify({"message": "Insufficient balance"}), 402

        url, api_key = OpenAIConfig.get_credentials()
        incoming_data = request.json
        
        # Set the correct headers based on the successful request example
        headers = {
            'Accept': 'text/event-stream',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        print(f"relay data: {incoming_data}")
        print(f"header: {headers}")

        def generate():
            with requests.post(f'{url}/chat/completions', json=incoming_data, headers=headers, stream=True) as r:
                try:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=None):  # Set chunk size as None to get data as it arrives
                        if chunk:  # filter out keep-alive new chunks
                            print(chunk.decode('utf-8'))  # Optional: for debugging purposes
                            yield chunk.decode('utf-8')
                except requests.exceptions.HTTPError as http_err:
                    # Prints the HTTP status code and text if an HTTP error occurs
                    error_message = f'HTTP error occurred: {http_err} - Status Code: {r.status_code} - Response: {r.text}'
                    print(error_message)  # Optional: for debugging purposes
                    yield f'Error: {error_message}'  # You may want to handle this more gracefully
                except requests.exceptions.RequestException as req_err:
                    # Prints the request exception message if a different RequestException occurs
                    error_message = f'Request error occurred: {req_err}'
                    print(error_message)  # Optional: for debugging purposes
                    yield f'Error: {error_message}'  # You may want to handle this more gracefully

        return Response(stream_with_context(generate()), content_type='text/event-stream')

    return app
