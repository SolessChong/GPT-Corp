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

def create_app(config_name):
    app = Flask(__name__)
    jwt = JWTManager(app)

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

    # @app.route('/v1/chat/completions', methods=['POST'])
    # @jwt_required()
    # def chat_completions():
    #     user_id = get_jwt_identity()
    #     if not user_id:
    #         return jsonify({"message": "Unauthorized"}), 401
        
    #     user = User.query.get(user_id)
    #     if user is None:
    #         return jsonify({"message": "User not found"}), 404

    #     # Check if the user has enough balance
    #     if user.balance <= 0:
    #         return jsonify({"message": "Insufficient balance"}), 402

    #     url, api_key = OpenAIConfig.get_credentials()
    #     incoming_data = request.get_json()
    #     # print(f"relay data: {incoming_data}")
    #     headers = {
    #         'Content-Type': 'application/json',
    #         'Authorization': f'Bearer {api_key}'
    #     }

    #     def generate():
    #         try:
    #             with requests.post(f'{url}/chat/completions', json=incoming_data, headers=headers, stream=True) as r:
    #                 r.raise_for_status()
    #                 for chunk in r.iter_content(chunk_size=None):  # Use server's chunk size
    #                     if chunk:  # filter out keep-alive new chunks
    #                         # Here you would normally process the chunk if needed
    #                         yield f"data: {chunk.decode()}\n\n"
    #         except requests.exceptions.RequestException as e:
    #             yield f"data: {json.dumps({'error': str(e)})}\n\n"
    #             return

    #     return Response(stream_with_context(generate()), content_type='text/event-stream')

    
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
        incoming_data = request.get_json()
        print(f"relay data: {incoming_data}")
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        try:
            response = requests.post(f'{url}/chat/completions', json=incoming_data, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            abort(response.status_code, description=str(e))

        # Parse the response to find out how many tokens were used
        response_data = response.json()
        print(response_data)
        tokens_used = response_data['usage']['total_tokens']

        # Deduct tokens from the user's balance and add to their tokens_used
        user.balance -= tokens_used  # Ensure that balance cannot go negative in your User model logic
        user.tokens_used += tokens_used

        # Update the user's record in the database
        db.session.commit()

        return jsonify(response_data), response.status_code

    return app
