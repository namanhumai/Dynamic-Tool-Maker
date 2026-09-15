# Dynamic-Tool-Maker
An agent that encounters a task it lacks the tools to solve, autonomously writes a new FastMCP server on the fly, tests and boots it in an isolated subprocess, binds to it dynamically as an MCP client, executes the task, and shuts it down.

---

### 3. ToolMaker AI (Zero-Shot MCP Synthesizer)

**GitHub "About" (Description):**
> An experimental agentic workflow that writes its own backend. When faced with an impossible task, ToolMaker AI writes a custom FastMCP server, boots it in a subprocess, uses the newly generated tools to solve the problem, and shuts it down.

**`README.md`**

```markdown
# 🛠️ ToolMaker AI (Meta-Toolmaker)

Most AI agents are limited by the tools humans hardcode for them. If an agent needs to do complex prime factorization or calculate geospatial distances, and you didn't give it a calculator tool, it hallucinates and fails.

**ToolMaker AI fixes this by writing its own tools on the fly.** 

When given a complex task it can't solve zero-shot, the LangGraph orchestrator spins up an "Architect" agent. The Architect writes a complete, runnable Python script using the FastMCP 2.0 framework. The system then boots that newly created server in a local subprocess, dynamically binds to it via the Model Context Protocol, executes the task using the new tools, and tears the server down. 

If the code the Architect wrote has a SyntaxError or crashes? The stack trace is caught and routed *back* to the Architect to debug and rewrite itself. 

## 🏗️ Architecture

1. **Architect Node:** Generates `dynamic_server.py` based on the user's prompt, enforcing strict FastMCP 2.0 type hints and decorators.
2. **Subprocess Executor:** Uses `MultiServerMCPClient` to boot the generated script via `stdio`.
3. **Execution & Routing:** Connects a LangGraph ReAct sub-agent to the new tools. If it crashes, the graph cycles backward for self-healing.
4. **Judge:** Evaluates if the generated Python code actually solved the initial prompt without hallucinating.

## 💻 Tech Stack
* **Framework:** LangGraph
* **Protocol:** FastMCP 2.0 (Dynamic Server instantiation)
* **LLM:** Gemini (reasoning for writing backend protocol code)


