import secrets

def generate_key():
	secret_key = secrets.token_urlsafe(32)
	print(secret_key)
