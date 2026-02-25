---
chapter_id: ch8-agentic-workflows
title: "Agentic Workflows"
module: 3
order: 8
difficulty: advanced
estimated_read_time: 24
word_count: 3000
tags: ["agentic", "workflows", "orchestration", "multi-agent", "patterns", "error-handling"]
prerequisites: ["ch1-intro-to-agents", "ch2-agent-factory-architecture", "ch6-socratic-tutor-skill", "ch7-progress-motivator-skill"]
learning_objectives:
  - "Design multi-step agent workflows that compose multiple skills"
  - "Choose between sequential and parallel execution strategies"
  - "Implement robust error handling and recovery mechanisms"
  - "Apply workflow patterns: chain, fan-out, fan-in, and router"
  - "Build a complete workflow orchestration engine in Python"
created_at: 2026-01-10T00:00:00Z
updated_at: 2026-01-15T12:00:00Z
---

# Agentic Workflows

## Overview

Individual AI skills are powerful, but real-world tasks often require **multiple skills working together** in coordinated sequences. A learner asks a question: the system needs to explain the concept, quiz them on it, guide them through Socratic discovery if they struggle, and track their progress throughout. This is an **agentic workflow** -- a multi-step process where an orchestrator coordinates specialized agents to accomplish a complex goal.

This chapter teaches you how to design, implement, and debug workflows that chain skills together reliably, handle failures gracefully, and execute steps in parallel when possible.

## What You'll Learn

- What agentic workflows are and why single-agent approaches fall short
- The four core workflow patterns: Chain, Fan-Out, Fan-In, and Router
- How to choose between sequential and parallel execution
- Error handling strategies: retry, fallback, circuit breaker
- A complete Python workflow orchestration engine

## Concepts

### Concept 1: Why Workflows Matter

A single agent with a single skill can handle simple requests. But consider a "Study Session" that should:

1. Identify the topic the learner wants to study
2. Explain the core concepts (Concept Explainer)
3. Ask Socratic questions to deepen understanding (Socratic Tutor)
4. Quiz the learner on the material (Quiz Master)
5. Record progress and deliver motivation (Progress Motivator)

No single skill can do all of this. You need an **orchestrator** that breaks the goal into steps, assigns each step to the right skill, manages data flow between steps, and handles failures.

| Approach | Complexity Supported | Failure Handling | Skill Reuse |
|----------|---------------------|------------------|-------------|
| Single Agent | Low | None | No |
| Hardcoded Pipeline | Medium | Manual | Partial |
| Workflow Orchestrator | High | Automatic | Full |
| Multi-Agent System | Very High | Distributed | Full |

### Concept 2: Workflow Patterns

Four patterns cover the vast majority of workflow designs:

```
1. CHAIN (Sequential Pipeline)
   Step A ---> Step B ---> Step C ---> Result
   Each step depends on the output of the previous step.

2. FAN-OUT / FAN-IN (Parallel with Aggregation)
                 +--> Worker A --+
   Input --------+--> Worker B --+--------> Aggregate --> Result
                 +--> Worker C --+
   Independent steps run in parallel, then results are combined.

3. ROUTER (Conditional Branching)
                 +--> Path A (if condition X)
   Input --> Router
                 +--> Path B (if condition Y)
   A decision point sends the input down different paths.

4. LOOP (Iterative Refinement)
   Input --> Process --> Check Quality --+--> Result (if good)
                  ^                     |
                  +---------------------+ (if not good, retry)
   Repeat until a quality threshold is met or max iterations reached.
```

**When to Use Each Pattern**

| Pattern | Use When | Example |
|---------|----------|---------|
| Chain | Steps have strict dependencies | Explain -> Quiz -> Record Progress |
| Fan-Out/In | Steps are independent and can run simultaneously | Generate quiz + fetch related content + check prerequisites |
| Router | Different inputs require different processing paths | Beginner gets explanation, advanced gets challenge |
| Loop | Output quality is uncertain and may need refinement | Regenerate question if previous one was too easy |

### Concept 3: Error Handling and Recovery

Workflows fail. LLM calls time out, skills return unexpected data, and external services go down. A production workflow must handle these failures without crashing the entire pipeline.

**Three Error Handling Strategies**

```
Strategy 1: RETRY (with backoff)
+--------+     +--------+     +--------+
| Try 1  | --> | Try 2  | --> | Try 3  | --> Fail
| (fail) |     | (fail) |     | (fail) |
+--------+     +--------+     +--------+
  wait 1s        wait 2s        wait 4s

Strategy 2: FALLBACK (graceful degradation)
+----------+     +-----------+
| Primary  | --> | Fallback  | --> Result
| (failed) |     | (simpler) |
+----------+     +-----------+

Strategy 3: CIRCUIT BREAKER (prevent cascade)
+----------+     +----------+
| Attempts | --> | OPEN     | --> Skip for cooldown period
| 3 fails  |     | Circuit  |
| in 60s   |     | Breaker  |
+----------+     +----------+
```

| Strategy | Best For | Trade-off |
|----------|----------|-----------|
| Retry | Transient failures (network, timeout) | Adds latency on failure |
| Fallback | Non-critical features | Reduced functionality |
| Circuit Breaker | Protecting downstream services | Temporary feature unavailability |

### Concept 4: Sequential vs Parallel Execution

Choosing between sequential and parallel execution depends on data dependencies between steps.

**Rule of thumb**: If Step B needs the output of Step A, they must be sequential. If Step B and Step C are independent of each other, they can be parallel.

```
Sequential (total time = sum of all steps):
  [Step A: 2s] --> [Step B: 3s] --> [Step C: 1s] = 6s total

Parallel (total time = longest step):
  [Step A: 2s] --+
  [Step B: 3s] --+--> [Aggregate: 0.5s] = 3.5s total
  [Step C: 1s] --+
```

Parallel execution can dramatically reduce latency, but it requires careful handling of shared state. Never let two parallel steps write to the same data without synchronization.

## Hands-On Example

Here is a complete workflow orchestration engine:

```python
import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from datetime import datetime


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepResult:
    """Result of executing a single workflow step."""
    step_name: str
    status: StepStatus
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0


@dataclass
class WorkflowStep:
    """Definition of a single step in a workflow."""
    name: str
    handler: Callable
    retry_count: int = 2
    fallback: Optional[Callable] = None
    depends_on: list[str] = field(default_factory=list)


@dataclass
class WorkflowResult:
    """Aggregated result of an entire workflow execution."""
    workflow_name: str
    steps: list[StepResult] = field(default_factory=list)
    success: bool = True
    total_duration_ms: float = 0.0

    def get_step_output(self, step_name: str) -> Any:
        """Retrieve the output of a specific step by name."""
        for step in self.steps:
            if step.step_name == step_name:
                return step.output
        return None


class WorkflowOrchestrator:
    """Executes multi-step agent workflows with error handling."""

    def __init__(self, name: str):
        self.name = name
        self.steps: list[WorkflowStep] = []

    def add_step(
        self,
        name: str,
        handler: Callable,
        retry_count: int = 2,
        fallback: Optional[Callable] = None,
        depends_on: Optional[list[str]] = None,
    ) -> "WorkflowOrchestrator":
        """Add a step to the workflow. Returns self for chaining."""
        self.steps.append(
            WorkflowStep(
                name=name,
                handler=handler,
                retry_count=retry_count,
                fallback=fallback,
                depends_on=depends_on or [],
            )
        )
        return self

    async def execute(self, initial_context: dict) -> WorkflowResult:
        """Execute all workflow steps, respecting dependencies."""
        result = WorkflowResult(workflow_name=self.name)
        context = dict(initial_context)
        completed: dict[str, StepResult] = {}
        start_time = datetime.now()

        # Build dependency graph and find execution order
        remaining = list(self.steps)

        while remaining:
            # Find steps whose dependencies are all satisfied
            ready = [
                s for s in remaining
                if all(dep in completed for dep in s.depends_on)
            ]
            if not ready:
                # Deadlock -- remaining steps have unmet dependencies
                for step in remaining:
                    step_result = StepResult(
                        step_name=step.name,
                        status=StepStatus.SKIPPED,
                        error="Unresolvable dependency",
                    )
                    result.steps.append(step_result)
                    result.success = False
                break

            # Execute all ready steps in parallel
            tasks = [
                self._execute_step(step, context, completed)
                for step in ready
            ]
            step_results = await asyncio.gather(*tasks)

            for step, step_result in zip(ready, step_results):
                completed[step.name] = step_result
                result.steps.append(step_result)

                if step_result.status == StepStatus.COMPLETED:
                    # Make step output available to subsequent steps
                    context[step.name] = step_result.output
                else:
                    result.success = False

                remaining.remove(step)

        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        result.total_duration_ms = round(elapsed, 2)
        return result

    async def _execute_step(
        self,
        step: WorkflowStep,
        context: dict,
        completed: dict[str, StepResult],
    ) -> StepResult:
        """Execute a single step with retry and fallback logic."""
        start = datetime.now()

        for attempt in range(1, step.retry_count + 1):
            try:
                output = await self._call_handler(step.handler, context)
                elapsed = (datetime.now() - start).total_seconds() * 1000
                return StepResult(
                    step_name=step.name,
                    status=StepStatus.COMPLETED,
                    output=output,
                    duration_ms=round(elapsed, 2),
                )
            except Exception as exc:
                if attempt < step.retry_count:
                    await asyncio.sleep(attempt * 0.5)  # backoff
                    continue
                # All retries exhausted -- try fallback
                if step.fallback:
                    try:
                        output = await self._call_handler(
                            step.fallback, context
                        )
                        elapsed = (
                            (datetime.now() - start).total_seconds() * 1000
                        )
                        return StepResult(
                            step_name=step.name,
                            status=StepStatus.COMPLETED,
                            output=output,
                            duration_ms=round(elapsed, 2),
                        )
                    except Exception:
                        pass
                elapsed = (datetime.now() - start).total_seconds() * 1000
                return StepResult(
                    step_name=step.name,
                    status=StepStatus.FAILED,
                    error=str(exc),
                    duration_ms=round(elapsed, 2),
                )

        # Should not reach here, but handle gracefully
        return StepResult(step_name=step.name, status=StepStatus.FAILED)

    @staticmethod
    async def _call_handler(handler: Callable, context: dict) -> Any:
        """Call a handler, supporting both sync and async functions."""
        if asyncio.iscoroutinefunction(handler):
            return await handler(context)
        return handler(context)


# --- Example: Study Session Workflow ---
async def explain_concept(ctx: dict) -> dict:
    """Simulate the Concept Explainer skill."""
    topic = ctx.get("topic", "unknown")
    return {"explanation": f"Core concepts of {topic} explained clearly."}


async def socratic_question(ctx: dict) -> dict:
    """Simulate the Socratic Tutor skill."""
    explanation = ctx.get("explain", {}).get("explanation", "")
    return {"question": f"Based on the explanation, what do you think is the key idea?"}


async def quiz_learner(ctx: dict) -> dict:
    """Simulate the Quiz Master skill."""
    return {"score": 0.85, "feedback": "Good understanding, review edge cases."}


async def record_progress(ctx: dict) -> dict:
    """Simulate the Progress Motivator skill."""
    score = ctx.get("quiz", {}).get("score", 0)
    return {"xp_earned": int(score * 100), "message": "Great study session!"}


async def main():
    """Run a complete Study Session workflow."""
    workflow = WorkflowOrchestrator("Study Session")
    workflow.add_step("explain", explain_concept)
    workflow.add_step("socratic", socratic_question, depends_on=["explain"])
    workflow.add_step("quiz", quiz_learner, depends_on=["socratic"])
    workflow.add_step("progress", record_progress, depends_on=["quiz"])

    result = await workflow.execute({"topic": "recursion", "learner_id": "s7"})

    print(f"Workflow: {result.workflow_name}")
    print(f"Success: {result.success}")
    print(f"Duration: {result.total_duration_ms}ms\n")
    for step in result.steps:
        status_icon = "OK" if step.status == StepStatus.COMPLETED else "FAIL"
        print(f"  [{status_icon}] {step.step_name}: {step.output}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Key Takeaways

1. **Agentic workflows compose multiple skills into multi-step processes** -- individual skills are building blocks; workflows assemble them into complete solutions.
2. **Four patterns cover most designs** -- Chain for sequential dependencies, Fan-Out/In for parallelism, Router for conditional logic, and Loop for iterative refinement.
3. **Error handling is not optional** -- production workflows must implement retry with backoff, fallback handlers, and circuit breakers to survive real-world failures.
4. **Parallel execution reduces latency** -- independent steps should run simultaneously, but shared state must be synchronized.
5. **Dependency graphs prevent execution errors** -- the orchestrator must resolve step dependencies before execution to avoid deadlocks and data races.

## Check Your Understanding

Before moving on, make sure you can answer:

1. Why is a workflow orchestrator better than hardcoding a pipeline of skill calls?
2. Describe each of the four workflow patterns and give a concrete example for each.
3. When should you use retry vs. fallback vs. circuit breaker for error handling?
4. How does the orchestrator determine which steps can run in parallel?
5. What would happen if you added a circular dependency (Step A depends on Step B, Step B depends on Step A)?

## Next Steps

In the final chapter, you will learn how to take everything you have built -- skills, workflows, and the full agent system -- and **deploy it to production**. You will cover deployment platforms, monitoring and observability, scaling strategies, security hardening, and cost optimization.

Ready to ship? Continue to Chapter 9!
