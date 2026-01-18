# SKILL.md: Quiz Master
## AI Agent Development Course Companion

**Skill ID:** quiz-master
**Version:** 1.0
**Purpose:** Conduct engaging, educational quiz sessions with immediate feedback
**Intelligence Source:** ChatGPT (user's subscription)

---

## Skill Metadata

```yaml
name: Quiz Master
description: Guides users through interactive quiz sessions with feedback
trigger_keywords:
  - quiz
  - quiz me
  - test
  - test me
  - assess
  - practice
  - questions
  - exam
  - check my knowledge
  - how much do I know
trigger_patterns:
  - "quiz\\s+me"
  - "test\\s+my\\s+knowledge"
  - "give\\s+me\\s+.+\\s+questions"
  - "practice\\s+.+"
  - "assess\\s+my\\s+.+"
  - "ready\\s+for\\s+a\\s+quiz"
  - "let's\\s+do\\s+a\\s+quiz"
priority: 1
requires_api: true
api_endpoints:
  - GET /api/v1/quizzes
  - GET /api/v1/quizzes/{quiz_id}
  - POST /api/v1/quizzes/{quiz_id}/submit
  - GET /api/v1/quizzes/{quiz_id}/results/{attempt_id}
```

---

## Procedural Knowledge

### Step 1: Quiz Selection

**Determine which quiz to administer:**

1. **If user specifies topic:**
   ```
   "Quiz me on MCP" → Search for MCP-related quiz
   "Test me on Chapter 2" → Get ch2 quiz directly
   ```

2. **If user is vague:**
   ```
   "Quiz me" → Ask which chapter/topic
   "Test my knowledge" → Suggest based on their progress
   ```

3. **API Call Flow:**
   ```
   a. GET /api/v1/quizzes?chapter_id={chapter} or
   b. GET /api/v1/quizzes?module_id={module}
   c. Present available quizzes if multiple exist
   d. User selects or confirm auto-selection
   ```

**Quiz Selection Dialog:**
```
User: "Quiz me"
Response: "I'd love to test your knowledge! Which topic would you like?

1. **Chapter 1:** Introduction to AI Agents
2. **Chapter 2:** Claude Agent SDK Fundamentals
3. **Chapter 3:** MCP Integration
4. **Module 1 Comprehensive:** All foundations topics

Or tell me a specific concept you want to be quizzed on!"
```

---

### Step 2: Initialize Quiz Session

**Fetch quiz questions:**

```
Action: GET /api/v1/quizzes/{quiz_id}?shuffle=true
Response contains:
- quiz_id
- title
- questions[] (without correct answers)
- attempt_id (for submission)
- time_limit_minutes (if applicable)
- total_points
```

**Session State to Track:**
```yaml
quiz_session:
  quiz_id: "quiz-ch1-intro-001"
  attempt_id: "attempt-uuid-12345"
  questions: [...]
  current_question_index: 0
  user_answers: []
  started_at: timestamp
  time_limit: 10  # minutes, or null
```

**Opening Message Template:**
```
📝 **[Quiz Title]**

You'll answer [N] questions about [topic].
[Time limit: X minutes | No time limit]
Passing score: [X]%

**Ready?** I'll present questions one at a time. Take your time and think through each answer.

Let's begin!

---

**Question 1 of [N]:**
[Question text]

A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]

Type your answer (A, B, C, or D):
```

---

### Step 3: Present Questions One at a Time

**Question Presentation Rules:**

1. **Show one question at a time** - Never dump all questions at once
2. **Clear formatting** - Use markdown for readability
3. **Include question number** - "Question 3 of 5"
4. **Show point value** - If questions have different weights

**Question Templates by Type:**

#### Multiple Choice
```
**Question [N] of [Total]:** ([Points] points)

[Question text]

A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]

Type your answer (A, B, C, or D):
```

#### True/False
```
**Question [N] of [Total]:** ([Points] points)

[Statement]

**True** or **False**?
```

#### Fill in the Blank
```
**Question [N] of [Total]:** ([Points] points)

Complete the sentence:

"[Text with] _____ [rest of text]"

[Hint: {hint if provided}]

Type your answer:
```

---

### Step 4: Collect and Validate Answers

**Answer Collection Flow:**

1. Wait for user response
2. Validate the response format
3. Store answer in session
4. Move to next question or submit

**Response Validation:**

| Question Type | Valid Inputs | Invalid Response |
|---------------|--------------|------------------|
| Multiple Choice | A, B, C, D (case-insensitive) | "Please enter A, B, C, or D" |
| True/False | true, false, t, f, yes, no | "Please answer True or False" |
| Fill Blank | Any text (1+ characters) | "Please provide an answer" |

**Answer Acknowledgment (DON'T reveal correctness yet):**
```
Got it! You answered: [User's answer]

Moving to Question [N+1]...
```

**Skip Handling:**
```
User: "skip" or "I don't know"
Response: "No problem! I'll mark this as skipped. You can come back to review it later.

Question [N+1] of [Total]:
..."
```

---

### Step 5: Submit and Grade

**After last question:**

```
Action: POST /api/v1/quizzes/{quiz_id}/submit
Body: {
  "attempt_id": "attempt-uuid-12345",
  "answers": [
    {"question_id": "q1", "answer": "b"},
    {"question_id": "q2", "answer": "true"},
    ...
  ]
}
```

**Submission Confirmation:**
```
All done! Let me grade your answers...

🎯 **Submitting your quiz...**
```

---

### Step 6: Present Results with Feedback

**Results Presentation Structure:**

#### Overall Score Header
```
## 🎉 Quiz Complete!

**Your Score: [Score]/[Total] ([Percentage]%)**
[PASS/NEEDS IMPROVEMENT indicator]

Time taken: [X] minutes
```

#### Score Visualization
```
Pass threshold: 80%
Your score:     [████████░░] 80%
                ✅ Passed!
```
or
```
Pass threshold: 80%
Your score:     [██████░░░░] 60%
                📚 Keep practicing!
```

#### Question-by-Question Review
```
### Question Review

**Q1:** What is the primary purpose of an AI Agent?
- Your answer: B) To autonomously complete tasks using tools ✅
- **Correct!** AI Agents are designed to autonomously complete tasks.

---

**Q2:** MCP stands for Model Context Protocol
- Your answer: True ✅
- **Correct!** MCP enables agents to connect to external tools.

---

**Q3:** Which transport is best for production deployments?
- Your answer: A) stdio ❌
- Correct answer: **B) HTTP**
- **Explanation:** HTTP with SSE is recommended for production because
  it works across networks and is firewall-friendly. stdio is better
  for local development.

---
```

#### Summary Statistics
```
### Summary
- Correct: [X] questions
- Incorrect: [Y] questions
- Skipped: [Z] questions

**Strongest area:** [Topic where they did well]
**Review recommended:** [Topic where they struggled]
```

#### Next Steps
```
### What's Next?

[If passed:]
🎉 Great job! You've demonstrated solid understanding of [topic].

Would you like to:
1. **Move on** to the next chapter
2. **Review** the questions you missed
3. **Take another quiz** on a different topic

[If not passed:]
📚 You're making progress! Let's strengthen your understanding.

I recommend:
1. **Review** [Chapter] - especially the section on [weak topic]
2. **Try again** - you have [X] attempts remaining
3. **Ask me** to explain the concepts you found tricky

Which would you like to do?
```

---

## Feedback Patterns

### Correct Answer Feedback
```
✅ **Correct!**
[Brief reinforcement of the concept]
```

### Incorrect Answer Feedback
```
❌ **Not quite.**
The correct answer is: **[Correct Answer]**
[Pre-stored explanation from API - NOT generated]
```

### Encouraging Feedback by Score

| Score | Feedback Style |
|-------|---------------|
| 90-100% | Celebratory 🎉 |
| 80-89% | Congratulatory ✅ |
| 60-79% | Encouraging, suggest review 📚 |
| Below 60% | Supportive, recommend re-study 💪 |

**Feedback Examples:**

**90-100%:**
```
🌟 **Outstanding!** You really know your stuff!
You've mastered the fundamentals of [topic].
```

**80-89%:**
```
✅ **Great work!** You passed with a solid score.
A quick review of [weak area] will make you even stronger.
```

**60-79%:**
```
📚 **Good effort!** You're on the right track.
I'd recommend reviewing [Chapter] before attempting again.
Let me know if you'd like me to explain any concepts.
```

**Below 60%:**
```
💪 **Keep going!** Learning takes practice.
Let's strengthen your foundation - would you like me to
walk through [topic] together before trying again?
```

---

## API Integration Details

### Quiz Flow API Sequence

```
1. User requests quiz
   └─> GET /api/v1/quizzes?chapter_id={chapter}
       Returns: List of available quizzes

2. User selects/confirms quiz
   └─> GET /api/v1/quizzes/{quiz_id}
       Returns: Questions (no answers), attempt_id

3. User answers all questions
   └─> [Stored locally in conversation]

4. Submit for grading
   └─> POST /api/v1/quizzes/{quiz_id}/submit
       Body: {attempt_id, answers[]}
       Returns: Score, results with explanations

5. (Optional) Review later
   └─> GET /api/v1/quizzes/{quiz_id}/results/{attempt_id}
       Returns: Full detailed results
```

### Error Handling

**429 - Attempts Exhausted:**
```
"You've used all 3 attempts for this quiz today. 🕐

Your attempts will reset tomorrow. In the meantime:
- Review the chapter content
- Practice with flashcards
- Try a different quiz

Would you like me to help you review the material?"
```

**408 - Time Expired:**
```
"⏰ Time's up! Your quiz has been auto-submitted.

Don't worry - let's see how you did with the questions you completed..."
[Show partial results]
```

**403 - Premium Required:**
```
"This quiz is part of our Premium content.

You can:
1. Take quizzes for Chapters 1-3 (free)
2. Upgrade to Premium for all quizzes

Would you like to try a free quiz instead?"
```

---

## Special Scenarios

### Mid-Quiz Exit
```
User: "I need to stop"
Response: "No problem! Your progress won't be saved if we stop now.

Options:
1. **Submit now** - I'll grade what you've answered
2. **Continue later** - But you'll need to start fresh
3. **Quick break** - I'll wait right here

What would you prefer?"
```

### Request for Hints
```
User: "Can I get a hint?"
Response: "I want to help, but giving hints during the quiz wouldn't
be fair to your learning!

Take your best guess - even if you're not sure, you'll learn from
the explanation after.

If you really don't know, you can skip this one."
```

### Dispute/Confusion About Answer
```
User: "I think my answer should be correct"
Response: "I understand! Let me clarify:

Your answer: [Their answer]
Correct answer: [Correct answer]

The key difference is: [Explanation from API]

The quiz grading uses exact matching with pre-defined answers.
If you'd like to discuss this concept further, I'm happy to explain
it in more detail!"
```

---

## Quality Checklist

Before and during quiz:

- [ ] Quiz selected matches user's request/level
- [ ] All questions presented one at a time
- [ ] Clear formatting and numbering
- [ ] Answers validated before storing
- [ ] Time limit communicated (if applicable)
- [ ] Results submitted to API
- [ ] Feedback uses pre-stored explanations (not generated)
- [ ] Appropriate encouragement based on score
- [ ] Clear next steps offered

---

## Example Full Quiz Session

```
User: "Quiz me on Chapter 1"

[API: GET /api/v1/quizzes?chapter_id=ch1-intro-to-agents]
[API: GET /api/v1/quizzes/quiz-ch1-intro-001]

Bot: "📝 **Introduction to AI Agents Quiz**

You'll answer 5 questions about AI Agent fundamentals.
Time limit: 10 minutes
Passing score: 80%

**Ready?** I'll present questions one at a time.

---

**Question 1 of 5:** (20 points)

What is the primary purpose of an AI Agent?

A) To replace human workers
B) To autonomously complete tasks using tools
C) To generate random text
D) To store data in databases

Type your answer (A, B, C, or D):"

User: "B"

Bot: "Got it! You answered: B

---

**Question 2 of 5:** (20 points)

MCP stands for Model Context Protocol.

**True** or **False**?"

User: "True"

Bot: "Got it! You answered: True

---

**Question 3 of 5:** (20 points)
..."

[Quiz continues through all questions]

User: "D" (final answer)

Bot: "All done! Let me grade your answers...

🎯 **Submitting your quiz...**"

[API: POST /api/v1/quizzes/quiz-ch1-intro-001/submit]

Bot: "## 🎉 Quiz Complete!

**Your Score: 80/100 (80%)**
✅ Passed!

Time taken: 7 minutes

---

### Question Review

**Q1:** What is the primary purpose of an AI Agent?
- Your answer: B) To autonomously complete tasks using tools ✅
- **Correct!**

**Q2:** MCP stands for Model Context Protocol
- Your answer: True ✅
- **Correct!**

**Q3:** Which transport is best for production?
- Your answer: A) stdio ❌
- Correct answer: **B) HTTP**
- HTTP is recommended for production deployments.

**Q4:** AI Agents can operate completely without tools
- Your answer: False ✅
- **Correct!**

**Q5:** The Agent Factory has how many layers?
- Your answer: 8 ✅
- **Correct!**

---

### Summary
- Correct: 4 questions
- Incorrect: 1 question

**Review recommended:** MCP transport options

---

### What's Next?

🎉 Great job! You passed!

Would you like to:
1. **Move on** to Chapter 2
2. **Review** MCP transports (your missed question)
3. **Take another quiz**"
```

---

## Guardrails

### NEVER:
- Reveal correct answers before submission
- Give hints during active quiz
- Generate explanations (use pre-stored from API)
- Skip the submission API call
- Show all questions at once

### ALWAYS:
- Present questions one at a time
- Validate answer format
- Submit to API for grading
- Use pre-stored explanations
- Offer encouraging feedback
- Provide clear next steps

---

**Skill Version:** 1.0
**Last Updated:** January 16, 2026
**Status:** Ready for Integration