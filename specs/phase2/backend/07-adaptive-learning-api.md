# Backend API Specification: Adaptive Learning
## Phase 2 - LLM-Enhanced Personalization

**API Version:** 2.0
**Responsibility:** Provide personalized learning paths and recommendations via Claude Sonnet 4
**Intelligence Level:** LLM-ENHANCED (Claude Sonnet 4 for personalization, with rule-based fallbacks)

---

## Overview

The Adaptive Learning API provides personalized learning experiences by analyzing user progress, identifying knowledge gaps, and generating tailored learning paths. This Phase 2 feature leverages Claude Sonnet 4 to deliver intelligent recommendations while maintaining cost efficiency through strategic caching and rule-based fallbacks.

### Key Capabilities

1. **Learning Profile Analysis** - Understand user learning patterns, pace, and preferences
2. **Knowledge Gap Detection** - Identify areas where users struggle or have incomplete understanding
3. **Personalized Recommendations** - AI-generated content suggestions based on user context
4. **Dynamic Learning Paths** - Custom curriculum generation adapted to individual needs
5. **Next Steps Guidance** - Actionable recommendations for immediate learning focus

---

## Constitutional Compliance (Phase 2)

**ALLOWED:** LLM-powered personalization for Pro tier users
**ALLOWED:** Caching LLM responses for efficiency
**ALLOWED:** Rule-based fallbacks when LLM unavailable
**REQUIRED:** Token budget enforcement per user/session
**REQUIRED:** Graceful degradation to deterministic recommendations

**Reference:** `specs/phase2/constitution/02-LLM-USAGE-RULES.md`

---

## Access Control by Tier

| Tier | Learning Profile | Recommendations | Knowledge Gaps | Learning Path | Next Steps |
|------|-----------------|-----------------|----------------|---------------|------------|
| **Free** | No access | No access | No access | No access | No access |
| **Premium** | Basic (rule-based) | Basic (rule-based) | No access | No access | Basic (rule-based) |
| **Pro** | Full (LLM-enhanced) | Full (LLM-enhanced) | Full (LLM-enhanced) | Full (LLM-enhanced) | Full (LLM-enhanced) |
| **Team** | Full + Team insights | Full + Team insights | Full + Team insights | Full + Team insights | Full + Team insights |

---

## API Endpoints

### 1. Get User Learning Profile

**Endpoint:** `GET /api/v1/learning/profile/{user_id}`

**Purpose:** Retrieve comprehensive learning profile with pace, style, strengths, and weaknesses

**Path Parameters:**
- `user_id` (string, required): User identifier

**Query Parameters:**
- `include_history` (boolean, optional): Include recent learning history (default: false)
- `refresh` (boolean, optional): Force recalculation (bypass cache, default: false)

**Request Example:**
```http
GET /api/v1/learning/profile/user-123?include_history=true
Authorization: Bearer <user_token>
```

**Response 200 (Pro Tier - LLM Enhanced):**
```json
{
  "user_id": "user-123",
  "profile": {
    "learning_pace": {
      "category": "moderate",
      "chapters_per_week": 2.3,
      "avg_session_minutes": 25,
      "preferred_session_times": ["evening", "weekend"],
      "consistency_score": 78
    },
    "learning_style": {
      "primary": "visual",
      "secondary": "hands_on",
      "preferences": {
        "prefers_examples": true,
        "prefers_theory_first": false,
        "prefers_practice_exercises": true,
        "reading_vs_video": "reading"
      }
    },
    "strengths": [
      {
        "topic": "Claude Agent SDK",
        "chapter_id": "ch2-claude-agent-sdk",
        "confidence_score": 92,
        "evidence": "Scored 95% on chapter quiz, completed 3 practice exercises"
      },
      {
        "topic": "MCP Integration Basics",
        "chapter_id": "ch3-mcp-integration",
        "confidence_score": 85,
        "evidence": "Completed chapter quickly with high retention"
      }
    ],
    "weaknesses": [
      {
        "topic": "Multi-Agent Communication Patterns",
        "chapter_id": "ch8-multi-agent-systems",
        "confidence_score": 45,
        "evidence": "Quiz score 55%, multiple retakes, slow progress",
        "recommended_action": "Review prerequisite ch7 before continuing"
      },
      {
        "topic": "Production Deployment Strategies",
        "chapter_id": "ch9-production-deployment",
        "confidence_score": 30,
        "evidence": "Chapter not started, prerequisite gaps detected"
      }
    ],
    "overall_progress": {
      "chapters_completed": 5,
      "chapters_total": 9,
      "completion_percentage": 56,
      "estimated_completion_date": "2026-02-15",
      "current_streak_days": 4
    }
  },
  "learning_history": [
    {
      "date": "2026-01-18",
      "activity": "chapter_completed",
      "chapter_id": "ch5-procedural-knowledge",
      "duration_minutes": 32,
      "quiz_score": 85
    },
    {
      "date": "2026-01-17",
      "activity": "quiz_attempt",
      "quiz_id": "quiz-ch4-practice",
      "score": 70,
      "duration_minutes": 15
    }
  ],
  "ai_insights": {
    "generated_by": "claude-sonnet-4",
    "generated_at": "2026-01-19T10:30:00Z",
    "summary": "You're making steady progress with a methodical approach. Your strength lies in SDK fundamentals, but you may benefit from more practice with distributed system concepts before tackling multi-agent patterns.",
    "personalized_tips": [
      "Consider reviewing orchestration patterns (ch7) before multi-agent systems",
      "Your evening study sessions are most productive - try to maintain this schedule",
      "You learn best from code examples - use the interactive exercises more"
    ]
  },
  "cached": false,
  "cache_expires_at": "2026-01-19T22:30:00Z"
}
```

**Response 200 (Premium Tier - Rule-Based):**
```json
{
  "user_id": "user-456",
  "profile": {
    "learning_pace": {
      "category": "moderate",
      "chapters_per_week": 1.8,
      "avg_session_minutes": 20,
      "consistency_score": 65
    },
    "learning_style": {
      "primary": "unknown",
      "note": "Upgrade to Pro for AI-powered learning style analysis"
    },
    "strengths": [
      {
        "topic": "Introduction to AI Agents",
        "chapter_id": "ch1-intro-to-agents",
        "confidence_score": 88,
        "evidence": "Quiz score 88%"
      }
    ],
    "weaknesses": [
      {
        "topic": "MCP Integration",
        "chapter_id": "ch3-mcp-integration",
        "confidence_score": 52,
        "evidence": "Quiz score 52%"
      }
    ],
    "overall_progress": {
      "chapters_completed": 3,
      "chapters_total": 9,
      "completion_percentage": 33
    }
  },
  "ai_insights": null,
  "upgrade_prompt": {
    "message": "Upgrade to Pro for AI-powered learning insights and personalized study plans",
    "features": ["Detailed learning style analysis", "Personalized study tips", "Knowledge gap detection"],
    "url": "/api/v1/pricing/pro"
  }
}
```

**Response 403 (Free Tier):**
```json
{
  "error": "feature_not_available",
  "message": "Learning profiles are available for Premium and Pro subscribers",
  "required_tier": "premium",
  "upgrade_url": "/api/v1/pricing"
}
```

---

### 2. Get Personalized Recommendations

**Endpoint:** `GET /api/v1/learning/recommendations/{user_id}`

**Purpose:** Get AI-generated content recommendations based on user profile and progress

**Path Parameters:**
- `user_id` (string, required): User identifier

**Query Parameters:**
- `limit` (integer, optional): Maximum recommendations to return (default: 5, max: 10)
- `type` (string, optional): Filter by type: `chapter`, `quiz`, `practice`, `review` (default: all)
- `context` (string, optional): Current context: `morning_session`, `evening_session`, `quick_review`, `deep_study`

**Request Example:**
```http
GET /api/v1/learning/recommendations/user-123?limit=5&context=evening_session
Authorization: Bearer <user_token>
```

**Response 200 (Pro Tier):**
```json
{
  "user_id": "user-123",
  "recommendations": [
    {
      "id": "rec-001",
      "type": "chapter",
      "content_id": "ch6-runtime-skills",
      "title": "Runtime Skills and Dynamic Loading",
      "priority": "high",
      "reason": "This chapter builds directly on your strong SDK foundation and prepares you for orchestration patterns",
      "estimated_time_minutes": 35,
      "difficulty_match": "appropriate",
      "prerequisites_met": true,
      "confidence": 0.92,
      "tags": ["next_in_sequence", "skill_building"]
    },
    {
      "id": "rec-002",
      "type": "review",
      "content_id": "ch3-mcp-integration",
      "title": "Review: MCP Integration",
      "priority": "medium",
      "reason": "Your quiz score of 55% suggests some concepts may need reinforcement before proceeding",
      "estimated_time_minutes": 15,
      "focus_areas": ["MCP server configuration", "Tool definitions"],
      "confidence": 0.85,
      "tags": ["reinforcement", "weakness_area"]
    },
    {
      "id": "rec-003",
      "type": "practice",
      "content_id": "practice-ch5-01",
      "title": "Procedural Knowledge Exercise Set",
      "priority": "medium",
      "reason": "Hands-on practice aligns with your learning style preference",
      "estimated_time_minutes": 20,
      "confidence": 0.88,
      "tags": ["hands_on", "style_match"]
    },
    {
      "id": "rec-004",
      "type": "quiz",
      "content_id": "quiz-ch4-retry",
      "title": "Skill.md Structure Assessment (Retry)",
      "priority": "low",
      "reason": "Optional retake to improve your score from 70% to unlock achievement",
      "estimated_time_minutes": 10,
      "potential_achievement": "Perfect Score Badge",
      "confidence": 0.75,
      "tags": ["achievement_opportunity"]
    },
    {
      "id": "rec-005",
      "type": "chapter",
      "content_id": "ch7-orchestration-patterns",
      "title": "Orchestration Patterns",
      "priority": "low",
      "reason": "Preview content - complete ch6 first for optimal learning sequence",
      "estimated_time_minutes": 45,
      "prerequisites_met": false,
      "missing_prerequisites": ["ch6-runtime-skills"],
      "confidence": 0.70,
      "tags": ["preview", "future_content"]
    }
  ],
  "session_context": {
    "context": "evening_session",
    "recommended_duration_minutes": 45,
    "focus_suggestion": "This is typically your most productive time. Consider tackling the ch6 chapter for deeper learning."
  },
  "generated_by": "claude-sonnet-4",
  "generated_at": "2026-01-19T18:30:00Z",
  "cache_key": "rec-user123-evening-v2",
  "cached": false,
  "cache_expires_at": "2026-01-19T22:30:00Z"
}
```

**Response 200 (Premium Tier - Rule-Based):**
```json
{
  "user_id": "user-456",
  "recommendations": [
    {
      "id": "rec-001",
      "type": "chapter",
      "content_id": "ch4-skill-md-structure",
      "title": "Skill.md Structure",
      "priority": "high",
      "reason": "Next chapter in sequence",
      "estimated_time_minutes": 30,
      "prerequisites_met": true,
      "confidence": 1.0,
      "tags": ["next_in_sequence"]
    },
    {
      "id": "rec-002",
      "type": "review",
      "content_id": "ch3-mcp-integration",
      "title": "Review: MCP Integration",
      "priority": "medium",
      "reason": "Quiz score below 60% - review recommended",
      "estimated_time_minutes": 15,
      "confidence": 1.0,
      "tags": ["low_score_review"]
    }
  ],
  "generated_by": "rule_engine",
  "upgrade_prompt": {
    "message": "Upgrade to Pro for AI-powered personalized recommendations",
    "url": "/api/v1/pricing/pro"
  }
}
```

---

### 3. Identify Knowledge Gaps

**Endpoint:** `GET /api/v1/learning/knowledge-gaps/{user_id}`

**Purpose:** AI-powered analysis of knowledge gaps and missing prerequisites

**Path Parameters:**
- `user_id` (string, required): User identifier

**Query Parameters:**
- `depth` (string, optional): Analysis depth: `surface`, `detailed` (default: detailed)
- `module` (integer, optional): Focus on specific module

**Request Example:**
```http
GET /api/v1/learning/knowledge-gaps/user-123?depth=detailed
Authorization: Bearer <user_token>
```

**Response 200 (Pro Tier):**
```json
{
  "user_id": "user-123",
  "analysis_summary": {
    "total_gaps_identified": 4,
    "critical_gaps": 1,
    "moderate_gaps": 2,
    "minor_gaps": 1,
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
        "description": "Weak foundation in orchestration patterns (ch7) affecting understanding of multi-agent coordination",
        "evidence": [
          "Quiz ch7: 58% (below passing)",
          "Time on ch7: 18min (avg: 35min for this chapter)",
          "Skipped 3 practice exercises"
        ]
      },
      "recommended_content": [
        {
          "content_id": "ch7-orchestration-patterns",
          "type": "review",
          "priority": "high",
          "focus_sections": ["Agent coordination", "Message passing patterns", "State management"],
          "estimated_time_minutes": 25
        },
        {
          "content_id": "practice-ch7-01",
          "type": "practice",
          "priority": "high",
          "description": "Orchestration hands-on exercises",
          "estimated_time_minutes": 30
        }
      ],
      "impact_if_unaddressed": "Will struggle significantly with Modules 3 content and production deployment concepts"
    },
    {
      "id": "gap-002",
      "topic": "MCP Server Configuration",
      "severity": "moderate",
      "severity_score": 60,
      "affected_chapters": ["ch6-runtime-skills"],
      "root_cause": {
        "type": "incomplete_understanding",
        "description": "Partial grasp of MCP server setup - understood basic concepts but missed configuration details",
        "evidence": [
          "Quiz ch3 section 2: 45%",
          "Correct on theory, incorrect on implementation questions"
        ]
      },
      "recommended_content": [
        {
          "content_id": "ch3-mcp-integration",
          "type": "focused_review",
          "priority": "medium",
          "focus_sections": ["Server configuration", "Environment setup"],
          "estimated_time_minutes": 15
        }
      ],
      "impact_if_unaddressed": "May face implementation challenges in runtime skills chapter"
    },
    {
      "id": "gap-003",
      "topic": "Error Handling in Agent Workflows",
      "severity": "moderate",
      "severity_score": 55,
      "affected_chapters": ["ch7-orchestration-patterns", "ch9-production-deployment"],
      "root_cause": {
        "type": "topic_not_encountered",
        "description": "Haven't yet reached the chapters covering this topic in depth",
        "evidence": [
          "Chapter ch7 not started",
          "Related quiz questions not attempted"
        ]
      },
      "recommended_content": [
        {
          "content_id": "ch7-orchestration-patterns",
          "type": "chapter",
          "priority": "medium",
          "focus_sections": ["Error recovery patterns", "Retry strategies"],
          "estimated_time_minutes": 40
        }
      ],
      "impact_if_unaddressed": "Natural progression - will be addressed as you continue the course"
    },
    {
      "id": "gap-004",
      "topic": "SDK Authentication Methods",
      "severity": "minor",
      "severity_score": 30,
      "affected_chapters": ["ch9-production-deployment"],
      "root_cause": {
        "type": "partial_coverage",
        "description": "Basic understanding present but advanced auth patterns not yet covered",
        "evidence": [
          "Quiz ch2: 95% but auth section: 75%"
        ]
      },
      "recommended_content": [
        {
          "content_id": "ch2-claude-agent-sdk",
          "type": "focused_review",
          "priority": "low",
          "focus_sections": ["API key management", "OAuth integration"],
          "estimated_time_minutes": 10
        }
      ],
      "impact_if_unaddressed": "Minor - will be reinforced in production deployment chapter"
    }
  ],
  "remediation_plan": {
    "estimated_total_time_minutes": 120,
    "suggested_order": ["gap-001", "gap-002", "gap-003", "gap-004"],
    "schedule_suggestion": "Focus on gap-001 (critical) in your next 2 sessions, then address gap-002 before continuing with new content"
  },
  "generated_by": "claude-sonnet-4",
  "generated_at": "2026-01-19T10:30:00Z",
  "analysis_depth": "detailed"
}
```

**Response 403 (Premium or Free Tier):**
```json
{
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
```

---

### 4. Generate Personalized Learning Path

**Endpoint:** `POST /api/v1/learning/path/generate`

**Purpose:** Generate a custom learning path based on user goals and constraints

**Request Body:**
```json
{
  "user_id": "user-123",
  "goal": {
    "type": "complete_course",
    "target_date": "2026-02-28",
    "priority_topics": ["multi-agent-systems", "production-deployment"],
    "skip_topics": []
  },
  "constraints": {
    "available_hours_per_week": 5,
    "preferred_session_length_minutes": 30,
    "preferred_days": ["tuesday", "thursday", "saturday"],
    "learning_style_preference": "hands_on"
  },
  "options": {
    "include_review_sessions": true,
    "include_practice_exercises": true,
    "buffer_time_percent": 20
  }
}
```

**Request Example:**
```http
POST /api/v1/learning/path/generate
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "user_id": "user-123",
  "goal": {
    "type": "complete_course",
    "target_date": "2026-02-28"
  },
  "constraints": {
    "available_hours_per_week": 5,
    "preferred_session_length_minutes": 30
  }
}
```

**Response 201 (Pro Tier):**
```json
{
  "path_id": "path-abc123",
  "user_id": "user-123",
  "generated_at": "2026-01-19T10:30:00Z",
  "summary": {
    "total_duration_hours": 18.5,
    "total_sessions": 24,
    "estimated_completion_date": "2026-02-25",
    "target_date": "2026-02-28",
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
            "priority": "critical",
            "checkpoint": {
              "type": "quiz",
              "quiz_id": "quiz-ch7-review",
              "passing_score": 70
            }
          },
          {
            "step_id": "step-002",
            "order": 2,
            "type": "practice",
            "content_id": "practice-ch7-01",
            "title": "Orchestration Hands-on Exercises",
            "description": "Apply orchestration patterns in practice",
            "duration_minutes": 30,
            "scheduled_date": "2026-01-23",
            "priority": "high"
          },
          {
            "step_id": "step-003",
            "order": 3,
            "type": "review",
            "content_id": "ch3-mcp-integration",
            "title": "Quick Review: MCP Configuration",
            "description": "Reinforce MCP server setup knowledge",
            "duration_minutes": 15,
            "scheduled_date": "2026-01-25",
            "focus_sections": ["Server configuration"],
            "priority": "medium"
          }
        ]
      },
      {
        "phase_number": 2,
        "name": "Multi-Agent Systems Mastery",
        "description": "Deep dive into multi-agent architectures",
        "duration_days": 14,
        "start_date": "2026-01-27",
        "end_date": "2026-02-09",
        "steps": [
          {
            "step_id": "step-004",
            "order": 4,
            "type": "chapter",
            "content_id": "ch8-multi-agent-systems",
            "title": "Multi-Agent Systems",
            "description": "Core multi-agent concepts and patterns",
            "duration_minutes": 45,
            "scheduled_date": "2026-01-28",
            "priority": "high",
            "checkpoint": {
              "type": "quiz",
              "quiz_id": "quiz-ch8",
              "passing_score": 70
            }
          },
          {
            "step_id": "step-005",
            "order": 5,
            "type": "practice",
            "content_id": "practice-ch8-01",
            "title": "Multi-Agent Exercise: Agent Communication",
            "duration_minutes": 35,
            "scheduled_date": "2026-01-30",
            "priority": "high"
          },
          {
            "step_id": "step-006",
            "order": 6,
            "type": "practice",
            "content_id": "practice-ch8-02",
            "title": "Multi-Agent Exercise: Coordination Patterns",
            "duration_minutes": 35,
            "scheduled_date": "2026-02-01",
            "priority": "medium"
          },
          {
            "step_id": "step-007",
            "order": 7,
            "type": "review",
            "content_id": "ch8-multi-agent-systems",
            "title": "Chapter 8 Consolidation",
            "description": "Review and solidify multi-agent concepts",
            "duration_minutes": 20,
            "scheduled_date": "2026-02-04",
            "priority": "medium"
          }
        ]
      },
      {
        "phase_number": 3,
        "name": "Production Readiness",
        "description": "Complete course with production deployment",
        "duration_days": 14,
        "start_date": "2026-02-10",
        "end_date": "2026-02-25",
        "steps": [
          {
            "step_id": "step-008",
            "order": 8,
            "type": "chapter",
            "content_id": "ch9-production-deployment",
            "title": "Production Deployment",
            "description": "Learn to deploy agents to production",
            "duration_minutes": 50,
            "scheduled_date": "2026-02-11",
            "priority": "high",
            "checkpoint": {
              "type": "quiz",
              "quiz_id": "quiz-ch9",
              "passing_score": 70
            }
          },
          {
            "step_id": "step-009",
            "order": 9,
            "type": "practice",
            "content_id": "practice-ch9-01",
            "title": "Deployment Exercise: CI/CD Pipeline",
            "duration_minutes": 40,
            "scheduled_date": "2026-02-13",
            "priority": "high"
          },
          {
            "step_id": "step-010",
            "order": 10,
            "type": "assessment",
            "content_id": "final-assessment",
            "title": "Course Final Assessment",
            "description": "Comprehensive assessment covering all modules",
            "duration_minutes": 60,
            "scheduled_date": "2026-02-20",
            "priority": "critical",
            "checkpoint": {
              "type": "assessment",
              "passing_score": 75,
              "unlocks": "course_completion_certificate"
            }
          }
        ]
      }
    ],
    "milestones": [
      {
        "milestone_id": "ms-001",
        "name": "Foundation Complete",
        "target_date": "2026-01-26",
        "requirements": ["step-001", "step-002", "step-003"],
        "reward": "Foundation Mastery Badge"
      },
      {
        "milestone_id": "ms-002",
        "name": "Multi-Agent Expert",
        "target_date": "2026-02-09",
        "requirements": ["step-004", "step-005", "step-006", "step-007"],
        "reward": "Multi-Agent Expert Badge"
      },
      {
        "milestone_id": "ms-003",
        "name": "Course Complete",
        "target_date": "2026-02-25",
        "requirements": ["step-008", "step-009", "step-010"],
        "reward": "Course Completion Certificate"
      }
    ]
  },
  "personalization_factors": {
    "learning_pace_adjustment": "Slightly accelerated based on your history",
    "style_accommodations": "Included extra hands-on exercises based on your preference",
    "gap_remediation": "Added Phase 1 to address identified knowledge gaps",
    "schedule_optimization": "Sessions scheduled for your preferred evening times"
  },
  "ai_notes": {
    "generated_by": "claude-sonnet-4",
    "rationale": "This path prioritizes addressing your orchestration patterns gap first, as it's critical for multi-agent systems understanding. The 3-day buffer accounts for potential schedule conflicts while keeping you on track for your target date.",
    "alternative_approaches": [
      "Faster track (16 hours, no review): Achievable but higher risk of retention issues",
      "Deeper track (22 hours, extra practice): More thorough but extends past target date"
    ]
  },
  "actions": {
    "save_path": "/api/v1/learning/path/path-abc123/save",
    "modify_path": "/api/v1/learning/path/path-abc123/modify",
    "start_path": "/api/v1/learning/path/path-abc123/start"
  }
}
```

**Response 400 (Invalid Constraints):**
```json
{
  "error": "infeasible_constraints",
  "message": "Cannot complete course by target date with given time constraints",
  "details": {
    "required_hours": 25,
    "available_hours": 15,
    "shortfall_hours": 10
  },
  "suggestions": [
    {
      "option": "extend_deadline",
      "new_target_date": "2026-03-15",
      "feasibility": "achievable"
    },
    {
      "option": "increase_hours",
      "required_hours_per_week": 8,
      "feasibility": "achievable"
    },
    {
      "option": "skip_optional_content",
      "skipped_items": ["practice exercises", "review sessions"],
      "new_duration_hours": 14,
      "feasibility": "achievable_with_tradeoffs"
    }
  ]
}
```

---

### 5. Get Next Recommended Steps

**Endpoint:** `GET /api/v1/learning/next-steps/{user_id}`

**Purpose:** Get immediate next actions for the user's current session

**Path Parameters:**
- `user_id` (string, required): User identifier

**Query Parameters:**
- `available_minutes` (integer, optional): Time available for current session (default: 30)
- `mood` (string, optional): Current learning mood: `focused`, `casual`, `quick_review`, `challenge_me`

**Request Example:**
```http
GET /api/v1/learning/next-steps/user-123?available_minutes=45&mood=focused
Authorization: Bearer <user_token>
```

**Response 200 (Pro Tier):**
```json
{
  "user_id": "user-123",
  "session_context": {
    "available_minutes": 45,
    "mood": "focused",
    "current_time": "2026-01-19T19:30:00Z",
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
    },
    {
      "step_number": 2,
      "action": "take_quiz",
      "content_id": "quiz-ch6-checkpoint",
      "title": "Mid-Chapter Check",
      "description": "Quick knowledge check before proceeding",
      "duration_minutes": 8,
      "reason": "Reinforce learning before moving to next section",
      "cta": "Take Quiz"
    },
    {
      "step_number": 3,
      "action": "practice_exercise",
      "content_id": "practice-ch6-01",
      "title": "Runtime Skills Exercise",
      "description": "Apply what you've learned with hands-on practice",
      "duration_minutes": 12,
      "reason": "Matches your hands-on learning preference",
      "cta": "Start Exercise"
    }
  ],
  "alternative_paths": [
    {
      "mood": "quick_review",
      "description": "Short 15-min review session instead",
      "steps": ["Review ch5 key concepts", "Flashcard practice"]
    },
    {
      "mood": "challenge_me",
      "description": "Jump to advanced content",
      "steps": ["Preview ch7 intro", "Advanced quiz attempt"]
    }
  ],
  "motivational_context": {
    "streak_status": "4 days - keep it going!",
    "achievement_progress": "2 more chapters for 'Consistent Learner' badge",
    "personalized_message": "Your evening sessions are your most productive. Great time for the focused chapter work you planned."
  },
  "generated_by": "claude-sonnet-4",
  "generated_at": "2026-01-19T19:30:00Z"
}
```

**Response 200 (Premium Tier - Rule-Based):**
```json
{
  "user_id": "user-456",
  "session_context": {
    "available_minutes": 30,
    "mood": "focused"
  },
  "next_steps": [
    {
      "step_number": 1,
      "action": "start_chapter",
      "content_id": "ch4-skill-md-structure",
      "title": "Next: Skill.md Structure",
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
```

---

## Data Models

### LearningProfile

```typescript
interface LearningProfile {
  user_id: string;

  learning_pace: {
    category: 'slow' | 'moderate' | 'fast' | 'intensive';
    chapters_per_week: number;
    avg_session_minutes: number;
    preferred_session_times: ('morning' | 'afternoon' | 'evening' | 'weekend')[];
    consistency_score: number; // 0-100
  };

  learning_style: {
    primary: 'visual' | 'auditory' | 'reading' | 'hands_on' | 'unknown';
    secondary?: 'visual' | 'auditory' | 'reading' | 'hands_on';
    preferences: {
      prefers_examples: boolean;
      prefers_theory_first: boolean;
      prefers_practice_exercises: boolean;
      reading_vs_video: 'reading' | 'video' | 'mixed';
    };
  };

  strengths: TopicAssessment[];
  weaknesses: TopicAssessment[];

  overall_progress: {
    chapters_completed: number;
    chapters_total: number;
    completion_percentage: number;
    estimated_completion_date?: string; // ISO date
    current_streak_days: number;
  };

  ai_insights?: {
    generated_by: string;
    generated_at: string; // ISO datetime
    summary: string;
    personalized_tips: string[];
  };

  updated_at: string; // ISO datetime
}

interface TopicAssessment {
  topic: string;
  chapter_id: string;
  confidence_score: number; // 0-100
  evidence: string;
  recommended_action?: string;
}
```

### Recommendation

```typescript
interface Recommendation {
  id: string;
  type: 'chapter' | 'quiz' | 'practice' | 'review' | 'assessment';
  content_id: string;
  title: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  reason: string;
  estimated_time_minutes: number;

  // Optional fields based on type
  difficulty_match?: 'too_easy' | 'appropriate' | 'challenging' | 'too_hard';
  prerequisites_met?: boolean;
  missing_prerequisites?: string[];
  focus_areas?: string[];
  potential_achievement?: string;

  confidence: number; // 0-1, how confident the AI is in this recommendation
  tags: string[];
}
```

### KnowledgeGap

```typescript
interface KnowledgeGap {
  id: string;
  topic: string;
  severity: 'critical' | 'moderate' | 'minor';
  severity_score: number; // 0-100
  affected_chapters: string[];

  root_cause: {
    type: 'prerequisite_gap' | 'incomplete_understanding' | 'topic_not_encountered' | 'partial_coverage';
    description: string;
    evidence: string[];
  };

  recommended_content: RecommendedRemediationContent[];
  impact_if_unaddressed: string;
}

interface RecommendedRemediationContent {
  content_id: string;
  type: 'chapter' | 'review' | 'focused_review' | 'practice' | 'quiz';
  priority: 'critical' | 'high' | 'medium' | 'low';
  focus_sections?: string[];
  description?: string;
  estimated_time_minutes: number;
}
```

### LearningPath

```typescript
interface LearningPath {
  path_id: string;
  user_id: string;
  generated_at: string; // ISO datetime

  summary: {
    total_duration_hours: number;
    total_sessions: number;
    estimated_completion_date: string; // ISO date
    target_date?: string; // ISO date
    buffer_days?: number;
    feasibility: 'achievable' | 'challenging' | 'at_risk' | 'infeasible';
    confidence: number; // 0-1
  };

  phases: LearningPhase[];
  milestones: Milestone[];

  personalization_factors: {
    learning_pace_adjustment: string;
    style_accommodations: string;
    gap_remediation: string;
    schedule_optimization: string;
  };
}

interface LearningPhase {
  phase_number: number;
  name: string;
  description: string;
  duration_days: number;
  start_date: string; // ISO date
  end_date: string; // ISO date
  steps: LearningStep[];
}

interface LearningStep {
  step_id: string;
  order: number;
  type: 'chapter' | 'review' | 'practice' | 'quiz' | 'assessment';
  content_id: string;
  title: string;
  description?: string;
  duration_minutes: number;
  scheduled_date: string; // ISO date
  priority: 'critical' | 'high' | 'medium' | 'low';
  focus_sections?: string[];

  checkpoint?: {
    type: 'quiz' | 'assessment' | 'exercise';
    quiz_id?: string;
    passing_score: number;
    unlocks?: string;
  };
}

interface Milestone {
  milestone_id: string;
  name: string;
  target_date: string; // ISO date
  requirements: string[]; // step_ids
  reward: string;
}
```

---

## LLM Integration

### When to Call Claude API vs Use Cached/Rule-Based

| Scenario | Method | Rationale |
|----------|--------|-----------|
| First profile request | Claude API | Need full analysis |
| Profile request < 4 hours old | Cache | Stable data, save tokens |
| Profile with no new activity | Cache | No new data to analyze |
| Recommendations < 2 hours old | Cache | Context unchanged |
| New quiz completed | Claude API | Significant new signal |
| Chapter completed | Claude API | Update recommendations |
| Knowledge gap analysis | Claude API | Complex reasoning required |
| Learning path generation | Claude API | Complex planning required |
| Next steps (repeat request) | Cache | Same context |
| Next steps (new mood/time) | Hybrid | Rule-based + cached insights |
| Free/Premium tier | Rule-based | LLM features not available |

### Prompt Templates

#### Learning Profile Analysis Prompt

```text
You are an expert learning analyst for an AI Agents course. Analyze the following learner data and provide insights.

## Learner Data
- User ID: {{user_id}}
- Course Progress: {{chapters_completed}}/{{total_chapters}} chapters
- Quiz Scores: {{quiz_scores_summary}}
- Session History: {{session_history}}
- Time on Chapters: {{time_per_chapter}}
- Practice Exercise Completion: {{practice_completion}}

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
```

#### Knowledge Gap Analysis Prompt

```text
You are an expert educational diagnostician for an AI Agents course.

## Course Structure
Module 1: Foundations (ch1-ch3)
Module 2: Skills & Runtime (ch4-ch6)
Module 3: Advanced (ch7-ch9)

Prerequisites:
- ch4 requires ch1-ch3
- ch7 requires ch4-ch6
- ch8 requires ch7
- ch9 requires ch7-ch8

## Learner Performance Data
{{performance_data}}

## Your Task
Identify knowledge gaps by analyzing:
1. Quiz performance by topic/section
2. Time spent vs expected time
3. Retry patterns
4. Prerequisite completion status
5. Practice exercise completion

For each gap found, provide:
- Topic name
- Severity (critical/moderate/minor) with score
- Root cause analysis
- Evidence from the data
- Specific recommended remediation content
- Impact if unaddressed

Order gaps by severity (critical first).
Respond in JSON format matching the KnowledgeGap schema.
```

#### Learning Path Generation Prompt

```text
You are an expert learning path designer for an AI Agents course.

## Learner Context
- Current Progress: {{current_progress}}
- Knowledge Gaps: {{knowledge_gaps}}
- Learning Profile: {{learning_profile}}
- Goal: {{goal}}
- Constraints: {{constraints}}

## Course Content Available
{{available_content}}

## Your Task
Design an optimal learning path that:
1. Addresses critical knowledge gaps first
2. Respects the learner's time constraints
3. Accommodates their learning style
4. Includes appropriate checkpoints
5. Builds toward their goal

The path should include:
- Phases with clear objectives
- Specific steps with timing
- Checkpoints for assessment
- Milestones for motivation
- Buffer time for unexpected delays

Provide rationale for key decisions.
Respond in JSON format matching the LearningPath schema.
```

### Token Budget Constraints

| Operation | Max Input Tokens | Max Output Tokens | Cache TTL |
|-----------|-----------------|-------------------|-----------|
| Profile Analysis | 2,000 | 1,500 | 4 hours |
| Recommendations | 1,500 | 1,000 | 2 hours |
| Knowledge Gap | 3,000 | 2,000 | 6 hours |
| Learning Path | 4,000 | 3,000 | 24 hours |
| Next Steps | 1,000 | 500 | 1 hour |

**Monthly Budget per User (Pro Tier):**
- Target: 50,000 tokens/month (~$0.15 at current Sonnet pricing)
- Hard limit: 100,000 tokens/month
- Overage action: Fall back to rule-based until next month

### Caching Strategy

```python
# Cache key patterns
CACHE_KEYS = {
    "profile": "adaptive:profile:{user_id}:v{version}",
    "recommendations": "adaptive:recs:{user_id}:{context}:v{version}",
    "knowledge_gaps": "adaptive:gaps:{user_id}:v{version}",
    "learning_path": "adaptive:path:{path_id}",
    "next_steps": "adaptive:next:{user_id}:{available_min}:{mood}:v{version}"
}

# Invalidation triggers
INVALIDATION_TRIGGERS = {
    "profile": ["quiz_completed", "chapter_completed", "manual_refresh"],
    "recommendations": ["quiz_completed", "chapter_completed", "new_session"],
    "knowledge_gaps": ["quiz_completed", "chapter_completed", "manual_refresh"],
    "next_steps": ["content_completed", "mood_change", "time_change"]
}
```

---

## Error Handling & Fallbacks

### LLM Unavailability Handling

```python
async def get_recommendations_with_fallback(user_id: str, context: str) -> dict:
    """
    Get recommendations with graceful degradation.
    """
    # Check cache first
    cached = await cache.get(f"adaptive:recs:{user_id}:{context}")
    if cached:
        return {**cached, "cached": True}

    # Try LLM
    try:
        result = await call_claude_api(
            prompt=build_recommendation_prompt(user_id, context),
            timeout=10.0,
            max_retries=2
        )
        await cache.set(f"adaptive:recs:{user_id}:{context}", result, ttl=7200)
        return {**result, "generated_by": "claude-sonnet-4", "cached": False}

    except LLMUnavailableError:
        logger.warning(f"LLM unavailable for user {user_id}, falling back to rules")
        return generate_rule_based_recommendations(user_id, context)

    except LLMRateLimitError:
        logger.warning(f"LLM rate limited for user {user_id}")
        # Return stale cache if available
        stale = await cache.get(f"adaptive:recs:{user_id}:{context}", allow_stale=True)
        if stale:
            return {**stale, "cached": True, "stale": True}
        return generate_rule_based_recommendations(user_id, context)

    except LLMTokenBudgetExceeded:
        logger.warning(f"Token budget exceeded for user {user_id}")
        return {
            **generate_rule_based_recommendations(user_id, context),
            "budget_notice": "AI features will refresh next billing cycle"
        }
```

### Error Response Codes

| Error | HTTP Code | Response |
|-------|-----------|----------|
| LLM unavailable | 200 | Returns rule-based fallback with `"fallback": true` |
| LLM timeout | 200 | Returns cached or rule-based fallback |
| Token budget exceeded | 200 | Returns rule-based with budget notice |
| Invalid user | 404 | `{"error": "user_not_found"}` |
| Access denied (tier) | 403 | `{"error": "feature_not_available", "required_tier": "..."}` |
| Invalid request | 400 | `{"error": "validation_error", "details": {...}}` |
| Rate limited | 429 | `{"error": "rate_limited", "retry_after": 60}` |

### Rule-Based Fallback Logic

```python
def generate_rule_based_recommendations(user_id: str, context: str) -> dict:
    """
    Generate recommendations without LLM using simple rules.
    """
    # Get user progress
    progress = get_user_progress(user_id)

    recommendations = []

    # Rule 1: Next chapter in sequence
    next_chapter = get_next_incomplete_chapter(progress)
    if next_chapter:
        recommendations.append({
            "id": f"rec-rule-{next_chapter.id}",
            "type": "chapter",
            "content_id": next_chapter.id,
            "title": next_chapter.title,
            "priority": "high",
            "reason": "Next chapter in sequence",
            "confidence": 1.0,
            "tags": ["next_in_sequence"]
        })

    # Rule 2: Low quiz scores need review
    low_scores = get_quizzes_below_threshold(progress, threshold=60)
    for quiz in low_scores[:2]:
        recommendations.append({
            "id": f"rec-rule-review-{quiz.chapter_id}",
            "type": "review",
            "content_id": quiz.chapter_id,
            "title": f"Review: {quiz.chapter_title}",
            "priority": "medium",
            "reason": f"Quiz score {quiz.score}% - review recommended",
            "confidence": 1.0,
            "tags": ["low_score_review"]
        })

    # Rule 3: Incomplete practice exercises
    incomplete_practice = get_incomplete_practice(progress)
    if incomplete_practice:
        recommendations.append({
            "id": f"rec-rule-practice",
            "type": "practice",
            "content_id": incomplete_practice.id,
            "title": incomplete_practice.title,
            "priority": "low",
            "reason": "Incomplete practice exercise",
            "confidence": 1.0,
            "tags": ["incomplete"]
        })

    return {
        "user_id": user_id,
        "recommendations": recommendations[:5],
        "generated_by": "rule_engine",
        "fallback": True
    }
```

---

## Database Schema

```sql
-- Learning profiles (cached LLM analysis)
CREATE TABLE learning_profiles (
    user_id VARCHAR(100) PRIMARY KEY,
    profile_data JSONB NOT NULL,
    generated_by VARCHAR(50) NOT NULL, -- 'claude-sonnet-4', 'rule_engine'
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL
);

-- Learning paths
CREATE TABLE learning_paths (
    path_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL,
    path_data JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'active', 'completed', 'abandoned'
    generated_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Learning path progress
CREATE TABLE learning_path_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    path_id UUID REFERENCES learning_paths(path_id),
    user_id VARCHAR(100) NOT NULL,
    step_id VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'skipped'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    score INTEGER, -- if checkpoint
    notes TEXT,
    UNIQUE(path_id, step_id)
);

-- Token usage tracking
CREATE TABLE llm_token_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL,
    operation VARCHAR(50) NOT NULL, -- 'profile', 'recommendations', 'gaps', 'path', 'next_steps'
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    model VARCHAR(50) NOT NULL,
    cached BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Monthly token budget tracking
CREATE TABLE llm_token_budgets (
    user_id VARCHAR(100) NOT NULL,
    month VARCHAR(7) NOT NULL, -- 'YYYY-MM'
    tokens_used INTEGER DEFAULT 0,
    budget_limit INTEGER DEFAULT 50000,
    overage_action VARCHAR(20) DEFAULT 'fallback', -- 'fallback', 'block', 'alert'
    PRIMARY KEY (user_id, month)
);

-- Indexes
CREATE INDEX idx_profiles_user ON learning_profiles(user_id);
CREATE INDEX idx_profiles_expires ON learning_profiles(expires_at);
CREATE INDEX idx_paths_user ON learning_paths(user_id);
CREATE INDEX idx_paths_status ON learning_paths(status);
CREATE INDEX idx_path_progress_path ON learning_path_progress(path_id);
CREATE INDEX idx_token_usage_user_month ON llm_token_usage(user_id, created_at);
CREATE INDEX idx_token_budgets_month ON llm_token_budgets(month);
```

---

## Implementation Requirements

### FastAPI Implementation Pattern

```python
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Literal
from pydantic import BaseModel
from datetime import datetime, timedelta
import anthropic

router = APIRouter(prefix="/api/v1/learning")

# Claude client
claude = anthropic.Anthropic()

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


@router.get("/profile/{user_id}")
async def get_learning_profile(
    user_id: str,
    include_history: bool = False,
    refresh: bool = False,
    user: dict = Depends(get_current_user)
):
    """
    Get user learning profile with AI insights.

    Access Control:
    - Free: No access
    - Premium: Basic profile (rule-based)
    - Pro/Team: Full profile (LLM-enhanced)
    """
    # Verify user can access this profile
    if user["id"] != user_id and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    tier = user.get("tier", "free")

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
        if cached and cached.get("expires_at") > datetime.utcnow().isoformat():
            return {**cached, "cached": True}

    # Get user data for analysis
    user_data = await gather_user_learning_data(user_id)

    # Premium tier - rule-based basic profile
    if tier == "premium":
        profile = generate_rule_based_profile(user_data)
        profile["upgrade_prompt"] = {
            "message": "Upgrade to Pro for AI-powered learning insights",
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
        await cache.set(f"adaptive:profile:{user_id}", cache_data, ttl=14400)

        # Track token usage
        await track_token_usage(user_id, "profile", profile.get("token_usage", {}))

        return {**profile, "cached": False}

    except Exception as e:
        logger.error(f"LLM profile generation failed: {e}")
        # Fallback to rule-based
        profile = generate_rule_based_profile(user_data)
        profile["fallback"] = True
        profile["fallback_reason"] = "AI service temporarily unavailable"
        return profile


async def generate_llm_profile(user_id: str, user_data: dict) -> dict:
    """Generate learning profile using Claude Sonnet 4."""

    # Check token budget
    budget = await get_user_token_budget(user_id)
    if budget["remaining"] < 3500:  # Estimated tokens for profile
        raise LLMTokenBudgetExceeded(f"Token budget low: {budget['remaining']} remaining")

    prompt = build_profile_prompt(user_data)

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[
            {"role": "user", "content": prompt}
        ],
        system="You are an expert learning analyst. Respond only with valid JSON."
    )

    # Parse response
    profile_data = parse_json_response(response.content[0].text)

    return {
        "user_id": user_id,
        "profile": profile_data,
        "ai_insights": profile_data.get("ai_insights"),
        "generated_by": "claude-sonnet-4",
        "generated_at": datetime.utcnow().isoformat(),
        "token_usage": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }


@router.get("/recommendations/{user_id}")
async def get_recommendations(
    user_id: str,
    limit: int = Query(5, ge=1, le=10),
    type: Optional[Literal["chapter", "quiz", "practice", "review"]] = None,
    context: Optional[Literal["morning_session", "evening_session", "quick_review", "deep_study"]] = None,
    user: dict = Depends(get_current_user)
):
    """
    Get personalized content recommendations.

    Access Control:
    - Free: No access
    - Premium: Basic recommendations (rule-based)
    - Pro/Team: Full recommendations (LLM-enhanced)
    """
    # Similar implementation pattern...
    pass


@router.get("/knowledge-gaps/{user_id}")
async def get_knowledge_gaps(
    user_id: str,
    depth: Literal["surface", "detailed"] = "detailed",
    module: Optional[int] = None,
    user: dict = Depends(get_current_user)
):
    """
    AI-powered knowledge gap analysis.

    Access Control:
    - Free/Premium: No access (Pro feature)
    - Pro/Team: Full access
    """
    tier = user.get("tier", "free")

    if tier not in ["pro", "team"]:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "feature_not_available",
                "message": "Knowledge gap analysis is a Pro feature",
                "required_tier": "pro",
                "upgrade_url": "/api/v1/pricing/pro"
            }
        )

    # Implementation...
    pass


@router.post("/path/generate")
async def generate_learning_path(
    request: LearningPathRequest,
    user: dict = Depends(get_current_user)
):
    """
    Generate personalized learning path.

    Access Control:
    - Free/Premium: No access (Pro feature)
    - Pro/Team: Full access
    """
    # Implementation...
    pass


@router.get("/next-steps/{user_id}")
async def get_next_steps(
    user_id: str,
    available_minutes: int = Query(30, ge=5, le=180),
    mood: Optional[Literal["focused", "casual", "quick_review", "challenge_me"]] = None,
    user: dict = Depends(get_current_user)
):
    """
    Get immediate next learning actions.

    Access Control:
    - Free: No access
    - Premium: Basic next steps (rule-based)
    - Pro/Team: AI-powered next steps
    """
    # Implementation...
    pass
```

---

## Performance Requirements

- **Response Time (cached):** < 50ms (p95)
- **Response Time (LLM):** < 5s (p95)
- **Response Time (rule-based fallback):** < 100ms (p95)
- **Throughput:** 100 requests/second
- **LLM Availability Target:** 99%
- **Cache Hit Rate:** > 70%

---

## Security Requirements

1. **Authentication:** JWT Bearer tokens required
2. **Authorization:** Users can only access their own learning data
3. **Data Privacy:** Learning profiles contain personal patterns - encrypt at rest
4. **Rate Limiting:**
   - 30 requests/minute for profile/recommendations
   - 10 requests/minute for knowledge gaps/path generation
5. **Token Budget:** Enforce per-user monthly limits

---

## Testing Requirements

### Unit Tests

```python
def test_profile_pro_tier():
    """Test Pro user gets LLM-enhanced profile"""
    response = client.get(
        "/api/v1/learning/profile/user-123",
        headers={"Authorization": f"Bearer {pro_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["ai_insights"] is not None
    assert response.json()["generated_by"] == "claude-sonnet-4"

def test_profile_premium_tier():
    """Test Premium user gets rule-based profile"""
    response = client.get(
        "/api/v1/learning/profile/user-456",
        headers={"Authorization": f"Bearer {premium_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["ai_insights"] is None
    assert "upgrade_prompt" in response.json()

def test_profile_free_tier_denied():
    """Test Free user cannot access profiles"""
    response = client.get(
        "/api/v1/learning/profile/user-789",
        headers={"Authorization": f"Bearer {free_user_token}"}
    )
    assert response.status_code == 403
    assert response.json()["error"] == "feature_not_available"

def test_knowledge_gaps_pro_only():
    """Test knowledge gaps is Pro-only feature"""
    response = client.get(
        "/api/v1/learning/knowledge-gaps/user-456",
        headers={"Authorization": f"Bearer {premium_user_token}"}
    )
    assert response.status_code == 403
    assert response.json()["required_tier"] == "pro"

def test_llm_fallback_on_unavailable():
    """Test graceful fallback when LLM unavailable"""
    with mock.patch('anthropic.Anthropic.messages.create', side_effect=Exception("API down")):
        response = client.get(
            "/api/v1/learning/profile/user-123",
            headers={"Authorization": f"Bearer {pro_user_token}"}
        )
        assert response.status_code == 200
        assert response.json()["fallback"] == True
        assert response.json()["generated_by"] == "rule_engine"

def test_token_budget_enforcement():
    """Test token budget prevents overuse"""
    # Set budget to near limit
    set_user_token_budget("user-123", remaining=100)

    response = client.post(
        "/api/v1/learning/path/generate",
        json={"user_id": "user-123", "goal": {"type": "complete_course"}},
        headers={"Authorization": f"Bearer {pro_user_token}"}
    )
    assert response.status_code == 200
    assert "budget_notice" in response.json()
```

### Integration Tests

- Claude API connectivity and response parsing
- Cache invalidation on progress updates
- Token usage tracking accuracy
- End-to-end learning path workflow

---

## Monitoring & Observability

### Metrics to Track

- LLM response latency (p50, p95, p99)
- LLM error rate by type
- Cache hit/miss ratio
- Token usage per user/operation
- Fallback activation rate
- Recommendation engagement (clicked/ignored)

### Logging

```python
logger.info(
    "adaptive_request",
    user_id=user_id,
    operation="profile",
    tier=tier,
    source="llm" | "cache" | "rule_engine",
    latency_ms=duration,
    tokens_used=tokens
)

logger.warning(
    "llm_fallback_activated",
    user_id=user_id,
    operation=operation,
    reason=str(error)
)
```

---

## Cost Analysis

### Per Request Cost (Pro Tier)

```
Learning Profile (LLM):
- Input: ~1,500 tokens = $0.0045
- Output: ~1,000 tokens = $0.015
- Total: ~$0.02 per request
- With 70% cache hit: ~$0.006 effective

Recommendations (LLM):
- Input: ~1,000 tokens = $0.003
- Output: ~600 tokens = $0.009
- Total: ~$0.012 per request
- With 70% cache hit: ~$0.0036 effective

Knowledge Gaps (LLM):
- Input: ~2,500 tokens = $0.0075
- Output: ~1,500 tokens = $0.0225
- Total: ~$0.03 per request
- With 60% cache hit: ~$0.012 effective

Learning Path (LLM):
- Input: ~3,500 tokens = $0.0105
- Output: ~2,500 tokens = $0.0375
- Total: ~$0.048 per request
- Generated once, cached 24h: minimal ongoing cost

Monthly Cost per Active Pro User:
- Estimated 20 LLM requests/month
- Average $0.02 per request
- Total: ~$0.40/user/month
- At $19.99 subscription: 2% of revenue
```

---

## Success Criteria

**LLM Integration:**
- Claude Sonnet 4 integration working
- Token budgets enforced
- Graceful fallback to rule-based

**Performance:**
- P95 cached response < 50ms
- P95 LLM response < 5s
- Cache hit rate > 70%

**Functionality:**
- All 5 endpoints implemented
- Tier-based access enforced
- Fallback logic tested

**User Experience:**
- Recommendations feel personalized
- Knowledge gaps are actionable
- Learning paths are achievable

---

**Spec Version:** 2.0
**Last Updated:** January 19, 2026
**Status:** Ready for Implementation
