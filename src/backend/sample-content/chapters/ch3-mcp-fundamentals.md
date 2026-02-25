---
chapter_id: ch3-mcp-fundamentals
title: MCP Fundamentals
module: 1
order: 3
difficulty: beginner
estimated_read_time: 18
word_count: 2000
tags: ["mcp", "protocol", "tools", "integration"]
prerequisites: ["ch1-intro-to-agents", "ch2-agent-factory-architecture"]
learning_objectives:
  - "Understand what MCP is and why it matters"
  - "Learn the core MCP architecture: Host, Server, and Client"
  - "Know how to define tools with JSON Schema"
  - "Understand resources and prompts in MCP"
created_at: 2026-01-10T00:00:00Z
updated_at: 2026-01-15T12:00:00Z
---

# MCP Fundamentals

## Overview

In Chapter 2, you learned that the Action layer is where agents interact with external systems. But how does an agent discover what tools are available and how to call them? That is the problem the **Model Context Protocol (MCP)** solves. MCP provides a universal, standardized way for AI agents to connect to tools, data sources, and services.

## What You'll Learn

- What MCP is and the problem it solves
- The three core components: Host, Server, and Client
- How tools are defined using JSON Schema
- The role of Resources and Prompts in MCP
- How to build a simple MCP server

## Concepts

### Concept 1: What is MCP and Why Does It Exist?

Before MCP, every AI tool integration was custom-built. Want your agent to search the web? Write a custom adapter. Read a database? Another adapter. Access a file system? Yet another one. This led to:

- **Fragmentation**: Every agent framework had its own tool format
- **Duplication**: The same tool had to be re-implemented for each platform
- **Brittleness**: Changes to a tool broke every agent using it

**MCP fixes this** by defining a single protocol that any agent can use to discover and invoke any tool. Think of MCP as the USB standard for AI agents--one connector, universal compatibility.

| Before MCP | With MCP |
|------------|----------|
| Custom adapters per tool | One standard protocol |
| Tools locked to one framework | Tools work across all MCP hosts |
| Manual tool documentation | Self-describing tools via schema |
| No runtime discovery | Dynamic tool discovery |
| Fragile integrations | Versioned, stable contracts |

### Concept 2: The MCP Architecture

MCP has three core components that work together:

**MCP Host**: The AI application or agent that needs to use tools. The Host initiates connections to Servers and invokes tools on behalf of the user. Examples include Claude Desktop, an IDE plugin, or your own custom agent.

**MCP Client**: A library embedded inside the Host that handles the protocol details--serialization, transport, error handling. You typically use an SDK rather than implementing the Client from scratch.

**MCP Server**: A standalone process that exposes tools, resources, and prompts. Each Server is a specialist: one might handle file operations, another might handle database queries, and a third might handle web searches.

```
+---------------------------------------------------+
|                   MCP Host                        |
|               (Your AI Agent)                     |
|                                                   |
|  +-----------+  +-----------+  +-----------+      |
|  |MCP Client |  |MCP Client |  |MCP Client |      |
|  +-----+-----+  +-----+-----+  +-----+-----+      |
+---------|--------------|--------------|-----------+
          |              |              |
          v              v              v
   +-----------+  +-----------+  +-----------+
   |MCP Server |  |MCP Server |  |MCP Server |
   |  (Files)  |  |(Database) |  |  (Web)    |
   +-----------+  +-----------+  +-----------+
```

A single Host can connect to multiple Servers simultaneously, giving the agent access to a wide range of capabilities.

### Concept 3: Tool Definition with JSON Schema

The heart of MCP is **tool definition**. Every tool exposed by an MCP Server is described using JSON Schema, which specifies:

- **name**: A unique identifier for the tool
- **description**: A human-readable explanation of what it does
- **inputSchema**: A JSON Schema defining the expected parameters
- **annotations**: Optional metadata like read-only hints or cost estimates

Here is what a tool definition looks like:

```json
{
  "name": "search_course_content",
  "description": "Search through course chapters and materials by keyword or topic. Returns matching sections with relevance scores.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The search term or topic to look for"
      },
      "chapter_id": {
        "type": "string",
        "description": "Optional: limit search to a specific chapter"
      },
      "max_results": {
        "type": "integer",
        "description": "Maximum number of results to return",
        "default": 5
      }
    },
    "required": ["query"]
  }
}
```

The JSON Schema gives the AI model enough information to decide when and how to call the tool--without any custom code on the model side.

### Concept 4: Resources and Prompts

MCP is not just about tools. It also defines two other primitives:

**Resources** are read-only data sources that an MCP Server can expose. They are identified by URIs and can represent files, database records, API responses, or any structured data. Resources let agents pull in context without executing actions.

```json
{
  "uri": "course://chapters/ch1-intro-to-agents",
  "name": "Chapter 1: Introduction to AI Agents",
  "mimeType": "text/markdown",
  "description": "Full content of chapter 1"
}
```

**Prompts** are reusable prompt templates that an MCP Server can offer. They help standardize how agents interact with certain tools or data, ensuring consistent and high-quality interactions.

```json
{
  "name": "explain_concept",
  "description": "Generate an explanation for a course concept",
  "arguments": [
    {
      "name": "concept",
      "description": "The concept to explain",
      "required": true
    },
    {
      "name": "difficulty",
      "description": "Learner level: beginner, intermediate, or advanced",
      "required": false
    }
  ]
}
```

Together, Tools + Resources + Prompts give an MCP Server a complete vocabulary for exposing capabilities to agents.

## Hands-On Example

Here is a simplified MCP server written in Python using the MCP SDK pattern:

```python
# course_mcp_server.py -- A simple MCP server for course content

from typing import Any

# Simulated course content store
COURSE_CHAPTERS = {
    "ch1": {"title": "Intro to Agents", "content": "AI agents are..."},
    "ch2": {"title": "Agent Factory", "content": "The 8-layer framework..."},
    "ch3": {"title": "MCP Fundamentals", "content": "MCP is a protocol..."},
}

def list_tools() -> list[dict]:
    """Expose available tools to MCP clients."""
    return [
        {
            "name": "search_content",
            "description": "Search course chapters by keyword",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term"},
                },
                "required": ["query"],
            },
        },
        {
            "name": "get_chapter",
            "description": "Retrieve a specific chapter by ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chapter_id": {"type": "string", "description": "Chapter ID"},
                },
                "required": ["chapter_id"],
            },
        },
    ]

def call_tool(name: str, arguments: dict) -> Any:
    """Handle tool invocations from MCP clients."""
    if name == "search_content":
        query = arguments["query"].lower()
        results = []
        for cid, chapter in COURSE_CHAPTERS.items():
            if query in chapter["title"].lower() or query in chapter["content"].lower():
                results.append({"chapter_id": cid, "title": chapter["title"]})
        return {"results": results, "count": len(results)}

    elif name == "get_chapter":
        chapter_id = arguments["chapter_id"]
        if chapter_id in COURSE_CHAPTERS:
            return COURSE_CHAPTERS[chapter_id]
        return {"error": f"Chapter {chapter_id} not found"}

    return {"error": f"Unknown tool: {name}"}

# Example usage (simulating an MCP client call)
print(call_tool("search_content", {"query": "agent"}))
# Output: {"results": [{"chapter_id": "ch1", ...}, ...], "count": 2}
```

In a real deployment, this server would run as a separate process and communicate with the Host over stdio or HTTP using the MCP wire protocol. The SDK handles all the serialization for you.

## Key Takeaways

1. **MCP is a universal standard**: One protocol for all agent-tool interactions
2. **Three components**: Host (agent), Client (library), Server (tool provider)
3. **JSON Schema powers discovery**: Tools describe themselves so agents know how to call them
4. **Resources and Prompts complement Tools**: Providing data and templates alongside executable actions
5. **Modular by design**: Each MCP Server is an independent, reusable capability

## Check Your Understanding

Before moving on, make sure you can answer:

1. What problem does MCP solve that custom tool adapters do not?
2. What are the three core components of the MCP architecture?
3. How does JSON Schema enable tool discovery?
4. What is the difference between a Tool and a Resource in MCP?

## Next Steps

In the next chapter, you'll put MCP to work by building your first agent skill--the **Concept Explainer**. You'll see how MCP tools, resources, and prompt templates come together to create an intelligent teaching assistant.

Ready to build your first skill? Continue to Chapter 4!
