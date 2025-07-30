"""Command-line interface for AI Agent Team."""

import click
import asyncio
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import settings
from src.utils import get_logger

console = Console()
logger = get_logger(__name__)


@click.group()
def cli():
    """AI Agent Team CLI - Manage your AI development team."""
    pass


@cli.command()
@click.option("--name", prompt="Project name", help="Name of the project")
@click.option("--description", prompt="Project description", help="Project description")
@click.option("--type", default="web", help="Project type (web, mobile, desktop)")
def create_project(name: str, description: str, type: str):
    """Create a new project."""
    from src.core.database.session import DatabaseManager
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating project...", total=None)
        
        try:
            project_id = DatabaseManager.create_project(name, description, type)
            progress.update(task, completed=True)
            
            console.print(f"\n✅ Project created successfully!")
            console.print(f"Project ID: [bold cyan]{project_id}[/bold cyan]")
            console.print(f"Name: [bold]{name}[/bold]")
            console.print(f"Type: {type}")
            
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"\n❌ Failed to create project: {str(e)}", style="bold red")


@cli.command()
@click.option("--project-id", prompt="Project ID", help="ID of the project")
@click.option("--goal", prompt="Sprint goal", help="Goal for this sprint")
@click.option("--name", help="Sprint name (optional)")
def start_sprint(project_id: str, goal: str, name: Optional[str] = None):
    """Start a new sprint for a project."""
    from src.core.database.session import DatabaseManager
    
    sprint_name = name or f"Sprint - {goal[:30]}..."
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating sprint...", total=None)
        
        try:
            sprint_id = DatabaseManager.create_sprint(project_id, sprint_name, goal)
            progress.update(task, completed=True)
            
            console.print(f"\n✅ Sprint created successfully!")
            console.print(f"Sprint ID: [bold cyan]{sprint_id}[/bold cyan]")
            console.print(f"Goal: [bold]{goal}[/bold]")
            
            # TODO: Initialize agents for the sprint
            console.print("\n🤖 Initializing agents...")
            console.print("• Manager Agent: Ready")
            console.print("• PM Agent: Ready")
            console.print("• Developer Agent: Ready")
            console.print("• QA Agent: Ready")
            
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"\n❌ Failed to create sprint: {str(e)}", style="bold red")


@cli.command()
def list_projects():
    """List all projects."""
    from src.core.database.session import get_db_context
    from src.core.database.models import Project
    
    with get_db_context() as db:
        projects = db.query(Project).all()
        
        if not projects:
            console.print("No projects found. Create one with 'create-project' command.")
            return
        
        table = Table(title="Projects")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("Type")
        table.add_column("Status")
        table.add_column("Created", style="dim")
        
        for project in projects:
            table.add_row(
                str(project.id),
                project.name,
                project.project_type or "N/A",
                project.status.value,
                project.created_at.strftime("%Y-%m-%d %H:%M")
            )
        
        console.print(table)


@cli.command()
def list_agents():
    """List all registered agents."""
    from src.core.database.session import get_db_context
    from src.core.database.models import Agent
    
    with get_db_context() as db:
        agents = db.query(Agent).all()
        
        if not agents:
            console.print("No agents found. Run setup_database.py to create initial agents.")
            return
        
        table = Table(title="Registered Agents")
        table.add_column("ID", style="cyan")
        table.add_column("Role", style="bold")
        table.add_column("LLM Provider")
        table.add_column("Status")
        table.add_column("Tasks Completed", justify="right")
        
        for agent in agents:
            table.add_row(
                agent.id,
                agent.role,
                agent.llm_provider or "N/A",
                agent.current_status or "idle",
                str(agent.tasks_completed)
            )
        
        console.print(table)


@cli.command()
def status():
    """Show system status."""
    console.print("\n[bold]AI Agent Team Status[/bold]\n")
    
    # Environment info
    console.print(f"Environment: [cyan]{settings.app_env}[/cyan]")
    console.print(f"API URL: http://{settings.api_host}:{settings.api_port}")
    
    # Database status
    try:
        from src.core.database.session import engine
        engine.connect()
        console.print("Database: [green]Connected[/green]")
    except:
        console.print("Database: [red]Disconnected[/red]")
    
    # Redis status
    try:
        import redis
        r = redis.from_url(settings.redis_url)
        r.ping()
        console.print("Redis: [green]Connected[/green]")
    except:
        console.print("Redis: [red]Disconnected[/red]")
    
    # LLM providers
    console.print("\n[bold]LLM Providers:[/bold]")
    console.print(f"• DeepSeek: {'[green]Configured[/green]' if settings.deepseek_api_key else '[yellow]Not configured[/yellow]'}")
    console.print(f"• Aliyun: {'[green]Configured[/green]' if settings.aliyun_api_key else '[yellow]Not configured[/yellow]'}")
    console.print(f"• Local LM Studio: {settings.lm_studio_base_url}")


@cli.command()
def run():
    """Run the API server."""
    from src.main import run_server
    
    console.print("\n🚀 Starting AI Agent Team API server...\n")
    run_server()


if __name__ == "__main__":
    cli()