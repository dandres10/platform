import jwt
from datetime import datetime, timedelta
from src.core.config import settings
 
 
class Token:
    def __init__(
        self,
    ):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expiration_minutes = 120
        self.refresh_token_expiration_minutes = 122
 
    def createAccessToken(self, data: dict):
        expiration = datetime.utcnow() + timedelta(
            minutes=self.access_token_expiration_minutes
        )
        to_encode = data.copy()
        to_encode.update({"exp": expiration})
        
        
        access_token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return access_token
 
    def create_refresh_token(self, data):
        expiration = datetime.utcnow() + timedelta(
            minutes=self.refresh_token_expiration_minutes
        )
        to_encode = data.copy()
        to_encode.update({"exp": expiration})
        refresh_token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return refresh_token
 
    def verify_token(self, token):
        try:
            decoded_token = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return decoded_token
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
 
    def decode_token(self, token):
        try:
            decoded_token = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return decoded_token
        except:
            return None
 
    def refresh_access_token(self, refresh_token, body: dict):
        try:
            decoded_token = jwt.decode(
                refresh_token, self.secret_key, algorithms=[self.algorithm]
            )
 
            if decoded_token:
                new_access_token = self.createAccessToken(body)
                return new_access_token
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None