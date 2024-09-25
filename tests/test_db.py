import json
import os
import unittest
from models import db  # Assuming db is in models/__init__.py

# Load config from config.json
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

config = load_config()

class TestDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Set up the database instance once for all tests """
        cls.db_instance = db(config)

    def test_create_user(self):
        """ Test creating a new user independently """
        result = self.db_instance.create_user("testuser101@example.com", "hashed_password")
        self.assertTrue(result)

        # Verify user exists by creating a token
        result, token = self.db_instance.create_token("testuser101@example.com", "hashed_password", 1)
        self.assertTrue(result)

        # Clean up: delete the user after the test
        delete_status = self.db_instance.delete_user("testuser101@example.com", "hashed_password", token)
        self.assertTrue(delete_status)

        # Verify that the user was deleted by attempting to create a token
        result, token = self.db_instance.create_token("testuser101@example.com", "hashed_password", 1)
        self.assertFalse(result)

    def test_create_user_existing_email(self):
        """ Test creating a user with an existing email should fail """
        # First, create the user
        self.db_instance.create_user("testuser102@example.com", "hashed_password")

        # Try creating the same user again
        result = self.db_instance.create_user("testuser102@example.com", "hashed_password")
        self.assertFalse(result)

        # Clean up: delete the user
        result, token = self.db_instance.create_token("testuser102@example.com", "hashed_password", 1)
        delete_status = self.db_instance.delete_user("testuser102@example.com", "hashed_password", token)
        self.assertTrue(delete_status)

        # Verify that the user was deleted by attempting to create a token
        result, token = self.db_instance.create_token("testuser102@example.com", "hashed_password", 1)
        self.assertFalse(result)

    def test_create_token_valid_user(self):
        """ Test token creation for a valid user """
        self.db_instance.create_user("testuser103@example.com", "hashed_password")
        result, token = self.db_instance.create_token("testuser103@example.com", "hashed_password", 1)
        self.assertTrue(result)
        self.assertIsNotNone(token)

        # Clean up: delete the user
        delete_status = self.db_instance.delete_user("testuser103@example.com", "hashed_password", token)
        self.assertTrue(delete_status)

        # Verify that the user was deleted by attempting to create a token
        result, token = self.db_instance.create_token("testuser103@example.com", "hashed_password", 1)
        self.assertFalse(result)

    def test_verify_token_valid(self):
        """ Test verifying a valid token """
        self.db_instance.create_user("testuser104@example.com", "hashed_password")
        result, token = self.db_instance.create_token("testuser104@example.com", "hashed_password", 1)
        is_valid = self.db_instance.verify_token(token, "testuser104@example.com")
        self.assertTrue(is_valid)

        # Clean up: delete the user
        delete_status = self.db_instance.delete_user("testuser104@example.com", "hashed_password", token)
        self.assertTrue(delete_status)

        # Verify that the user was deleted by attempting to create a token
        result, token = self.db_instance.create_token("testuser104@example.com", "hashed_password", 1)
        self.assertFalse(result)

    def test_create_chat_history_valid_token(self):
        """ Test creating chat history with a valid token """
        self.db_instance.create_user("testuser105@example.com", "hashed_password")
        result, token = self.db_instance.create_token("testuser105@example.com", "hashed_password", 1)
        token_valid, create_status,_ = self.db_instance.create_chat_history(token, "testuser105@example.com", '{"message": "Hello!"}')
        self.assertTrue(token_valid)
        self.assertTrue(create_status)

        # Clean up: delete the user
        delete_status = self.db_instance.delete_user("testuser105@example.com", "hashed_password", token)
        self.assertTrue(delete_status)

        # Verify that the user was deleted by attempting to create a token
        result, token = self.db_instance.create_token("testuser105@example.com", "hashed_password", 1)
        self.assertFalse(result)

    # Access Control Tests

    def test_user_cannot_access_another_users_chat_history(self):
        """ Ensure one user cannot read another user's chat history """
        self.db_instance.create_user("testuser106@example.com", "hashed_password")
        result, token1 = self.db_instance.create_token("testuser106@example.com", "hashed_password", 1)
        self.db_instance.create_chat_history(token1, "testuser106@example.com", '{"message": "Hello from user106!"}')
        
        self.db_instance.create_user("testuser107@example.com", "hashed_password")
        result, token2 = self.db_instance.create_token("testuser107@example.com", "hashed_password", 1)
        self.db_instance.create_chat_history(token2, "testuser107@example.com", '{"message": "Hello from user107!"}')
        
        token_valid, read_status, chat_history = self.db_instance.read_chat_history(token1, "testuser107@example.com")
        self.assertFalse(token_valid)
        self.assertFalse(read_status)
        self.assertIsNone(chat_history)

        # Clean up: delete both users
        self.db_instance.delete_user("testuser106@example.com", "hashed_password", token1)
        self.db_instance.delete_user("testuser107@example.com", "hashed_password", token2)

        # Verify both users were deleted by attempting to create tokens
        result, token = self.db_instance.create_token("testuser106@example.com", "hashed_password", 1)
        self.assertFalse(result)
        result, token = self.db_instance.create_token("testuser107@example.com", "hashed_password", 1)
        self.assertFalse(result)

    def test_user_cannot_delete_another_users_chat_history(self):
        """ Ensure one user cannot delete another user's chat history """
        self.db_instance.create_user("testuser108@example.com", "hashed_password")
        result, token3 = self.db_instance.create_token("testuser108@example.com", "hashed_password", 1)
        self.db_instance.create_chat_history(token3, "testuser108@example.com", '{"message": "Hello from user108!"}')
        
        self.db_instance.create_user("testuser109@example.com", "hashed_password")
        result, token4 = self.db_instance.create_token("testuser109@example.com", "hashed_password", 1)
        self.db_instance.create_chat_history(token4, "testuser109@example.com", '{"message": "Hello from user109!"}')
        
        token_valid, delete_status = self.db_instance.delete_chat_history(token3, "testuser109@example.com", "fake-conversation-id")
        self.assertFalse(token_valid)
        self.assertFalse(delete_status)

        # Clean up: delete both users
        self.db_instance.delete_user("testuser108@example.com", "hashed_password", token3)
        self.db_instance.delete_user("testuser109@example.com", "hashed_password", token4)

        # Verify both users were deleted by attempting to create tokens
        result, token = self.db_instance.create_token("testuser108@example.com", "hashed_password", 1)
        self.assertFalse(result)
        result, token = self.db_instance.create_token("testuser109@example.com", "hashed_password", 1)
        self.assertFalse(result)

    # Security and Token Expiration

    def test_token_expiration(self):
        """ Test that expired tokens cannot be used """
        self.db_instance.create_user("testuser110@example.com", "hashed_password")
        result, token = self.db_instance.create_token("testuser110@example.com", "hashed_password", -1)  # Expired token
        token_valid, read_status, chat_history = self.db_instance.read_chat_history(token, "testuser110@example.com")
        self.assertFalse(token_valid)
        self.assertFalse(read_status)
        self.assertIsNone(chat_history)

        # Clean up: delete the user
        result, token = self.db_instance.create_token("testuser110@example.com", "hashed_password", 1) 
        delete_status = self.db_instance.delete_user("testuser110@example.com", "hashed_password", token)
        self.assertTrue(delete_status)

        # Verify that the user was deleted by attempting to create a token
        result, token = self.db_instance.create_token("testuser110@example.com", "hashed_password", 1)
        self.assertFalse(result)

    # Data Integrity

    def test_data_integrity(self):
        """ Test that data integrity is maintained during user actions """
        self.db_instance.create_user("testuser111@example.com", "hashed_password")
        result, token = self.db_instance.create_token("testuser111@example.com", "hashed_password", 1)
        token_validation,status,id = self.db_instance.create_chat_history(token, "testuser111@example.com", '{"message": "Hello!"}')
        
        # Ensure that data is stored correctly
        token_valid, read_status, chat_history = self.db_instance.read_chat_history(token, "testuser111@example.com")
        print(chat_history)
        for message in chat_history[0]:
            if message[0] == id:
                integrity_sample = message[1]
        test_message = json.loads(integrity_sample)['message']
        self.assertTrue(token_valid)
        self.assertTrue(read_status)
        self.assertEqual(test_message, 'Hello!')

        # Clean up: delete the user
        delete_status = self.db_instance.delete_user("testuser111@example.com", "hashed_password", token)
        self.assertTrue(delete_status)

        # Verify that the user was deleted by attempting to create a token
        result, token = self.db_instance.create_token("testuser111@example.com", "hashed_password", 1)
        self.assertFalse(result)

    # Test to ensure direct SQL queries are blocked
    def test_direct_insert_query_blocked(self):
        """ Ensure direct INSERT queries are blocked """
        with self.assertRaises(Exception):
            self.db_instance.execute_query(
                "INSERT INTO user_credentials (email, password_hash) VALUES (%s, %s);", 
                ("testuser201@example.com", "hashed_password")
            )

    def test_direct_select_query_blocked(self):
        """ Ensure direct SELECT queries are blocked """
        with self.assertRaises(Exception):
            self.db_instance.execute_query(
                "SELECT * FROM user_credentials WHERE email = %s;", 
                ("testuser201@example.com",)
            )

    def test_direct_update_query_blocked(self):
        """ Ensure direct UPDATE queries are blocked """
        with self.assertRaises(Exception):
            self.db_instance.execute_query(
                "UPDATE user_credentials SET password_hash = %s WHERE email = %s;", 
                ("new_hashed_password", "testuser201@example.com")
            )

    def test_direct_delete_query_blocked(self):
        """ Ensure direct DELETE queries are blocked """
        with self.assertRaises(Exception):
            self.db_instance.execute_query(
                "DELETE FROM user_credentials WHERE email = %s;", 
                ("testuser201@example.com",)
            )

if __name__ == '__main__':
    unittest.main()

