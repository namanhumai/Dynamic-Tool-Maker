# Dynamic-Tool-Maker
An agent that encounters a task it lacks the tools to solve, autonomously writes a new FastMCP server on the fly, tests and boots it in an isolated subprocess, binds to it dynamically as an MCP client, executes the task, and shuts it down.
