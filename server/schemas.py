from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str

class ContentRequest(BaseModel):
    topic: str
    difficulty: str = "Intermediate"
    subject: str = "General"
    contentType: str = "Study Notes"
    learningObjectives: Optional[List[str]] = None

class ContentOut(BaseModel):
    id: str
    topic: str
    content: str
    metadata: Dict[str, Any]

class QuestionGenRequest(BaseModel):
    contentId: str
    questionCount: int = 5
    questionTypes: List[str] = ["Multiple Choice", "Short Answer"]
    difficultyDistribution: Optional[Dict[str, float]] = None
    bloomLevels: Optional[List[str]] = None

class QuestionSetOut(BaseModel):
    id: str
    contentId: str
    questions: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class AnswerSubmitRequest(BaseModel):
    questionSetId: str
    answers: Dict[int, Any]

class FeedbackOut(BaseModel):
    id: str
    questionSetId: str
    overallScore: float
    detailedFeedback: str
    studySuggestions: Optional[str] = None
