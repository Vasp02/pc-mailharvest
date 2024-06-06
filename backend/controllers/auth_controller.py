import imaplib
import datetime
import bcrypt
from utils import dbutils
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from dotenv import load_dotenv
import os
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

def login_user(email,password):
    print(f"email : {email}")
    print(f"password : {password}")
    if is_account_valid(email,password):
        if not dbutils.does_accounts_table_exist():
            dbutils.create_accounts_table()
        if not dbutils.account_exists(email):
            hashed_password, salt = encrypt_pass(password)
            dbutils.save_account(email,hashed_password,salt)
        jwt = generate_jwt(email,password)
        return jwt




def is_account_valid(email,password,email_server='imap.gmail.com'):
    try:
        imap = imaplib.IMAP4_SSL(email_server)
        imap.login(email, password)
        print("Authentication successful")
        imap.logout()
        return True
    except imaplib.IMAP4.error as e:
        print(f"Login failed: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def generate_jwt(email,password):
    payload = {
        "email": email,
        "password": password,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),  # Token expiration time (1 day from now)
        "iat": datetime.datetime.utcnow()  # Issued at time
    }
    # Generate JWT
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def validate_jwt(encoded_jwt):
    try:
        decoded = jwt.decode(encoded_jwt, SECRET_KEY, algorithms=["HS256"])
        return {"status": "success", "payload": decoded}
    except ExpiredSignatureError:
        return {"status": "error", "message": "Token is expired"}
    except InvalidTokenError:
        return {"status": "error", "message": "Invalid token"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def encrypt_pass(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return (hashed_password,salt)

def validate_account_credentials(email, password):
    account = dbutils.get_account_by_email(email)
    account_salt = account.get('password_salt')
    account_hashed_password = account.get('password_hash').encode('utf-8')
    # provided_password_hashed = bcrypt.hashpw(password.encode('utf-8'), account_salt.encode('utf-8'))
    if bcrypt.checkpw(password.encode('utf-8'), account_hashed_password):
        print("Password is valid.")
        return True
    else:
        print("Invalid password.")
        return False

def extract_email_and_password_from_jwt(jwt_token):
    try:
        decoded = jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256"])
        email = decoded.get('email')
        password = decoded.get('password')
        return email, password
    except Exception as e:
        print(e)
        return None, None





