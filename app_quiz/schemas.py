from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[UUID]
    role: Optional[str]

class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    role: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class ChoiceBase(BaseModel):
    text: str
    is_answer: bool = False

class ChoiceCreate(ChoiceBase):
    pass

class ChoiceRead(BaseModel):
    id: UUID
    text: str

class QuestionBase(BaseModel):
    text: str
    choices: List[ChoiceCreate]

class QuestionCreate(QuestionBase):
    pass

class QuestionRead(BaseModel):
    id: UUID
    text: str
    choices: List[ChoiceRead]

class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    question_limit: int = 10
    randomize: bool = True

class QuizCreate(QuizBase):
    questions: List[QuestionCreate]

class QuizRead(QuizBase):
    id: UUID

class SubmissionRead(BaseModel):
    id: UUID
    created_at: datetime
    score: float

class AnswerCreate(BaseModel):
    question_id: UUID
    choice_id: UUID

class SubmissionCreate(BaseModel):
    answers: List[AnswerCreate]
    
class QuizStatus(BaseModel):
    quiz_id: UUID
    title: str
    submitted: bool
    submitted_at: Optional[datetime]
    score: Optional[float]

class QuizSessionRead(BaseModel):
    session_id: UUID
    questions: List[QuestionRead]

class SubmissionCreate(BaseModel):
    session_id: UUID
    answers: List[AnswerCreate]