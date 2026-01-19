"""
Learning API Schemas (Phase 2)
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union
from datetime import datetime
from enum import Enum

# Enums
class Priority(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

class ContentType(str, Enum):
    chapter = "chapter"
    quiz = "quiz"
    practice = "practice"
    review = "review"
    assessment = "assessment"

class LearningPaceCategory(str, Enum):
    slow = "slow"
    moderate = "moderate"
    fast = "fast"
    intensive = "intensive"

class LearningStyle(str, Enum):
    visual = "visual"
    auditory = "auditory"
    reading = "reading"
    hands_on = "hands_on"
    unknown = "unknown"

class SeverityLevel(str, Enum):
    critical = "critical"
    moderate = "moderate"
    minor = "minor"

class Feasibility(str, Enum):
    achievable = "achievable"
    challenging = "challenging"
    at_risk = "at_risk"
    infeasible = "infeasible"

class LearningProfileBase(BaseModel):
    learning_pace: dict
    learning_style: dict
    strengths: List[dict]
    weaknesses: List[dict]
    overall_progress: dict

class LearningProfile(LearningProfileBase):
    user_id: str
    ai_insights: Optional[dict] = None
    generated_by: Optional[str] = None

class LearningProfileResponse(BaseModel):
    user_id: str
    profile: LearningProfileBase
    learning_history: Optional[List[dict]] = None
    ai_insights: Optional[dict] = None
    cached: Optional[bool] = None
    cache_expires_at: Optional[str] = None
    upgrade_prompt: Optional[dict] = None

class Recommendation(BaseModel):
    id: str
    type: ContentType
    content_id: str
    title: str
    priority: Priority
    reason: str
    estimated_time_minutes: int
    difficulty_match: Optional[Literal["too_easy", "appropriate", "challenging", "too_hard"]] = None
    prerequisites_met: Optional[bool] = None
    missing_prerequisites: Optional[List[str]] = None
    focus_areas: Optional[List[str]] = None
    potential_achievement: Optional[str] = None
    confidence: float
    tags: List[str]

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[Recommendation]
    session_context: Optional[dict] = None
    generated_by: str
    generated_at: Optional[str] = None
    cache_key: Optional[str] = None
    cached: Optional[bool] = None
    cache_expires_at: Optional[str] = None
    upgrade_prompt: Optional[dict] = None
    fallback: Optional[bool] = None
    fallback_reason: Optional[str] = None

class KnowledgeGap(BaseModel):
    id: str
    topic: str
    severity: SeverityLevel
    severity_score: int
    affected_chapters: List[str]
    root_cause: dict
    recommended_content: List[dict]
    impact_if_unaddressed: str

class KnowledgeGapResponse(BaseModel):
    user_id: str
    analysis_summary: dict
    knowledge_gaps: List[KnowledgeGap]
    remediation_plan: Optional[dict] = None
    generated_by: str
    generated_at: str
    analysis_depth: str
    upgrade_prompt: Optional[dict] = None

class LearningStep(BaseModel):
    step_id: str
    order: int
    type: ContentType
    content_id: str
    title: str
    description: Optional[str] = None
    duration_minutes: int
    scheduled_date: str
    priority: Priority
    focus_sections: Optional[List[str]] = None
    checkpoint: Optional[dict] = None

class LearningPhase(BaseModel):
    phase_number: int
    name: str
    description: str
    duration_days: int
    start_date: str
    end_date: str
    steps: List[LearningStep]

class Milestone(BaseModel):
    milestone_id: str
    name: str
    target_date: str
    requirements: List[str]  # step_ids
    reward: str

class LearningPath(BaseModel):
    path_id: str
    user_id: str
    generated_at: str
    summary: dict
    phases: List[LearningPhase]
    milestones: List[Milestone]
    personalization_factors: dict

class LearningPathSummary(BaseModel):
    total_duration_hours: float
    total_sessions: int
    estimated_completion_date: str
    target_date: Optional[str] = None
    buffer_days: Optional[int] = None
    feasibility: Feasibility
    confidence: float

class LearningPathRequest(BaseModel):
    user_id: str
    goal: dict
    constraints: dict
    options: Optional[dict] = None

class LearningPathResponse(BaseModel):
    path_id: str
    user_id: str
    generated_at: str
    summary: LearningPathSummary
    learning_path: LearningPath
    personalization_factors: dict
    ai_notes: Optional[dict] = None
    actions: Optional[dict] = None
    generated_by: str

class NextStep(BaseModel):
    step_number: int
    action: str
    content_id: str
    title: str
    description: Optional[str] = None
    duration_minutes: int
    reason: str
    progress: Optional[dict] = None
    cta: str

class NextStepsResponse(BaseModel):
    user_id: str
    session_context: dict
    next_steps: List[NextStep]
    alternative_paths: Optional[List[dict]] = None
    motivational_context: Optional[dict] = None
    generated_by: str
    generated_at: Optional[str] = None
    upgrade_prompt: Optional[dict] = None
    fallback: Optional[bool] = None
    fallback_reason: Optional[bool] = None