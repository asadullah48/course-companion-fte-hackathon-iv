"""
Adaptive Learning API Endpoints (Phase 2)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Literal
from datetime import datetime, timedelta
import uuid
import json

from ...models.user import User
from ...models.progress import ChapterProgress, QuizAttempt
from ...models.achievement import UserAchievement
from ...schemas.learning import (
    LearningProfileResponse,
    RecommendationResponse,
    KnowledgeGapResponse,
    LearningPathRequest,
    LearningPathResponse,
    NextStepsResponse,
    LearningProfile,
    Recommendation,
    KnowledgeGap,
    LearningPath,
    NextStep
)
from ...core.auth import get_current_user
from ...config import get_settings
settings = get_settings()
from ...core.llm_gateway import llm_gateway
from ...core.cache import cache
from ...database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/learning", tags=["learning"])

# Tier access control
TIER_ACCESS = {
    "free": [],
    "premium": ["profile_basic", "recommendations_basic", "next_steps_basic"],
    "pro": ["profile", "recommendations", "knowledge_gaps", "learning_path", "next_steps"],
    "team": ["profile", "recommendations", "knowledge_gaps", "learning_path", "next_steps", "team_insights"]
}

def check_feature_access(user_tier: str, feature: str) -> bool:
    """Check if user tier has access to feature."""
    return feature in TIER_ACCESS.get(user_tier, [])

async def gather_user_learning_data(user_id: str) -> dict:
    """Gather all learning data for a user."""
    # This would query the database for user's progress, quiz scores, etc.
    # For now, returning mock data
    from ...models.user import User
    from ...models.progress import ChapterProgress, QuizAttempt
    
    # In a real implementation, this would query the database
    # For now, returning mock data
    return {
        "user_id": user_id,
        "chapters_completed": 5,
        "chapters_total": 9,
        "quiz_scores": {
            "ch1-intro-to-agents": 90,
            "ch2-claude-agent-sdk": 85,
            "ch3-mcp-integration": 75,
            "ch4-skill-md-structure": 80,
            "ch5-procedural-knowledge": 70
        },
        "time_spent": {
            "ch1-intro-to-agents": 25,
            "ch2-claude-agent-sdk": 35,
            "ch3-mcp-integration": 40,
            "ch4-skill-md-structure": 30,
            "ch5-procedural-knowledge": 45
        },
        "session_history": [
            {"date": "2026-01-18", "duration": 32, "activity": "chapter", "chapter_id": "ch5-procedural-knowledge"},
            {"date": "2026-01-17", "duration": 15, "activity": "quiz", "quiz_id": "quiz-ch4-practice", "score": 70}
        ],
        "practice_completion": {
            "ch4-exercise-1": True,
            "ch4-exercise-2": False,
            "ch5-exercise-1": True
        }
    }

def generate_rule_based_profile(user_data: dict) -> dict:
    """Generate learning profile using rule-based logic."""
    # Calculate learning pace
    chapters_completed = user_data.get("chapters_completed", 0)
    session_history = user_data.get("session_history", [])
    
    # Estimate pace based on recent activity
    recent_sessions = [s for s in session_history if 
                      datetime.fromisoformat(s["date"].replace("Z", "+00:00")) > 
                      datetime.now() - timedelta(days=7)]
    
    chapters_per_week = len(recent_sessions) if recent_sessions else 1
    avg_session_minutes = sum(s["duration"] for s in recent_sessions) / len(recent_sessions) if recent_sessions else 25
    
    # Determine pace category
    pace_category = "moderate"
    if chapters_per_week > 3:
        pace_category = "intensive"
    elif chapters_per_week > 1.5:
        pace_category = "fast"
    elif chapters_per_week < 1:
        pace_category = "slow"
    
    # Determine learning style based on engagement
    practice_completion = user_data.get("practice_completion", {})
    practice_completed = sum(1 for v in practice_completion.values() if v)
    practice_total = len(practice_completion)
    
    learning_style = "reading"
    if practice_total > 0 and practice_completed / practice_total > 0.6:
        learning_style = "hands_on"
    
    # Identify strengths and weaknesses based on quiz scores
    quiz_scores = user_data.get("quiz_scores", {})
    strengths = []
    weaknesses = []
    
    for chapter_id, score in quiz_scores.items():
        topic = chapter_id.replace("-", " ").replace("ch", "").title()
        assessment = {
            "topic": topic,
            "chapter_id": chapter_id,
            "confidence_score": score,
            "evidence": f"Quiz score {score}%"
        }
        
        if score >= 80:
            strengths.append(assessment)
        elif score < 60:
            weaknesses.append(assessment)
    
    # Calculate overall progress
    chapters_total = user_data.get("chapters_total", 9)
    completion_percentage = int((chapters_completed / chapters_total) * 100)
    
    return {
        "user_id": user_data["user_id"],
        "profile": {
            "learning_pace": {
                "category": pace_category,
                "chapters_per_week": chapters_per_week,
                "avg_session_minutes": avg_session_minutes,
                "preferred_session_times": ["evening", "weekend"],
                "consistency_score": 75
            },
            "learning_style": {
                "primary": learning_style,
                "secondary": "unknown",
                "preferences": {
                    "prefers_examples": True,
                    "prefers_theory_first": False,
                    "prefers_practice_exercises": learning_style == "hands_on",
                    "reading_vs_video": "reading"
                }
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "overall_progress": {
                "chapters_completed": chapters_completed,
                "chapters_total": chapters_total,
                "completion_percentage": completion_percentage,
                "estimated_completion_date": "2026-02-15",
                "current_streak_days": 4
            }
        },
        "ai_insights": None,
        "generated_by": "rule_engine"
    }

async def generate_llm_profile(user_id: str, user_data: dict) -> dict:
    """Generate learning profile using Claude Sonnet 4."""
    # Check token budget
    # In a real implementation, we would check the user's token budget here
    # For now, we'll proceed assuming budget is available
    
    # Build prompt for Claude
    prompt = f"""
You are an expert learning analyst for an AI Agents course. Analyze the following learner data and provide insights.

## Learner Data
- User ID: {user_data['user_id']}
- Course Progress: {user_data['chapters_completed']}/{user_data['chapters_total']} chapters
- Quiz Scores: {json.dumps(user_data['quiz_scores'])}
- Session History: {json.dumps(user_data['session_history'])}
- Time on Chapters: {json.dumps(user_data['time_spent'])}
- Practice Exercise Completion: {json.dumps(user_data['practice_completion'])}

## Your Task
Analyze this learner's profile and provide:

1. **Learning Pace Assessment** (slow/moderate/fast/intensive)
   - Base on chapters per week, session frequency, time spent

2. **Learning Style Detection** (visual/auditory/reading/hands_on)
   - Infer from content engagement patterns, quiz performance on different question types

3. **Strengths** (list 2-3 topics with evidence)
   - Topics with high quiz scores (>80%), fast completion, good retention

4. **Weaknesses** (list 2-3 topics with evidence and recommendations)
   - Topics with low scores (<70%), slow progress, multiple attempts

5. **Personalized Summary** (2-3 sentences)
   - Encouraging, specific, actionable

6. **Personalized Tips** (3 bullet points)
   - Specific to this learner's patterns

Respond in JSON format matching the LearningProfile schema.
"""
    
    # Call Claude API
    try:
        response = await llm_gateway.generate(prompt, model="claude-sonnet-4")
        # Parse the response and return as profile
        # For now, returning mock data based on the prompt
        profile = generate_rule_based_profile(user_data)
        profile["ai_insights"] = {
            "generated_by": "claude-sonnet-4",
            "generated_at": datetime.utcnow().isoformat(),
            "summary": "You're making steady progress with a methodical approach. Your strength lies in SDK fundamentals, but you may benefit from more practice with distributed system concepts before tackling multi-agent patterns.",
            "personalized_tips": [
                "Consider reviewing orchestration patterns (ch7) before multi-agent systems",
                "Your evening study sessions are most productive - try to maintain this schedule",
                "You learn best from code examples - use the interactive exercises more"
            ]
        }
        profile["generated_by"] = "claude-sonnet-4"
        return profile
    except Exception as e:
        # Fallback to rule-based if LLM fails
        print(f"LLM profile generation failed: {e}")
        return generate_rule_based_profile(user_data)

@router.get("/profile/{user_id}", response_model=LearningProfileResponse)
async def get_learning_profile(
    user_id: str,
    include_history: bool = Query(False, description="Include recent learning history"),
    refresh: bool = Query(False, description="Force recalculation (bypass cache)"),
    user: User = Depends(get_current_user)
):
    """
    Get user learning profile with AI insights.

    Access Control:
    - Free: No access
    - Premium: Basic profile (rule-based)
    - Pro/Team: Full profile (LLM-enhanced)
    """
    # Verify user can access this profile
    if user.id != user_id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    tier = getattr(user, 'tier', 'free')

    # Free tier - no access
    if tier == "free":
        raise HTTPException(
            status_code=403,
            detail={
                "error": "feature_not_available",
                "message": "Learning profiles are available for Premium and Pro subscribers",
                "required_tier": "premium",
                "upgrade_url": "/api/v1/pricing"
            }
        )

    # Check cache unless refresh requested
    if not refresh:
        cached = await cache.get(f"adaptive:profile:{user_id}")
        if cached:
            cached_data = json.loads(cached)
            if cached_data.get("expires_at") and datetime.fromisoformat(cached_data["expires_at"].replace("Z", "+00:00")) > datetime.utcnow():
                return {**cached_data, "cached": True}

    # Get user data for analysis
    user_data = await gather_user_learning_data(user_id)

    # Premium tier - rule-based basic profile
    if tier == "premium":
        profile = generate_rule_based_profile(user_data)
        profile["upgrade_prompt"] = {
            "message": "Upgrade to Pro for AI-powered learning insights and personalized study plans",
            "features": ["Detailed learning style analysis", "Personalized study tips", "Knowledge gap detection"],
            "url": "/api/v1/pricing/pro"
        }
        return profile

    # Pro/Team tier - LLM-enhanced profile
    try:
        profile = await generate_llm_profile(user_id, user_data)

        # Cache the result
        cache_data = {
            **profile,
            "expires_at": (datetime.utcnow() + timedelta(hours=4)).isoformat()
        }
        await cache.set(f"adaptive:profile:{user_id}", json.dumps(cache_data), ex=14400)

        return {**profile, "cached": False}

    except Exception as e:
        print(f"LLM profile generation failed: {e}")
        # Fallback to rule-based
        profile = generate_rule_based_profile(user_data)
        profile["fallback"] = True
        profile["fallback_reason"] = "AI service temporarily unavailable"
        return profile

@router.get("/recommendations/{user_id}", response_model=RecommendationResponse)
async def get_recommendations(
    user_id: str,
    limit: int = Query(5, ge=1, le=10, description="Maximum recommendations to return"),
    type_filter: Optional[str] = Query(None, description="Filter by type: chapter, quiz, practice, review"),
    context: Optional[str] = Query(None, description="Current context: morning_session, evening_session, quick_review, deep_study"),
    user: User = Depends(get_current_user)
):
    """
    Get AI-generated content recommendations based on user profile and progress.

    Access Control:
    - Free: No access
    - Premium: Basic recommendations (rule-based)
    - Pro/Team: Full recommendations (LLM-enhanced)
    """
    # Verify user can access this profile
    if user.id != user_id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    tier = getattr(user, 'tier', 'free')

    # Free tier - no access
    if tier == "free":
        raise HTTPException(
            status_code=403,
            detail={
                "error": "feature_not_available",
                "message": "Recommendations are available for Premium and Pro subscribers",
                "required_tier": "premium",
                "upgrade_url": "/api/v1/pricing"
            }
        )

    # Check cache unless context is different
    cache_key = f"adaptive:recs:{user_id}:{context or 'default'}"
    cached = await cache.get(cache_key)
    if cached:
        cached_data = json.loads(cached)
        if cached_data.get("expires_at") and datetime.fromisoformat(cached_data["expires_at"].replace("Z", "+00:00")) > datetime.utcnow():
            return {**cached_data, "cached": True}

    # Get user data for analysis
    user_data = await gather_user_learning_data(user_id)

    # Premium tier - rule-based recommendations
    if tier == "premium":
        recommendations = []
        
        # Rule 1: Next chapter in sequence
        next_chapter_id = f"ch{user_data['chapters_completed'] + 1}-next-chapter"
        recommendations.append({
            "id": f"rec-rule-{next_chapter_id}",
            "type": "chapter",
            "content_id": next_chapter_id,
            "title": f"Chapter {user_data['chapters_completed'] + 1} Content",
            "priority": "high",
            "reason": "Next chapter in sequence",
            "estimated_time_minutes": 30,
            "confidence": 1.0,
            "tags": ["next_in_sequence"]
        })

        # Rule 2: Low quiz scores need review
        low_scores = {k: v for k, v in user_data['quiz_scores'].items() if v < 60}
        for chapter_id, score in list(low_scores.items())[:2]:
            recommendations.append({
                "id": f"rec-rule-review-{chapter_id}",
                "type": "review",
                "content_id": chapter_id,
                "title": f"Review: {chapter_id.replace('-', ' ').title()}",
                "priority": "medium",
                "reason": f"Quiz score {score}% - review recommended",
                "estimated_time_minutes": 15,
                "confidence": 1.0,
                "tags": ["low_score_review"]
            })

        result = {
            "user_id": user_id,
            "recommendations": recommendations[:limit],
            "generated_by": "rule_engine",
            "upgrade_prompt": {
                "message": "Upgrade to Pro for AI-powered personalized recommendations",
                "url": "/api/v1/pricing/pro"
            }
        }
        return result

    # Pro/Team tier - LLM-enhanced recommendations
    try:
        # Build prompt for Claude
        prompt = f"""
You are an expert learning recommender for an AI Agents course. Based on the user's progress, suggest relevant content.

## User Data
- User ID: {user_data['user_id']}
- Progress: {user_data['chapters_completed']}/{user_data['chapters_total']} chapters
- Quiz Scores: {json.dumps(user_data['quiz_scores'])}
- Context: {context or 'general'}

## Your Task
Generate up to {limit} personalized recommendations that would be most beneficial for this learner right now.

Consider:
- Their strengths and weaknesses
- What they should learn next
- What they might need to review
- Their learning context ({context})

Format as JSON with recommendations.
"""
        
        # Call Claude API
        response = await llm_gateway.generate(prompt, model="claude-sonnet-4")
        
        # For now, return mock data based on the prompt
        recommendations = [
            {
                "id": "rec-001",
                "type": "chapter",
                "content_id": "ch6-runtime-skills",
                "title": "Runtime Skills and Dynamic Loading",
                "priority": "high",
                "reason": "This chapter builds directly on your strong SDK foundation and prepares you for orchestration patterns",
                "estimated_time_minutes": 35,
                "difficulty_match": "appropriate",
                "prerequisites_met": True,
                "confidence": 0.92,
                "tags": ["next_in_sequence", "skill_building"]
            },
            {
                "id": "rec-002",
                "type": "review",
                "content_id": "ch3-mcp-integration",
                "title": "Review: MCP Integration",
                "priority": "medium",
                "reason": "Your quiz score of 75% suggests some concepts may need reinforcement before proceeding",
                "estimated_time_minutes": 15,
                "focus_areas": ["MCP server configuration", "Tool definitions"],
                "confidence": 0.85,
                "tags": ["reinforcement", "weakness_area"]
            }
        ]
        
        result = {
            "user_id": user_id,
            "recommendations": recommendations[:limit],
            "session_context": {
                "context": context or "general",
                "recommended_duration_minutes": 45,
                "focus_suggestion": "This is typically your most productive time. Consider tackling the ch6 chapter for deeper learning."
            },
            "generated_by": "claude-sonnet-4",
            "generated_at": datetime.utcnow().isoformat(),
            "cache_key": cache_key,
            "cached": False,
            "cache_expires_at": (datetime.utcnow() + timedelta(hours=2)).isoformat()
        }
        
        # Cache the result
        cache_data = {k: v for k, v in result.items() if k != 'cached'}
        await cache.set(cache_key, json.dumps(cache_data), ex=7200)
        
        return result

    except Exception as e:
        print(f"LLM recommendations generation failed: {e}")
        # Fallback to rule-based
        recommendations = []
        
        # Rule 1: Next chapter in sequence
        next_chapter_id = f"ch{user_data['chapters_completed'] + 1}-next-chapter"
        recommendations.append({
            "id": f"rec-rule-{next_chapter_id}",
            "type": "chapter",
            "content_id": next_chapter_id,
            "title": f"Chapter {user_data['chapters_completed'] + 1} Content",
            "priority": "high",
            "reason": "Next chapter in sequence",
            "estimated_time_minutes": 30,
            "confidence": 1.0,
            "tags": ["next_in_sequence"]
        })

        result = {
            "user_id": user_id,
            "recommendations": recommendations[:limit],
            "generated_by": "rule_engine",
            "fallback": True,
            "fallback_reason": "AI service temporarily unavailable"
        }
        return result

# Placeholder for other endpoints - will implement based on full spec
@router.get("/knowledge-gaps/{user_id}")
async def get_knowledge_gaps(
    user_id: str,
    depth: str = Query("detailed", description="Analysis depth: surface, detailed"),
    module: Optional[int] = Query(None, description="Focus on specific module"),
    user: User = Depends(get_current_user)
):
    """
    Get AI-powered knowledge gap analysis.
    
    Access Control:
    - Free/Premium: No access
    - Pro/Team: Full access
    """
    tier = getattr(user, 'tier', 'free')
    
    if tier not in ["pro", "team"]:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "feature_not_available",
                "message": "Knowledge gap analysis is a Pro feature",
                "required_tier": "pro",
                "upgrade_url": "/api/v1/pricing/pro",
                "feature_preview": {
                    "description": "AI-powered knowledge gap detection identifies hidden weaknesses and provides targeted remediation plans",
                    "benefits": [
                        "Find gaps you didn't know you had",
                        "Get personalized study plans",
                        "Improve retention with targeted review"
                    ]
                }
            }
        )
    
    # Mock response for now
    return {
        "user_id": user_id,
        "analysis_summary": {
            "total_gaps_identified": 2,
            "critical_gaps": 1,
            "moderate_gaps": 1,
            "overall_readiness": {
                "module_1": "strong",
                "module_2": "moderate", 
                "module_3": "needs_work"
            }
        },
        "knowledge_gaps": [
            {
                "id": "gap-001",
                "topic": "Multi-Agent Communication Protocols",
                "severity": "critical",
                "severity_score": 85,
                "affected_chapters": ["ch8-multi-agent-systems", "ch9-production-deployment"],
                "root_cause": {
                    "type": "prerequisite_gap",
                    "description": "Weak foundation in orchestration patterns affecting understanding of multi-agent coordination",
                    "evidence": ["Quiz ch7: 58% (below passing)"]
                },
                "recommended_content": [
                    {
                        "content_id": "ch7-orchestration-patterns",
                        "type": "review",
                        "priority": "high",
                        "focus_sections": ["Agent coordination", "Message passing patterns"],
                        "estimated_time_minutes": 25
                    }
                ],
                "impact_if_unaddressed": "Will struggle significantly with Modules 3 content"
            }
        ],
        "remediation_plan": {
            "estimated_total_time_minutes": 50,
            "suggested_order": ["gap-001"],
            "schedule_suggestion": "Focus on gap-001 in your next session"
        },
        "generated_by": "claude-sonnet-4",
        "generated_at": datetime.utcnow().isoformat(),
        "analysis_depth": depth
    }

@router.post("/path/generate", response_model=LearningPathResponse)
async def generate_learning_path(
    request: LearningPathRequest,
    user: User = Depends(get_current_user)
):
    """
    Generate a personalized learning path based on user goals and constraints.
    
    Access Control:
    - Free/Premium: No access
    - Pro/Team: Full access
    """
    tier = getattr(user, 'tier', 'free')
    
    if tier not in ["pro", "team"]:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "feature_not_available",
                "message": "Learning path generation is a Pro feature",
                "required_tier": "pro",
                "upgrade_url": "/api/v1/pricing/pro"
            }
        )
    
    # Mock response for now
    return {
        "path_id": f"path-{uuid.uuid4()}",
        "user_id": request.user_id,
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {
            "total_duration_hours": 18.5,
            "total_sessions": 24,
            "estimated_completion_date": "2026-02-25",
            "target_date": request.goal.target_date,
            "buffer_days": 3,
            "feasibility": "achievable",
            "confidence": 0.85
        },
        "learning_path": {
            "phases": [
                {
                    "phase_number": 1,
                    "name": "Foundation Reinforcement",
                    "description": "Address knowledge gaps before proceeding",
                    "duration_days": 7,
                    "start_date": "2026-01-20",
                    "end_date": "2026-01-26",
                    "steps": [
                        {
                            "step_id": "step-001",
                            "order": 1,
                            "type": "review",
                            "content_id": "ch7-orchestration-patterns",
                            "title": "Review: Orchestration Patterns",
                            "description": "Strengthen foundation in agent coordination",
                            "duration_minutes": 25,
                            "scheduled_date": "2026-01-21",
                            "priority": "critical"
                        }
                    ]
                }
            ],
            "milestones": [
                {
                    "milestone_id": "ms-001",
                    "name": "Foundation Complete",
                    "target_date": "2026-01-26",
                    "requirements": ["step-001"],
                    "reward": "Foundation Mastery Badge"
                }
            ]
        },
        "personalization_factors": {
            "learning_pace_adjustment": "Slightly accelerated based on your history",
            "style_accommodations": "Included extra hands-on exercises based on your preference",
            "gap_remediation": "Added Phase 1 to address identified gaps",
            "schedule_optimization": "Sessions scheduled for your preferred evening times"
        },
        "ai_notes": {
            "generated_by": "claude-sonnet-4",
            "rationale": "This path prioritizes addressing your orchestration patterns gap first, as it's critical for multi-agent systems understanding.",
            "alternative_approaches": [
                "Faster track (16 hours, no review): Achievable but higher risk of retention issues"
            ]
        },
        "actions": {
            "save_path": f"/api/v1/learning/path/{uuid.uuid4()}/save",
            "modify_path": f"/api/v1/learning/path/{uuid.uuid4()}/modify",
            "start_path": f"/api/v1/learning/path/{uuid.uuid4()}/start"
        }
    }

@router.get("/next-steps/{user_id}")
async def get_next_steps(
    user_id: str,
    available_minutes: int = Query(30, description="Time available for current session"),
    mood: str = Query("focused", description="Current learning mood: focused, casual, quick_review, challenge_me"),
    user: User = Depends(get_current_user)
):
    """
    Get immediate next actions for the user's current session.
    
    Access Control:
    - Free: No access
    - Premium: Basic next steps (rule-based)
    - Pro/Team: Full next steps (LLM-enhanced)
    """
    tier = getattr(user, 'tier', 'free')
    
    if tier == "free":
        raise HTTPException(
            status_code=403,
            detail={
                "error": "feature_not_available",
                "message": "Next steps are available for Premium and Pro subscribers",
                "required_tier": "premium",
                "upgrade_url": "/api/v1/pricing"
            }
        )
    
    # Mock response for now
    if tier == "premium":
        return {
            "user_id": user_id,
            "session_context": {
                "available_minutes": available_minutes,
                "mood": mood
            },
            "next_steps": [
                {
                    "step_number": 1,
                    "action": "start_chapter",
                    "content_id": f"ch{5 + 1}-next-chapter",  # Next chapter after completed
                    "title": f"Next: Chapter {5 + 1}",
                    "description": "Continue with the next chapter in sequence",
                    "duration_minutes": 30,
                    "reason": "Next chapter in your learning sequence",
                    "cta": "Start Chapter"
                }
            ],
            "generated_by": "rule_engine",
            "upgrade_prompt": {
                "message": "Get personalized next steps with AI-powered recommendations",
                "url": "/api/v1/pricing/pro"
            }
        }
    else:  # Pro/Team
        return {
            "user_id": user_id,
            "session_context": {
                "available_minutes": available_minutes,
                "mood": mood,
                "current_time": datetime.utcnow().isoformat(),
                "session_type": "evening_deep_study"
            },
            "next_steps": [
                {
                    "step_number": 1,
                    "action": "start_chapter",
                    "content_id": "ch6-runtime-skills",
                    "title": "Continue: Runtime Skills",
                    "description": "Pick up where you left off in section 2.3",
                    "duration_minutes": 25,
                    "reason": "Optimal for focused evening session - builds on your SDK strength",
                    "progress": {
                        "current_section": "2.3",
                        "sections_remaining": 3,
                        "estimated_completion": "2 sessions"
                    },
                    "cta": "Continue Reading"
                }
            ],
            "alternative_paths": [
                {
                    "mood": "quick_review",
                    "description": "Short 15-min review session instead",
                    "steps": ["Review ch5 key concepts", "Flashcard practice"]
                }
            ],
            "motivational_context": {
                "streak_status": "4 days - keep it going!",
                "achievement_progress": "2 more chapters for 'Consistent Learner' badge",
                "personalized_message": "Your evening sessions are your most productive. Great time for focused chapter work."
            },
            "generated_by": "claude-sonnet-4",
            "generated_at": datetime.utcnow().isoformat()
        }