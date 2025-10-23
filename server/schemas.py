"""
Pydantic Schemas for Tutor AI API

This module defines all the data models used for request/response validation
in the FastAPI application. Uses Pydantic for automatic validation, serialization,
and API documentation generation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any

class SignupRequest(BaseModel):
    """Request model for user registration"""
    email: EmailStr
    password: str = Field(min_length=6, description="Password must be at least 6 characters")
    name: str

class LoginRequest(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: str

class ProfileUpdateRequest(BaseModel):
    """Request model for updating user profile"""
    name: str = Field(min_length=1, description="Name cannot be empty")
    email: EmailStr
    current_password: Optional[str] = None
    new_password: Optional[str] = Field(None, min_length=6)

class UserOut(BaseModel):
    """Response model for user information (excludes sensitive data)"""
    id: str
    email: EmailStr
    name: str

class ContentRequest(BaseModel):
    """Request model for content generation"""
    topic: str
    difficulty: str = "Intermediate"
    subject: str = "General"
    contentType: str = "Study Notes"
    learningObjectives: Optional[List[str]] = None

class ContentOut(BaseModel):

    """Response model for generated content"""
    
    id: str
    topic: str
    content: str
    metadata: Dict[str, Any]  # Additional info like subject, difficulty, etc.

class GeneratedContent(BaseModel):
    query: str
    embedding: List[float] = []
    content: str
    topic: str
    difficulty: str
    objectives: Optional[List[str]] = None
    similarity_threshold: float = 0.8
    created_at: str
    updated_at: Optional[str] = None

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
    individualEvaluations: Optional[List[Dict[str, Any]]] = None
