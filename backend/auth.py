# backend/auth.py

import os
import json
import uuid
from typing import Tuple, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


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
            # corrupted file, start fresh
            return {}


def _save_users(users: Dict[str, Any]) -> None:
    _ensure_data_dir()
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def _is_bu_email(email: str) -> bool:
    return email.lower().endswith("@bu.edu")


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

    password_hash = generate_password_hash(password)

    users[email] = {
        "email": email,
        "password_hash": password_hash,
        # you can add more fields here later, e.g. display_name
    }

    _save_users(users)

    # fake session token for demo purposes
    token = str(uuid.uuid4())

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

    # fake session token for demo/demo video
    token = str(uuid.uuid4())

    return True, {
        "success": True,
        "message": "Login successful.",
        "token": token,
        "email": email,
    }, 200
