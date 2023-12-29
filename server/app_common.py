import requests
import json
import tiktoken
from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, session, stream_with_context, Response, render_template
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, jwt_required
from llm.openai import OpenAIConfig
from flask_cors import CORS
from models.basic_models import *
from models.common import db
from api.user import user_blueprint
from corp.corp import corp_blueprint
from admin import admin
from collections import defaultdict
from threading import Lock

# Initialize a lock and a defaultdict for the cache
cache_lock = Lock()
response_tokens_cache = defaultdict(int)

def create_app(config_name):
    app = Flask(__name__)
    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(user_blueprint, url_prefix='/api/users')
    app.register_blueprint(corp_blueprint, url_prefix='/corp')

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

    ######
    # Routes

    # Register Blueprints or define routes here
    # Define the login endpoint
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')
        elif request.method == 'POST':
            data = request.get_json()
            print(data)
            username = data.get('username')
            password = data.get('password')

            user = User.query.filter(User.username==username).first()
            print(f"Login: user.id: {user.id}")
            if user and user.check_password(password):
                # Create a new token with the user's ID inside
                access_token = create_access_token(identity=user.id)
                return jsonify(access_token=access_token, user_id=user.id), 200

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

        def num_tokens_from_string(string: str, encoding_name: str="cl100k_base") -> int:
            """Returns the number of tokens in a text string."""
            encoding = tiktoken.get_encoding(encoding_name)
            num_tokens = len(encoding.encode(string))
            return num_tokens

        # Calculate prompt tokens
        prompt_tokens = sum(num_tokens_from_string(message['content']) for message in incoming_data['messages'] if message['role'] == 'system' or message['role'] == 'user')
        # Clear cache and write to db
        response_tokens = response_tokens_cache.get(user_id, 0)
        with cache_lock:
            response_tokens_cache[user_id] = 0
        # Update user data here since streaming is done
        total_tokens = prompt_tokens + response_tokens
        user.tokens_used += total_tokens

        print(f"Total tokens: {total_tokens}, prompt tokens: {prompt_tokens}, cache response tokens: {response_tokens}")

        # Calculate the balance used
        model_ratio = OpenAIConfig.get_model_cost_ratios()[incoming_data['model']]
        balance_used = total_tokens * model_ratio

        # Deduct the balance used from the user's balance
        user.balance -= balance_used

        print(f"Balance used: {balance_used}")

        # Commit the changes to the database
        common.db.session.commit()
        
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
                    full_content = ''
                    for chunk in r.iter_content(chunk_size=None):  # Set chunk size as None to get data as it arrives
                        if chunk:  # filter out keep-alive new chunks
                            chunk_data = chunk.decode('utf-8')
                            print(f"- {chunk.decode('utf-8')}")  # Optional: for debugging purposes
                            # Count the occurrences of "data: " and update the cache
                            num_data_prefixes = chunk_data.count("data: ")
                            tokens_to_add = num_data_prefixes * 2
                            # Update the cache in a thread-safe manner
                            with cache_lock:
                                response_tokens_cache[user_id] += tokens_to_add
                            yield chunk.decode('utf-8')
                            print(f"response_tokens_cache: {response_tokens_cache}")

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
                except json.decoder.JSONDecodeError as json_err:
                    error_message = f'Json error occurred: {json_err}'
                    yield f'Error: {error_message}'  # You may want to handle this more gracefully

        return Response(stream_with_context(generate()), content_type='text/event-stream')

    ######
    # Admin
    admin.admin.init_app(app)
    admin.admin.add_view(admin.AdminModelView(User, db.session, endpoint='admin_user'))

    return app
