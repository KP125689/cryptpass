import getpass
import hashlib
import json
import string
import random
from cryptography.fernet import Fernet

# Generate or load the key
key = Fernet.generate_key()
cipher_suite = Fernet(key)

MASTER_PASSWORD_FILE = 'master_password.json'
PASSWORDS_FILE = 'passwords.json'

# Function to hash the master password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to set the master password
def set_master_password():
    password = getpass.getpass("Set a master password: ")
    confirm_password = getpass.getpass("Confirm master password: ")
    if password == confirm_password:
        master_password_hash = hash_password(password)
        with open(MASTER_PASSWORD_FILE, 'w') as f:
            json.dump({'master_password_hash': master_password_hash}, f)
        print("Master password set successfully.")
    else:
        print("Passwords do not match. Please try again.")
        set_master_password()

# Function to authenticate the user
def authenticate():
    try:
        with open(MASTER_PASSWORD_FILE, 'r') as f:
            data = json.load(f)
        master_password_hash = data['master_password_hash']
    except FileNotFoundError:
        print("Master password not set.")
        set_master_password()
        return authenticate()
    
    password = getpass.getpass("Enter the master password: ")
    if hash_password(password) == master_password_hash:
        print("Access granted.")
        return True
    else:
        print("Access denied.")
        return False

# Functions to encrypt and decrypt passwords
def encrypt_password(password):
    return cipher_suite.encrypt(password.encode())

def decrypt_password(encrypted_password):
    return cipher_suite.decrypt(encrypted_password).decode()

# Load passwords from file
passwords = {}

def save_passwords():
    with open(PASSWORDS_FILE, 'w') as f:
        json.dump(passwords, f)

def load_passwords():
    global passwords
    try:
        with open(PASSWORDS_FILE, 'r') as f:
            passwords = json.load(f)
    except FileNotFoundError:
        passwords = {}

# Password management functions
def add_password(service, username, password):
    passwords[service] = {
        'username': username,
        'password': encrypt_password(password).decode()
    }
    save_passwords()

def get_password(service):
    if service in passwords:
        encrypted_password = passwords[service]['password']
        return {
            'username': passwords[service]['username'],
            'password': decrypt_password(encrypted_password.encode())
        }
    else:
        return None

def update_password(service, new_password):
    if service in passwords:
        passwords[service]['password'] = encrypt_password(new_password).decode()
        save_passwords()

def delete_password(service):
    if service in passwords:
        del passwords[service]
        save_passwords()

# Password creation function
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

# Command-line interface
def main():
    load_passwords()
    if not authenticate():
        return

    while True:
        print("\nPassword Manager")
        print("1. Add password")
        print("2. Get password")
        print("3. Update password")
        print("4. Delete password")
        print("5. Generate password")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            service = input("Enter the service name: ")
            username = input("Enter the username: ")
            password = getpass.getpass("Enter the password (leave blank to generate one): ")
            if not password:
                password = generate_password()
                print(f"Generated password: {password}")
            add_password(service, username, password)
        elif choice == '2':
            service = input("Enter the service name: ")
            creds = get_password(service)
            if creds:
                print(f"Username: {creds['username']}")
                print(f"Password: {creds['password']}")
            else:
                print("Service not found.")
        elif choice == '3':
            service = input("Enter the service name: ")
            new_password = getpass.getpass("Enter the new password (leave blank to generate one): ")
            if not new_password:
                new_password = generate_password()
                print(f"Generated password: {new_password}")
            update_password(service, new_password)
        elif choice == '4':
            service = input("Enter the service name: ")
            delete_password(service)
        elif choice == '5':
            length = int(input("Enter the length of the password (default 12): ") or 12)
            generated_password = generate_password(length)
            print(f"Generated password: {generated_password}")
        elif choice == '6':
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
