from rest_framework import exceptions
import jwt, datetime

def create_access_token(id):
    return jwt.encode({
        'user_id':id,
        'exp':datetime.datetime.now()+datetime.timedelta(30),
        'iat':datetime.datetime.now()
    }, 'access_secret', algorithm='HS256')

def create_refresh_token(id):
    return jwt.encode({
        'user_id':id,
        'exp':datetime.datetime.now()+datetime.timedelta(days=7),
        'iat':datetime.datetime.now()
    }, 'refresh_secret', algorithm='HS256')

def decode_access_token(token):
    try:
        payload=jwt.decode(token, 'access_secret', algorithms='HS256')

        return payload["user_id"]
    except Exception as e:
        print(e)
        raise exceptions.APIException("unauthenticated")
