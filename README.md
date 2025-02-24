# agent-ui
### Introduction 
https://docs.streamlit.io/deploy/tutorials/docker
https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/

```
from streamlit_authenticator.utilities.hasher import Hasher
# Pass the list of passwords directly to the 
# Hasher constructor and generate the hashes
passwords_to_hash = ['cdp@123']
hashed_passwords = Hasher(passwords_to_hash).generate()

print(hashed_passwords)

```
