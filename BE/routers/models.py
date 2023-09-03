from typing import Dict, Optional
from pydantic import BaseModel


class User(BaseModel):
    userId: str
    displayName: str
    jobRole :Optional[str]


class User_data(BaseModel):
    storyPoints: float


class User_details (User):
    isAdmin: Optional[bool]
    isActive: Optional[bool]
    data: Optional[User_data]


class User_action(BaseModel):
    actionType: str
    userData: Optional[User_details]
