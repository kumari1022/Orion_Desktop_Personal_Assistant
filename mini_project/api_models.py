from pydantic import BaseModel


class CommandRequest(BaseModel):
    command: str


class CommandResponse(BaseModel):
    success: bool
    response: str


class AuthResponse(BaseModel):
    success: bool
    status: str