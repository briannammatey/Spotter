# backend/auth.py

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional
from werkzeug.security import generate_password_hash, check_password_hash

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_users() -> Dict[str, Any]:
    _ensure_data_dir()
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save_users(users: Dict[str, Any]) -> None:
    _ensure_data_dir()
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def _load_sessions() -> Dict[str, Any]:
    _ensure_data_dir()
    if not os.path.exists(SESSIONS_FILE):
        return {}
    with open(SESSIONS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save_sessions(sessions: Dict[str, Any]) -> None:
    _ensure_data_dir()
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f, indent=2)


def _is_bu_email(email: str) -> bool:
    return email.lower().endswith("@bu.edu")


def _create_session(email: str) -> str:
    """Create a new session token for the user"""
    token = str(uuid.uuid4())
    sessions = _load_sessions()
    
    # Session expires in 7 days
    expiry = (datetime.now() + timedelta(days=7)).isoformat()
    
    sessions[token] = {
        "email": email,
        "created_at": datetime.now().isoformat(),
        "expires_at": expiry
    }
    
    _save_sessions(sessions)
    return token


def validate_token(token: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a session token.
    Returns (is_valid, email_or_none)
    """
    if not token:
        return False, None
    
    sessions = _load_sessions()
    session = sessions.get(token)
    
    if not session:
        return False, None
    
    # Check if expired
    expiry = datetime.fromisoformat(session["expires_at"])
    if datetime.now() > expiry:
        # Remove expired session
        del sessions[token]
        _save_sessions(sessions)
        return False, None
    
    return True, session["email"]


def logout_user(token: str) -> Tuple[bool, Dict[str, Any], int]:
    """Remove the session token"""
    if not token:
        return False, {"success": False, "error": "No token provided"}, 400
    
    sessions = _load_sessions()
    if token in sessions:
        del sessions[token]
        _save_sessions(sessions)
    
    return True, {"success": True, "message": "Logged out successfully"}, 200


def register_user(email: str, password: str) -> Tuple[bool, Dict[str, Any], int]:
    """
    Register a new user with a BU email and hashed password.
    Returns (success, response_body, status_code)
    """
    if not email or not password:
        return False, {"success": False, "error": "Email and password are required."}, 400

    email = email.strip().lower()

    if not _is_bu_email(email):
        return False, {
            "success": False,
            "error": "Only BU emails (@bu.edu) are allowed."
        }, 400

    users = _load_users()

    if email in users:
        return False, {
            "success": False,
            "error": "An account with this email already exists."
        }, 400

    if len(password) < 6:
        return False, {
            "success": False,
            "error": "Password must be at least 6 characters long."
        }, 400

    password_hash = generate_password_hash(password)

    users[email] = {
        "email": email,
        "password_hash": password_hash,
        "created_at": datetime.now().isoformat()
    }

    _save_users(users)

    # Create session
    token = _create_session(email)

    return True, {
        "success": True,
        "message": "User registered successfully.",
        "token": token,
        "email": email,
    }, 201


def login_user(email: str, password: str) -> Tuple[bool, Dict[str, Any], int]:
    """
    Log in an existing user. Validates email & password.
    Returns (success, response_body, status_code)
    """
    if not email or not password:
        return False, {"success": False, "error": "Email and password are required."}, 400

    email = email.strip().lower()
    users = _load_users()

    user = users.get(email)
    if not user:
        return False, {"success": False, "error": "Invalid email or password."}, 401

    if not check_password_hash(user["password_hash"], password):
        return False, {"success": False, "error": "Invalid email or password."}, 401

    # Create session
    token = _create_session(email)

    return True, {
        "success": True,
        "message": "Login successful.",
        "token": token,
        "email": email,
    }, 200
