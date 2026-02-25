---
chapter_id: ch5-quiz-master-skill
title: Quiz Master Skill
module: 2
order: 5
difficulty: intermediate
estimated_read_time: 17
word_count: 1900
tags: ["skills", "quiz", "assessment", "feedback"]
prerequisites: ["ch4-concept-explainer-skill"]
learning_objectives:
  - "Understand the Quiz Master skill architecture"
  - "Learn how to generate questions from course content"
  - "Implement answer validation with partial credit"
  - "Design scoring and feedback mechanisms"
created_at: 2026-01-10T00:00:00Z
updated_at: 2026-01-15T12:00:00Z
---

# Quiz Master Skill

## Overview

Explaining concepts is only half the learning equation--you also need to verify that students understood them. In this chapter, you'll build the **Quiz Master** skill, which generates questions from course content, validates student answers, and provides detailed feedback. The Quiz Master complements the Concept Explainer by closing the learning loop: explain, then assess.

## What You'll Learn

- How to generate different question types from course content
- Techniques for validating free-form and multiple-choice answers
- How to design a scoring system with partial credit
- Best practices for constructive feedback
- A complete Quiz Master skill implementation

## Concepts

### Concept 1: Question Generation from Content

The Quiz Master generates questions by analyzing course content through a structured pipeline. Rather than asking generic questions, it produces questions that are directly tied to what the student has studied.

The generation pipeline has three stages:

| Stage | Input | Output |
|-------|-------|--------|
| 1. Content Analysis | Chapter markdown | Key concepts, definitions, relationships |
| 2. Template Selection | Concept type + difficulty | Appropriate question template |
| 3. Question Assembly | Template + concept data | Complete question with answer key |

**Question Types and When to Use Them:**

| Type | Best For | Example |
|------|----------|---------|
| Multiple Choice | Testing recognition and recall | "Which layer handles tool execution?" |
| True/False | Checking understanding of specific facts | "MCP Servers can expose both tools and resources." |
| Fill in the Blank | Testing precise terminology | "The _____ layer breaks complex goals into sub-tasks." |
| Short Answer | Assessing deeper understanding | "Explain why a layered architecture is preferred." |
| Code Analysis | Evaluating practical knowledge | "What does this agent loop code do?" |

The key insight is that question type should match the learning objective. Recall-oriented objectives get multiple-choice questions, while understanding-oriented objectives get short-answer questions.

### Concept 2: Answer Validation Approaches

Validating answers is more nuanced than simple string comparison. The Quiz Master uses different strategies depending on the question type:

**Exact Match** (for fill-in-the-blank): Compare the student's answer against the expected answer, with normalization for case, whitespace, and common synonyms.

**Option Match** (for multiple-choice and true/false): Check if the selected option matches the correct answer key. Straightforward but effective.

**Semantic Similarity** (for short-answer): Use the language model to compare the student's answer against the expected answer, evaluating whether the core meaning is preserved even if the wording differs.

```
Student Answer: "The Planning layer splits big tasks into smaller steps"
Expected Answer: "The Planning layer decomposes complex goals into sub-tasks"

Exact match:  NO  (different words)
Semantic match: YES (same meaning)
```

**Rubric-Based** (for code analysis): Evaluate the answer against a checklist of key points that should be mentioned.

| Validation Method | Speed | Accuracy | Best For |
|-------------------|-------|----------|----------|
| Exact Match | Fast | Low for open-ended | Fill-in-the-blank |
| Option Match | Fast | High | Multiple choice, True/False |
| Semantic Similarity | Slow | High | Short answer |
| Rubric-Based | Medium | High | Code analysis, essays |

### Concept 3: Scoring and Partial Credit

A binary right-or-wrong system discourages learners. The Quiz Master implements a **partial credit** model that rewards understanding even when answers are incomplete:

- **Full credit (100%)**: Answer is correct and complete
- **Partial credit (25-75%)**: Answer demonstrates understanding but is incomplete or imprecise
- **Minimal credit (10%)**: Answer shows effort and engagement but misses the key point
- **No credit (0%)**: No answer or completely incorrect

The scoring formula for a quiz session:

```
Session Score = Sum(question_weight * question_score) / Sum(question_weight)

Where:
  question_weight = difficulty multiplier (beginner=1, intermediate=2, advanced=3)
  question_score  = 0.0 to 1.0 based on validation result
```

This weighted approach means harder questions count more, rewarding students who tackle advanced material.

### Concept 4: Feedback Mechanisms

Effective feedback is the most valuable output of the Quiz Master. Good feedback follows the **Correct-Explain-Encourage** pattern:

1. **Correct**: State whether the answer was right, wrong, or partially correct
2. **Explain**: Describe why, referencing the specific course content
3. **Encourage**: Suggest what to review or congratulate progress

**Example of good feedback:**

> Partially correct (75%). You correctly identified that the Action layer executes tools, but the Planning layer--not the Reasoning layer--is responsible for breaking goals into sub-tasks. Review Chapter 2, Concept 3 for the distinction between Reasoning and Planning. You are making great progress on understanding the architecture!

**Example of poor feedback:**

> Wrong. The answer is Planning layer.

The difference is that good feedback teaches, while poor feedback only judges. The Quiz Master always aims to teach.

## Hands-On Example

Here is a complete Quiz Master skill implementation:

```python
# quiz_master_skill.py

QUESTION_PROMPT = """You are a quiz generator for an AI Agent Development course.

## Source Material
{context}

## Task
Generate {count} quiz questions about: "{topic}"
Difficulty level: {difficulty}

## Instructions
- Base every question on the provided source material
- Include a mix of question types: multiple_choice, true_false, short_answer
- For multiple_choice: provide 4 options with exactly one correct answer
- For true_false: ensure the statement is unambiguously true or false
- For short_answer: provide a model answer for validation

Return the questions as a JSON array with this structure:
[
  {{
    "type": "multiple_choice",
    "question": "...",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "correct_answer": "A",
    "explanation": "...",
    "difficulty": "beginner"
  }}
]
"""

VALIDATION_PROMPT = """You are an answer evaluator for an AI course quiz.

## Question
{question}

## Expected Answer
{expected_answer}

## Student Answer
{student_answer}

## Task
Evaluate the student's answer. Return a JSON object:
{{
  "score": <float between 0.0 and 1.0>,
  "is_correct": <boolean>,
  "feedback": "<Correct-Explain-Encourage feedback>"
}}

Scoring guide:
- 1.0: Fully correct and complete
- 0.5-0.9: Partially correct, shows understanding
- 0.1-0.4: Shows effort but misses key point
- 0.0: Incorrect or no answer
"""

class QuizMasterSkill:
    """Skill that generates quizzes and validates answers."""

    def __init__(self, mcp_client, llm_client):
        self.mcp = mcp_client
        self.llm = llm_client

    def generate_quiz(self, topic: str, difficulty: str = "beginner",
                      count: int = 5) -> dict:
        """Generate a quiz from course content."""
        # Step 1: Retrieve relevant content
        search_results = self.mcp.call_tool(
            "search_content", {"query": topic, "max_results": 3}
        )
        context = self._build_context(search_results)

        # Step 2: Generate questions using the LLM
        prompt = QUESTION_PROMPT.format(
            context=context, topic=topic,
            difficulty=difficulty, count=count,
        )
        questions = self.llm.generate_json(prompt)

        return {
            "topic": topic,
            "difficulty": difficulty,
            "questions": questions,
            "total_questions": len(questions),
            "sources": [
                r["chapter_id"]
                for r in search_results.get("results", [])
            ],
        }

    def validate_answer(self, question: dict, student_answer: str) -> dict:
        """Validate a student's answer and provide feedback."""
        if question["type"] in ("multiple_choice", "true_false"):
            return self._validate_choice(question, student_answer)
        else:
            return self._validate_open_ended(question, student_answer)

    def _validate_choice(self, question: dict, answer: str) -> dict:
        """Fast validation for choice-based questions."""
        is_correct = (
            answer.strip().upper()
            == question["correct_answer"].strip().upper()
        )
        if is_correct:
            feedback = f"Correct! {question['explanation']}"
        else:
            feedback = (
                f"Not quite. The correct answer is "
                f"{question['correct_answer']}. "
                f"{question['explanation']} Keep going!"
            )
        return {
            "score": 1.0 if is_correct else 0.0,
            "is_correct": is_correct,
            "feedback": feedback,
        }

    def _validate_open_ended(self, question: dict, answer: str) -> dict:
        """Semantic validation for open-ended questions."""
        prompt = VALIDATION_PROMPT.format(
            question=question["question"],
            expected_answer=question.get("correct_answer", ""),
            student_answer=answer,
        )
        return self.llm.generate_json(prompt)

    def score_session(self, results: list[dict]) -> dict:
        """Calculate the overall quiz session score."""
        weight_map = {"beginner": 1, "intermediate": 2, "advanced": 3}
        total_weighted = 0
        total_weight = 0
        for r in results:
            weight = weight_map.get(r.get("difficulty", "beginner"), 1)
            total_weighted += weight * r["score"]
            total_weight += weight

        score = (total_weighted / total_weight) if total_weight > 0 else 0
        return {
            "total_questions": len(results),
            "weighted_score": round(score * 100, 1),
            "passed": score >= 0.7,
            "message": (
                "Great work! You have demonstrated solid understanding."
                if score >= 0.7
                else "Keep studying! Review the chapters listed in feedback."
            ),
        }

    def _build_context(self, search_results: dict) -> str:
        """Combine search results into a context string."""
        sections = []
        for result in search_results.get("results", []):
            chapter = self.mcp.call_tool(
                "get_chapter", {"chapter_id": result["chapter_id"]}
            )
            sections.append(
                f"### {chapter['title']}\n{chapter['content']}"
            )
        return (
            "\n\n".join(sections)
            if sections
            else "No relevant material found."
        )
```

The Quiz Master reuses the same Retrieve-Compose-Generate pattern from the Concept Explainer, but applies it to question generation and answer validation instead of explanations.

## Key Takeaways

1. **Question generation is a pipeline**: Content analysis, template selection, then assembly
2. **Validation strategy depends on question type**: Exact match for blanks, semantic similarity for open-ended
3. **Partial credit motivates learners**: A scoring model between 0.0 and 1.0 rewards effort
4. **Good feedback teaches**: Follow the Correct-Explain-Encourage pattern every time
5. **Skills compose well**: The Quiz Master builds on the same MCP tools and patterns as the Concept Explainer

## Check Your Understanding

Before moving on, make sure you can answer:

1. What are the three stages of the question generation pipeline?
2. When would you use semantic similarity validation instead of exact match?
3. How does the weighted scoring formula account for question difficulty?
4. What is the Correct-Explain-Encourage feedback pattern?

## Next Steps

In the next chapter, you'll learn about the **Socratic Tutor Skill**--an advanced agent skill that guides students to discover answers on their own through a series of carefully crafted questions.

Ready to explore guided learning? Continue to Chapter 6!
