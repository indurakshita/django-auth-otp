import jwt
import datetime
from django.conf import settings

def token_generation(user_id):
 
    secret_key=settings.SECRET_KEY
    payload = {
        "user_id":user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token