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