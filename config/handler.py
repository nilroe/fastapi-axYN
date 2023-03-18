import time
from typing import Dict
from jose import jwt

JWT_SECRET="GsTbHGLBC1ZVp1wNiJhNy6Cw?Qznu!cMcOMz/fAj2XR8MPDUvANxFBC7O-AhLKCX1o9V0Q5==QI!xJPUCHBvb/qhu/zaG1I4lFNSo1LecVaLfe9rxU5ImukKuU0qTBBdE0PjMUyHp7S0VB0/wXuk-9Jnm/Cfy5yYW?z-TLfr!PJvKXvI2UFifbRE5CIOMSu!01oloV6/P2gxBYVkBJJEuAB4L-egB0Ta09lG79!Zd7gRm6uzL01X/t3/RBehj3Gi"
JWT_ALGORITHM="HS256"


def token_response(token: str):
    return {
        "access_token": token
    }

def enToken(user_id: str, user_company: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "user_company": user_company,
        "expires": time.time() + 86400
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)

def deToken(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"]>= time.time() else None
    except:
        return {}