"""User domain model and persistence helpers for authentication and registration."""

from __future__ import annotations

import logging
from typing import Any, Final, cast

import pandas
from pandas import DataFrame

logger = logging.getLogger(__name__)

LOGINS_DTYPE: Final[dict[str, type[str]]] = {
    'id': str,
    'email': str,
    'password': str,
    'name': str,
    'role': str,
}

# Class User represents the logged-in user and operations over user data.
class User:
    """Represents the currently authenticated user and user-related operations."""

    # Initializes an empty user state before login.
    # Inputs: no inputs.
    # Returns: None.
    def __init__(self) -> None:
        """Initialize empty user state before authentication."""
        self.u_id: str | None = None
        self.email: str | None = None
        self.password: str | None = None
        self.name: str | None = None
        self.role: str | None = None

    @staticmethod
    # Loads users from logins.csv.
    # Inputs: no inputs.
    # Returns: pandas.DataFrame with users.
    def load_users_data() -> DataFrame:
        """Load users from CSV with explicit dtypes."""
        logger.debug("Loading users data from logins.csv")
        return pandas.read_csv("logins.csv", dtype=cast(Any, LOGINS_DTYPE))

    # Verifies login credentials and fills instance attributes on success.
    # Inputs: username (str), password (str).
    # Returns: bool - True on successful authentication, otherwise False.
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user by email and password and update in-memory state."""
        data = User.load_users_data() # Load with explicit column types.

        # Trim leading/trailing spaces in email and password columns.
        data['email'] = data['email'].str.strip()
        data['password'] = data['password'].str.strip()

        username = str(username).strip()  # Trim spaces from input.
        password = str(password).strip()  # Trim spaces from input.

        mask = (data['email'] == username) & (data['password'] == password)
        filtered_data = data[mask]

        if not filtered_data.empty:
            self.u_id = str(filtered_data['id'].iloc[0])
            self.email = str(filtered_data['email'].iloc[0])
            self.password = str(filtered_data['password'].iloc[0])
            self.name = str(filtered_data['name'].iloc[0])
            self.role = str(filtered_data['role'].iloc[0])
            logger.info(f"Authentication successful: user_id={self.u_id} email={self.email} role={self.role}")
            return True

        self.u_id = None
        self.email = None
        self.password = None
        self.name = None
        self.role = None
        logger.warning(f"Authentication failed for email={username}")
        return False

    @staticmethod
    # Creates a new user if the email does not already exist.
    # Inputs: email (str), password (str), name (str), role (str).
    # Returns: tuple(bool, str) - operation status and UI message.
    def create_user(email: str, password: str, name: str, role: str) -> tuple[bool, str]:
        """Create a new user record and persist it to CSV if validation passes."""
        data = User.load_users_data()

        email = str(email).strip()
        password = str(password).strip()
        name = str(name).strip()
        role = str(role).strip().lower()

        if not email or not password or not name:
            logger.warning("User registration failed: missing required fields")
            return False, "Vypln vsetky polia"

        data['id'] = data['id'].astype(str).str.strip()
        data['email'] = data['email'].astype(str).str.strip()

        if email in data['email'].values:
            logger.warning(f"User registration failed: email already exists ({email})")
            return False, "Pouzivatel s tymto e-mailom uz existuje"

        new_id = str(data['id'].astype(int).max() + 1)
        new_user = pandas.DataFrame([
            {
                'id': new_id,
                'email': email,
                'password': password,
                'name': name,
                'role': role
            }
        ])
        data = pandas.concat([data, new_user], ignore_index=True)
        data.to_csv("logins.csv", index=False)
        logger.info(f"User registered successfully: user_id={new_id} email={email} role={role}")
        return True, "Registracia bola uspesna"
