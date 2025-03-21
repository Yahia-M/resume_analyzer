import streamlit_authenticator as stauth

# List of passwords to hash , "securepassword"
passwords = "password123"

# Hash the passwords
hashed_passwords = stauth.Hasher(passwords)#.generate()

# Print the hashed passwords
print(hashed_passwords)