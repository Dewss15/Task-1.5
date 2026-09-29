from fastapi import FastAPI,Depends,HTTPException,Request
from pydantic import BaseModel
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from jose import jwt,JWTError,ExpiredSignatureError
from datetime import datetime,timezone,timedelta
from slowapi import Limiter,_rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import requests

app=FastAPI(title="Task 1.4")  #instance of fastapi titled task 1.4
sec=HTTPBearer()   #instance of HTTPBearer to get the header
SECRET_KEY="secret"
ALGORITHM="HS256"

class LoginReq(BaseModel):  #pydantic class to validate username and password 
    username:str
    password:str

@app.post("/auth/token")

#Login function to verify username and password in order to return a token
def login(obj:LoginReq):

    """ This func checks if the username or password are valid and raises 401 exception if invalid exceptions else a func call is made to create token which returns a token and displays the below dict """

    if obj.username!="admin" or obj.password!="1234":
        raise HTTPException(status_code=401,detail="Invalid credentials")
    token=create_token({"sub":obj.username})
    return {"access_token":token,"type":"bearer"}

#Token creation
def create_token(data:dict):

    """ Th expiry date is added to the data dict and a signed token is made from data,secret key and algo """

    exp=datetime.now(timezone.utc)+timedelta(minutes=15)
    data.update({"exp":exp})
    token=jwt.encode(data,SECRET_KEY,algorithm=ALGORITHM)
    return token


#Token verification
def verify_token(token:HTTPAuthorizationCredentials=Depends(sec)):

    " Credentials r extracted from signed token and the signed token is checked by using secret key and algo"
    " If token is expired(after 15 mins) , then u get expiredsignerror"

    token=token.credentials
    try:
        token_decode=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return token_decode
    except ExpiredSignatureError:
        raise HTTPException(status_code=401,detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401,detail="Invalid token")

def get_header(request:Request):
    auth=request.headers.get("Authorization"," ")

    if auth.startswith("Bearer "):
        return auth.split(" ",1)[1]
    return "Unauthorised"

limiter=Limiter(key_func=get_header)
app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)


@app.get("/v1/completions")
@limiter.limit("5/minute")
def protected(request:Request,pro=Depends(verify_token)):
    if pro["exp"]>15:
        create_token(pro)
    return {"sub":pro["sub"]}


def fetch_ext():
    resp=requests.get("https://api.com/data")
    return resp.json()





