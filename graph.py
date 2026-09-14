import sys
import asyncio
from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

# 1> State Definition 
class GraphState(TypedDict):
    task: str
    tool_code: str
    error_trace: str
    execution_result:str
    iterations: int

# 2. Strict JSON output structure for the LLM Architecture

class ToolCode(BaseModel):
    python_code: str = Field(description="The complete, runnable Python code for the FastMCP 2.0 server.")

async def create_workflow():
    # WE use a model for writing backend protocol code
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")


    # Node 1: The code generator (architect)
    async def architect_node(state: GraphState):
        prompt = ChatPromptTemplate.from_template(
            "You are an elite AI Tool Architect building a Model Context Protocol (MCP 2.0) Server.\n"
            "The user has a complex mathematical/computational task. You currently have no tools.\n"
            "User Task: {task}\n\n"
            "Write a standalone Python script using FastMCP 2.0 that provides the exact tools needed to solve this.\n"
            "Strict FastMCP 2.0 Requirements:\n"
            "1. Use ONLY standard Python libraries (math, datetime, etc.).\n"
            "2. Import exactly: from fastmcp import FastMCP\n"
            "3. Initialize exactly: mcp = FastMCP('DynamicTools')\n"
            "4. Expose tools using the @mcp.tool() decorator.\n"
            "5. You MUST include detailed docstrings and standard Python type hints (e.g. def calc(a: float) -> float:).\n"
            "6. End the script with exactly:\nif __name__ == '__main__':\n    mcp.run(transport='stdio')\n\n"
            "Previous Execution Error (if any, read the stack trace and fix your code!): {error}\n\n"
            "Output ONLY the raw Python code."
        )     

        chain = prompt | llm.with_structured_output(ToolCode)
        response = await chain.ainvoke({
            "task": state["task"],
            "error": state.get("error_trace", "None - this is the first attempt.")
        })

        # Strip markdown if the LLM hallucinated code blocks inside the JSON string
        code = response.python_code.replace("```python","").replace("```","").strip()

        # Autonomously write the FastMCP server file 
        with open("dynamic_server.py", "w", encoding="utf-8") as f:
            f.write(code)

        return {"tool_code": code,"iterations": state.get("iterations", 0) + 1, "error_trace": ""}


    # Node 2: The subproces Executor (client)
    async def executor_node(state: GraphState):
        # Mounting the MCP 2.0 server we JUST created on disk using the stdio transport
        client = MultiServerMCPClient({
          "dynamic_server":{
              "transport": "stdio",
              "command":sys.executable,
               'args':['dynamic_server.py']
        }
    })

        try:
            # Connecting via Langchain MCP adapters and extracting tools
            tools = await client.get_tools()
            
            # Creating a nested LangGraph ReAct agent to execute the user's task with the new tools
            agent = create_agent(llm, tools)
            result = await agent.ainvoke({"messages": [("user", state["task"])]})
            
            final_answer = result["messages"][-1].content
            return {"execution_result": final_answer, "error_trace": "SUCCESS"}
            
        except Exception as e:
            # If the generated MCP server crashes (SyntaxError, runtime error, etc.), capture the trace
            return {"error_trace": f"Server crash or protocol execution error: {str(e)}"}
         


    # Routing: Self healing loop
    def route_execution(state: GraphState):
        if state['error_trace'] == "SUCCESS":
            return END
        if state['iterations',0] >= 3:
            return END # Failsafe limit to prevent infinite loops which can occur
        return "architect_node" # CYCLE BACK with the error trace

    # 4. Compile the graph
    workflow = StateGraph(GraphState)
    workflow.add_node("architect_node",architect_node)
    workflow.add_node("executor_node",executor_node)

    workflow.set_entry_point("architect_node")
    workflow.add_edge("architect_node", "executor_node")
    workflow.add_conditional_edges("executor_node", route_execution)

    return workflow.compile()