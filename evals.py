from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class EvalResult(BaseModel):
    score: int = Field(description="1 to 5 score. 5 means perfect task execution without hallucination.")
    valid_mcp2_server: bool = Field(description="Did the code successfully implement a FastMCP 2.0 server without syntax errors?")
    reasoning: str = Field(description="Why this score was given")

async def evaluate_meta_agent(task: str, tool_code: str, execution_result: str) -> EvalResult:
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    
    prompt = ChatPromptTemplate.from_template(
        "You are an AI Engineering Manager evaluating a 'Meta-Toolmaker' agent.\n\n"
        "User Task: {task}\n\n"
        "Dynamically Generated Tool Code (FastMCP 2.0 Server):\n{code}\n\n"
        "Agent's Final Execution Result:\n{result}\n\n"
        "Evaluate two things:\n"
        "1. Does the code conform to FastMCP 2.0 standards (imports `FastMCP`, uses `@mcp.tool()`)?\n"
        "2. Does the final result accurately answer the user's task without hallucinations?\n"
    )
    
    chain = prompt | llm.with_structured_output(EvalResult)
    return await chain.ainvoke({
        "task": task,
        "code": tool_code,
        "result": execution_result
    })

