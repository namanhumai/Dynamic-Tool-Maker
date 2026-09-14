import asyncio
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from graph import create_workflow
from evals import evaluate_meta_agent

load_dotenv()
console = Console()

async def main():
    console.print(Panel.fit(
        "[bold cyan]🛠️ META-TOOLMAKER: FAST-MCP 2.0 SYNTHESIZER[/bold cyan]\n"
        "[dim]Agentic Infrastructure • Dynamic Server Synthesis • Self-Healing Loop[/dim]",
        border_style="cyan"
    ))

    # Cleaning up any leftover server code from previous runs
    if os.path.exists("dynamic_server.py"):
        os.remove("dynamic_server.py")

    console.print("[yellow]1. Initializing the LangGraph Orchestrator...[/yellow]")
    app = await create_workflow()

    # The zero-shot mathematical/geo task that requires custom tools to solve correctly.
    task = "Calculate the exact Haversine distance in kilometers between London (51.5074, -0.1278) and Tokyo (35.6764, 139.6500). Then, calculate the prime factorization of that exact distance rounded to the nearest integer."
    
    state = {
        "task": task,
        "tool_code": "",
        "error_trace": "",
        "execution_result": "",
        "iterations": 0
    }

    console.print(f"\n[bold white on purple] TARGET TASK: [/bold white on purple] {task}\n")
    console.print("[bold yellow]--- LIVE CAPABILITY SYNTHESIS STREAM ---[/bold yellow]")

    # Watch the agent process the graph live
    async for event in app.astream(state):
        for node_name, node_state in event.items():
            if node_name == "architect_node":
                console.print(f"\n  [magenta]▸ TOOL ARCHITECT (Attempt {node_state['iterations']}):[/magenta] Wrote new FastMCP 2.0 Server to disk.")
                code_snippet = node_state['tool_code'].split('\n')[:7]
                console.print("    [dim]" + "\n    ".join(code_snippet) + "\n    ...[/dim]")
                
            elif node_name == "executor_node":
                err = node_state.get('error_trace')
                if err == "SUCCESS":
                    console.print("  [bold green]▸ SUBPROCESS EXECUTOR:[/bold green] MCP 2.0 Server booted! Sub-agent successfully utilized the dynamic tools.")
                    console.print(f"  [bold cyan]▸ FINAL ANSWER:[/bold cyan] {node_state['execution_result']}")
                else:
                    console.print(f"  [bold red]▸ SUBPROCESS EXECUTOR CRASH:[/bold red] {err}")
                    console.print("  [magenta]↻ ROUTER:[/magenta] Routing stack trace back to Architect for self-healing rewrite...")

    final_state = await app.ainvoke(state)
    
    console.print("\n[bold yellow]--- SYNTHESIZED FAST-MCP 2.0 CODE (dynamic_server.py) ---[/bold yellow]")
    syntax = Syntax(final_state["tool_code"], "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, border_style="green"))

    console.print("\n[yellow]3. Running LLM-as-a-Judge Audit...[/yellow]")
    eval_result = await evaluate_meta_agent(
        task=task,
        tool_code=final_state["tool_code"],
        execution_result=final_state["execution_result"]
    )
    
    # Rendering the QA Audit Table
    eval_table = Table(title="Agent Capability & Protocol Audit", border_style="blue")
    eval_table.add_column("Metric", style="bold white")
    eval_table.add_column("Result", style="cyan")
    
    score_color = "green" if eval_result.score >= 4 else "red"
    eval_table.add_row("Execution Accuracy", f"[{score_color}]{eval_result.score} / 5[/{score_color}]")
    eval_table.add_row("Valid FastMCP 2.0 Syntax?", str(eval_result.valid_mcp2_server))
    eval_table.add_row("Judge Reasoning", eval_result.reasoning)
    console.print(eval_table)
    console.print()

if __name__ == "__main__":
    asyncio.run(main())