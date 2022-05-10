import os
from dotenv import load_dotenv

GH_TOEKN_KEY = "g_token"

"""
    $ gpg -o .env.gpg -c .env
    $ echo "passphrase" | gpg --passphrase-fd 0 -o .env -d .env.gpg
"""
load_dotenv('.env')

def get_gh_token():
    return os.environ[GH_TOEKN_KEY]