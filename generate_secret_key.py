"""
Generate a new Django SECRET_KEY for production
"""
from django.core.management.utils import get_random_secret_key

print("🔐 Generated SECRET_KEY for production:")
print()
print(get_random_secret_key())
print()
print("Copy this to your .env file or Render environment variables")
