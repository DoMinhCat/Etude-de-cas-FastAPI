import hmac
import hashlib

def hash_password_hs256(password, secret_key):
    """
    Hashes a password using HMAC-SHA256.

    Args:
        password (str): The password to hash.
        secret_key (str): The secret key for the hash.

    Returns:
        str: The hexadecimal string of the hashed password.
    """
    secret_key_bytes = secret_key.encode('utf-8')
    password_bytes = password.encode('utf-8')
    
    hashed_password = hmac.new(secret_key_bytes, password_bytes, hashlib.sha256).hexdigest()
    
    return hashed_password

# --- Example Usage ---
# Use a strong, secret key that is not stored in your code.
# For production, this should be an environment variable.
my_secret_key = "DEPLANO"

# The password to hash
my_password = "123"

# Get the hashed password
hashed_pwd = hash_password_hs256(my_password, my_secret_key)

print(f"Original Password: {my_password}")
print(f"Secret Key: {my_secret_key}")
print(f"Hashed Password (HS256): {hashed_pwd}")