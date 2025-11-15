#!/usr/bin/env python3
"""
Utility script to generate a Fernet encryption key for CREDENTIALS_ENCRYPTION_KEY

Usage:
    python3 generate_key.py
"""
from cryptography.fernet import Fernet

if __name__ == '__main__':
    key = Fernet.generate_key()
    print("\n" + "="*60)
    print("Generated Fernet Encryption Key:")
    print("="*60)
    print(f"\n{key.decode()}\n")
    print("="*60)
    print("\nCopy this key to your .env file:")
    print("CREDENTIALS_ENCRYPTION_KEY=" + key.decode())
    print("\n⚠️  WARNING: DO NOT change this key after users have")
    print("   stored platform credentials, or their credentials")
    print("   will become unreadable!")
    print("="*60 + "\n")
