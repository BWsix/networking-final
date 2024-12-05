def hash_password(password: str) -> str:
    """
    Hash password.
    
    :param password: Password to hash.
    
    :return: Hashed password.
    """

    # TODO(Low priority): Implement password hashing
    return password + "hashed"

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify password.
    
    :param password: Password to verify.
    :param hashed_password: Hashed password.
    
    :return: True if password is correct, False otherwise.
    """

    # TODO(Low priority): Implement password verification
    return hash_password(password) == hashed_password

def get_jwt(payload: str) -> str:
    """
    Get JWT token from payload.
    
    :param payload: User payload.

    :return: JWT token.
    """

    # TODO(Low priority): Implement JWT token generation
    return payload
