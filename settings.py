#import os

class TokenManager(object):
    def __init__(self, token_file, oauth_client_id, oauth_client_secret, scopes, commands):
        try:
            self.token_file = token_file
            self.oauth_client_id = oauth_client_id
            self.oauth_client_secret = oauth_client_secret
            self.scopes = scopes
            self.commands = commands
            self.token = self.get_token()
        except Exception as e:
            print(e)

    def get_token(self):
        try:
            with open(self.token_file,'r') as f:
                return f.read()
        except Exception as e:
            return self.set_token('undefined')

    def set_token(self, token):
        print(token)
        self.token = token
        if token is not None:
            with open(self.token_file, 'w') as f:
                f.write(token)
        else:
            print("TokenManagerError: Token is now None!")
        return token


class KibanaSettings(object):
    OAUTH_CLIENT_ID = "<YOUR_OAUTH_CLIENT_ID>"
    OAUTH_CLIENT_SECRET = "<YOUR_OAUTH_CLIENT_SECRET>"
    SCOPES = "spark-dashboard:view"
    TOKEN_FILE='current_token.txt'
    COMMANDS = []
