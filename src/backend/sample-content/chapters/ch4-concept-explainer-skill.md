---
chapter_id: ch4-concept-explainer-skill
title: Concept Explainer Skill
module: 2
order: 4
difficulty: intermediate
estimated_read_time: 16
word_count: 1800
tags: ["skills", "explanation", "teaching", "ai-tutor"]
prerequisites: ["ch1-intro-to-agents", "ch2-agent-factory-architecture", "ch3-mcp-fundamentals"]
learning_objectives:
  - "Understand the SKILL.md file and its role in defining agent skills"
  - "Build a Concept Explainer skill from scratch"
  - "Apply prompt engineering techniques for clear explanations"
  - "Use course content as context for grounded explanations"
created_at: 2026-01-10T00:00:00Z
updated_at: 2026-01-15T12:00:00Z
---

# Concept Explainer Skill

## Overview

You now understand how agents are structured (Chapter 2) and how they connect to tools via MCP (Chapter 3). In this chapter, you will build your first agent **skill**--the Concept Explainer. A skill is a focused capability that combines a prompt template, tool access, and domain logic to accomplish a specific task. The Concept Explainer takes a topic and produces a clear, level-appropriate explanation using course content as context.

## What You'll Learn

- What a SKILL.md file is and why it matters
- The architecture of the Concept Explainer skill
- Prompt engineering techniques for adaptive explanations
- How to retrieve and use course content as grounding context
- A complete skill definition in code

## Concepts

### Concept 1: What is a SKILL.md File?

Every agent skill starts with a **SKILL.md** file--a structured markdown document that acts as both documentation and configuration. It tells the agent framework:

- **What** the skill does (name, description, purpose)
- **When** to activate it (trigger conditions and intent matching)
- **How** to execute it (prompt template, required tools, parameters)
- **What success looks like** (expected output format and quality criteria)

Think of SKILL.md as a recipe card: it lists the ingredients (tools), the instructions (prompt template), and the expected result (output format).

```markdown
# SKILL.md -- Concept Explainer

## Metadata
- name: concept_explainer
- version: 1.0.0
- trigger: "explain", "what is", "how does", "define"

## Description
Explains course concepts at the appropriate difficulty level,
using course content as the primary knowledge source.

## Required Tools
- search_content: Find relevant chapter sections
- get_chapter: Retrieve full chapter content

## Parameters
- concept: The topic to explain (required)
- difficulty: beginner | intermediate | advanced (default: beginner)
- format: brief | detailed | analogy (default: detailed)

## Output Format
Structured explanation with definition, context, examples, and summary.
```

### Concept 2: The Concept Explainer Architecture

The Concept Explainer follows a three-phase execution pattern:

| Phase | Action | Purpose |
|-------|--------|---------|
| 1. Retrieve | Search course content for the topic | Ground the explanation in course material |
| 2. Compose | Build the prompt with context and parameters | Create a tailored instruction for the LLM |
| 3. Generate | Send the prompt to the language model | Produce the final explanation |

This **Retrieve-Compose-Generate** pattern ensures that explanations are always grounded in actual course content rather than relying solely on the model's general knowledge.

```
User: "Explain the Reasoning layer"
         |
         v
+--------------------+
|  1. RETRIEVE       |  Search chapters for "Reasoning layer"
|  (MCP tools)       |  -> Finds ch2 section on Layer 4
+----------+---------+
           |
           v
+--------------------+
|  2. COMPOSE        |  Build prompt with:
|  (Prompt Engine)   |  - Retrieved content as context
|                    |  - Difficulty level
|                    |  - Output format instructions
+----------+---------+
           |
           v
+--------------------+
|  3. GENERATE       |  LLM produces the explanation
|  (Language Model)  |  grounded in course material
+--------------------+
```

### Concept 3: Prompt Engineering for Explanations

The quality of the Concept Explainer depends heavily on its prompt template. Good explanation prompts follow these principles:

**1. Role Setting**: Tell the model who it is.
> "You are an expert tutor for an AI Agent Development course."

**2. Context Injection**: Provide the retrieved course content.
> "Use the following course material as your primary source: {context}"

**3. Difficulty Calibration**: Adjust language complexity.

| Level | Prompt Instruction |
|-------|--------------------|
| Beginner | "Use simple language, avoid jargon, include a real-world analogy" |
| Intermediate | "Use technical terms with brief definitions, include code examples" |
| Advanced | "Assume familiarity with the domain, focus on nuances and trade-offs" |

**4. Structure Enforcement**: Request a specific output format.
> "Structure your explanation with: Definition, Why It Matters, How It Works, Example, and Summary."

**5. Grounding Constraint**: Keep the model on topic.
> "Only use information from the provided course material. If the topic is not covered, say so."

### Concept 4: Using Course Content as Context

The Concept Explainer does not generate explanations from thin air. It retrieves relevant course content through MCP tools and injects it into the prompt. This approach, known as **Retrieval-Augmented Generation (RAG)**, has several benefits:

- **Accuracy**: Explanations match what the course actually teaches
- **Consistency**: Students get explanations aligned with their curriculum
- **Traceability**: Every explanation can cite its source chapter
- **Currency**: When course content updates, explanations update automatically

The retrieval step uses the `search_content` tool from Chapter 3 to find relevant sections, then passes them as context to the language model.

## Hands-On Example

Here is a complete Concept Explainer skill definition in Python:

```python
# concept_explainer_skill.py

PROMPT_TEMPLATE = """You are an expert tutor for an AI Agent Development course.

## Context from Course Material
{context}

## Task
Explain the concept: "{concept}"

## Instructions
- Difficulty level: {difficulty}
- {difficulty_instructions}
- Structure your response as:
  1. **Definition**: What is it?
  2. **Why It Matters**: Why should the learner care?
  3. **How It Works**: Technical explanation with details
  4. **Example**: A concrete, practical example
  5. **Summary**: One-sentence recap
- Only use information from the provided course material.
- If the concept is not covered in the material, state that clearly.
"""

DIFFICULTY_MAP = {
    "beginner": "Use simple language and a real-world analogy. Avoid jargon.",
    "intermediate": "Use technical terms with brief definitions. Include a code snippet.",
    "advanced": "Assume domain familiarity. Focus on nuances, trade-offs, and edge cases.",
}

class ConceptExplainerSkill:
    """Skill that explains course concepts at the appropriate level."""

    def __init__(self, mcp_client, llm_client):
        self.mcp = mcp_client      # For tool calls (search, get_chapter)
        self.llm = llm_client      # For generating explanations

    def execute(self, concept: str, difficulty: str = "beginner") -> dict:
        # Phase 1: Retrieve relevant course content
        search_results = self.mcp.call_tool(
            "search_content", {"query": concept, "max_results": 3}
        )
        context = self._build_context(search_results)

        # Phase 2: Compose the prompt
        prompt = PROMPT_TEMPLATE.format(
            context=context,
            concept=concept,
            difficulty=difficulty,
            difficulty_instructions=DIFFICULTY_MAP.get(
                difficulty, DIFFICULTY_MAP["beginner"]
            ),
        )

        # Phase 3: Generate the explanation
        response = self.llm.generate(prompt)

        return {
            "concept": concept,
            "difficulty": difficulty,
            "explanation": response,
            "sources": [
                r["chapter_id"] for r in search_results.get("results", [])
            ],
        }

    def _build_context(self, search_results: dict) -> str:
        """Combine search results into a single context string."""
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
            else "No relevant course material found."
        )
```

Notice how the skill separates retrieval, composition, and generation into distinct steps. This makes each phase independently testable and debuggable.

## Key Takeaways

1. **SKILL.md is the blueprint**: It defines what a skill does, when it activates, and how it works
2. **Retrieve-Compose-Generate**: The three-phase pattern grounds explanations in real content
3. **Prompt engineering matters**: Role setting, context injection, and difficulty calibration produce better explanations
4. **RAG ensures accuracy**: Using course content as context keeps explanations consistent with the curriculum

## Check Your Understanding

Before moving on, make sure you can answer:

1. What are the key sections of a SKILL.md file?
2. What are the three phases of the Concept Explainer's execution?
3. How does difficulty level affect the prompt template?
4. Why is retrieval-augmented generation important for a course companion?

## Next Steps

In the next chapter, you'll build the **Quiz Master Skill**--an agent skill that generates questions from course content and provides intelligent feedback on student answers.

Ready to test what students have learned? Continue to Chapter 5!
