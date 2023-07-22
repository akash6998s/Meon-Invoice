from flask import session, abort
from functools import wraps

def authenticate_user(func):
	@wraps(func)
	def inner(*args, **kwargs):
		print("authenticating...")
		if session.get('user', None):
			return func(*args, **kwargs)
		return abort(403)
	return inner
