# Module users.py handles user operations: loading, authentication,
# and user registration into logins.csv.
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
    # Initializes an empty user state before login.
    # Inputs: no inputs.
    # Returns: None.
    def __init__(self) -> None:
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
        logger.debug("Loading users data from logins.csv")
        return pandas.read_csv("logins.csv", dtype=cast(Any, LOGINS_DTYPE))

    # Verifies login credentials and fills instance attributes on success.
    # Inputs: username (str), password (str).
    # Returns: bool - True on successful authentication, otherwise False.
    def authenticate(self, username: str, password: str) -> bool:
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
            logger.info("Authentication successful: user_id=%s email=%s role=%s", self.u_id, self.email, self.role)
            return True

        self.u_id = None
        self.email = None
        self.password = None
        self.name = None
        self.role = None
        logger.warning("Authentication failed for email=%s", username)
        return False

    @staticmethod
    # Creates a new user if the email does not already exist.
    # Inputs: email (str), password (str), name (str), role (str).
    # Returns: tuple(bool, str) - operation status and UI message.
    def create_user(email: str, password: str, name: str, role: str) -> tuple[bool, str]:
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
            logger.warning("User registration failed: email already exists (%s)", email)
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
        logger.info("User registered successfully: user_id=%s email=%s role=%s", new_id, email, role)
        return True, "Registracia bola uspesna"
