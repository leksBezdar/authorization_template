from fastapi import HTTPException

class InvalidAuthenthicationCredential(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid authenthication credentials")
        
class InvalidToken(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid token")

class TokenExpired(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Token has expired")
        
class Forbidden(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Forbidden for you")
        
class NoUserData(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User data was not found")
        
class UserDoesNotExist(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User does not exist")
        
class UserAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User is already Exists")
