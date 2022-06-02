import re
from fastapi import HTTPException
regex = '^[\w\.]+@([\w]+\.)+[\w]{2,4}$'

def validate_email(email):
    if not re.match(regex, email):
        raise HTTPException(status_code=400, detail=str("Email error"))
