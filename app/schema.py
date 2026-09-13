from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Register(BaseModel):
    id: int
    name: str
    rollno: str
    department: str
    created_at: datetime

    class Config: 
        from_attributes=True

class Send_Register(BaseModel):
    name: str
    rollno: str
    password: str
    department: str

class Token(BaseModel):
    encode_token: str
    type: str

class TokenData(BaseModel):
    id: Optional[int]

class Question(BaseModel):
    question: str
    tags: list

class Answerdb(BaseModel):
    id: int
    answer: str
    question_id: int
    owner_id: int
    created_at: datetime
    owner: Register

    class Config:
        from_attributes=True

class Answer(BaseModel):
    question_id: int
    answer: str

class Votes(BaseModel):
    answer_id: int
    vote_dir: int

    class Config:
        form_attributes=True

class UserVoteOut(BaseModel):
    answer_id: int
    vote_dir: int

    class Config:
        from_attributes = True

class DiscoverUser(BaseModel):
    id: int
    name: str
    rollno: str
    department: str
    follow_status: str
    class Config: 
        from_attributes=True

class AttachmentResponse(BaseModel):
    id: int
    question_id: int
    file_name: str
    file_type: str
    file_size: int
    storage_path: str

    class Config:
        from_attributes = True

class Questiondb(BaseModel):
    id: int
    question: str
    tags: list
    created_at: datetime
    isSolved: bool
    owner: Optional[Register] = None
    attachment: list[AttachmentResponse] = Field(
        default_factory=list,
        validation_alias="attachments"
    )

    class Config: 
        from_attributes=True

class UserQuestions(BaseModel):
    id: int
    name: str
    rollno: str
    department: str
    questions: list[Questiondb]

class AttachmentAccessResponse(BaseModel):
    id: int
    question_id: int
    file_name: str
    file_type: str
    file_size: int
    url: str

    class Config:
        from_attributes = True