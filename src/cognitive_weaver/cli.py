#!/usr/bin/env python3
"""
Cognitive Weaver CLI - Main entry point for the AI-powered Obsidian knowledge graph structuring engine
"""

import typer
from pathlib import Path
from typing import Optional
import asyncio
from .monitor import VaultMonitor
from .config import load_config

app = typer.Typer(help="Cognitive Weaver - AI-powered Obsidian knowledge graph structuring engine")

@app.command()
def start(
    vault_path: str = typer.Argument(..., help="Path to your Obsidian vault directory"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file"),
    watch: bool = typer.Option(True, "--watch/--no-watch", help="Enable file watching mode"),
    batch: bool = typer.Option(False, "--batch", "-b", help="Process entire vault in batch mode")
):
    """
    Start the Cognitive Weaver service to monitor and process Obsidian notes.
    """
    try:
        # Load configuration
        config = load_config(config_file)
        
        vault_path = Path(vault_path).absolute()
        if not vault_path.exists():
            typer.echo(f"Error: Vault path '{vault_path}' does not exist.")
            raise typer.Exit(1)
        
        typer.echo(f"Starting Cognitive Weaver for vault: {vault_path}")
        typer.echo("Press Ctrl+C to stop the service.")
        
        # Initialize monitor
        monitor = VaultMonitor(vault_path, config)
        
        if batch:
            typer.echo("Running in batch mode...")
            asyncio.run(monitor.process_entire_vault())
        elif watch:
            typer.echo("Starting file watcher...")
            monitor.start_watching()
        else:
            typer.echo("No action specified. Use --watch or --batch.")
            
    except KeyboardInterrupt:
        typer.echo("\nShutting down Cognitive Weaver...")
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)

@app.command()
def version():
    """Show the version of Cognitive Weaver."""
    from . import __version__
    typer.echo(f"Cognitive Weaver v{__version__}")

if __name__ == "__main__":
    app()
