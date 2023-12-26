import unittest
from unittest.mock import patch
import json
from app_common import create_app, db  # Import from app_common.py
from models.basic_models import *
from flask_jwt_extended import create_access_token, decode_token

class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create the database and the database table
        db.create_all()

        # Insert user data
        user = User(username='testuser', email='a@a.com', balance=100000)
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()

        self.test_user = user

    def tearDown(self):
        # Clean up the database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login(self):
        # Send a POST request to the login endpoint with the username and password
        response = self.client.post('/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')

        print(response.data)
        print(f"test: user.id: {self.test_user.id}")

        # Check if the login was successful and the response contains a token
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', data)  # Check if 'access_token' is in the response

        # Decode the token
        decoded_token = decode_token(data['access_token'])
        self.assertEqual(str(decoded_token['sub']), str(self.test_user.id))  # Check if the user ID in the token is correct

    def test_balance_transfer(self):
        # Create a corporation
        corp = Corp(name='Test Corp', balance=1000.00)
        db.session.add(corp)
        db.session.commit()

        # Insert two users: one admin and one regular user
        admin_user = User(username='admin', email='admin@admin.com', corp_id=corp.id, is_admin=True, balance=500.00)
        admin_user.set_password('adminpassword')
        db.session.add(admin_user)

        regular_user = User(username='regular', email='regular@user.com', corp_id=corp.id, balance=100.00)
        regular_user.set_password('regularpassword')
        db.session.add(regular_user)

        db.session.commit()

        # Perform balance transfer from Corp to regular user
        transfer_amount = 50.00
        admin_user = User.query.filter_by(username='admin').first()
        corp = Corp.query.get(admin_user.corp_id)
        initial_corp_balance = corp.balance
        initial_regular_user_balance = regular_user.balance  # Store initial balance for debugging

        print(f"Before transfer: Corp balance = {initial_corp_balance}, Regular User balance = {initial_regular_user_balance}")

        success = admin_user.transfer_balance(recipient=regular_user.id, amount=transfer_amount)

        # Fetch updated records from the database
        corp_updated = Corp.query.get(corp.id)
        regular_user_updated = User.query.get(regular_user.id)

        print(f"After transfer: Corp balance = {corp_updated.balance}, Regular User balance = {regular_user_updated.balance}")

        # Check if the transfer was successful
        self.assertTrue(success)
        # Check if the Corp's balance has been decremented
        self.assertEqual(corp_updated.balance, initial_corp_balance - transfer_amount)
        # Check if the regular user's balance has been incremented
        self.assertEqual(regular_user_updated.balance, initial_regular_user_balance + transfer_amount)

    def login(self):
        return self.client.post('/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')

    def test_chat_completions(self):
        # Perform login to get the access token
        login_response = self.login()
        login_data = json.loads(login_response.data.decode())
        access_token = login_data['access_token']

        # Mock the OpenAI API response
        mock_response = {
            "choices": [
                {
                    "finish_reason": "stop",
                    "index": 0,
                    "logprobs": None,
                    "message": {
                        "content": "This is a test!",
                        "role": "assistant"
                    }
                }
            ],
            "created": 1703517775,
            "id": "chatcmpl-8Zh55rHrMQsvPjKMSHN7zrQw7k6ft",
            "model": "gpt-3.5-turbo-0613",
            "object": "chat.completion",
            "system_fingerprint": None,
            "usage": {
                "completion_tokens": 5,
                "prompt_tokens": 13,
                "total_tokens": 18
            }
        }

        with patch('requests.post') as mock_post:
            # Configure the mock to return a response with our mocked OpenAI API response
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response

            # Prepare the headers and data for the POST request
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'  # Add the JWT token to the headers
            }

            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Say this is a test!"}],
                "temperature": 0.7
            }

            # Send a POST request to the chat completions endpoint
            response = self.client.post('/v1/chat/completions', data=json.dumps(data), headers=headers)

            # Check that the response is successful
            # self.assertEqual(response.status_code, 200)

            # Verify the response data
            response_data = json.loads(response.data.decode())
            self.assertIn('id', response_data)
            self.assertIn('choices', response_data)
            self.assertEqual(response_data['choices'][0]['message']['content'], 'This is a test!')


if __name__ == '__main__':
    unittest.main()
