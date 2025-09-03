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
def process_folder(
    folder_path: str = typer.Argument(..., help="Path to the folder containing markdown files to process"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file")
):
    """
    Process all markdown files in a specific folder.
    """
    try:
        # Load configuration
        config = load_config(config_file)
        
        folder_path = Path(folder_path).absolute()
        if not folder_path.exists():
            typer.echo(f"Error: Folder path '{folder_path}' does not exist.")
            raise typer.Exit(1)
        
        if not folder_path.is_dir():
            typer.echo(f"Error: '{folder_path}' is not a directory.")
            raise typer.Exit(1)
        
        typer.echo(f"Processing folder: {folder_path}")
        
        # Initialize monitor with a dummy vault path (since we're processing a specific folder)
        monitor = VaultMonitor(folder_path, config)
        
        # Process the folder
        asyncio.run(monitor.process_folder(folder_path))
        
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)

@app.command()
def process_config_folders(
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file")
):
    """
    Process all markdown files in folders specified in the configuration file.
    """
    try:
        # Load configuration
        config = load_config(config_file)
        
        if not config.file_monitoring.folders_to_scan:
            typer.echo("No folders specified in configuration. Please add 'folders_to_scan' to your config.yaml.")
            raise typer.Exit(1)
        
        typer.echo(f"Processing folders from configuration: {config.file_monitoring.folders_to_scan}")
        
        # Initialize monitor with a dummy vault path (since we're processing specific folders)
        # Use the first folder as dummy vault path
        dummy_vault_path = Path(config.file_monitoring.folders_to_scan[0]).absolute()
        monitor = VaultMonitor(dummy_vault_path, config)
        
        # Process each folder
        for folder_path in config.file_monitoring.folders_to_scan:
            folder_path_obj = Path(folder_path).absolute()
            if not folder_path_obj.exists():
                typer.echo(f"Warning: Folder path '{folder_path_obj}' does not exist. Skipping.")
                continue
            
            if not folder_path_obj.is_dir():
                typer.echo(f"Warning: '{folder_path_obj}' is not a directory. Skipping.")
                continue
            
            typer.echo(f"Processing folder: {folder_path_obj}")
            asyncio.run(monitor.process_folder(folder_path_obj))
        
        typer.echo("All configured folders processed successfully.")
        
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)

@app.command()
def process_keywords(
    folder_path: str = typer.Argument(..., help="Path to the folder containing markdown files to process for keyword linking"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file")
):
    """
    Process keywords across all markdown files in a folder and create Obsidian links for similar concepts.
    """
    try:
        # Load configuration
        config = load_config(config_file)
        
        folder_path_obj = Path(folder_path).absolute()
        if not folder_path_obj.exists():
            typer.echo(f"Error: Folder path '{folder_path_obj}' does not exist.")
            raise typer.Exit(1)
        
        if not folder_path_obj.is_dir():
            typer.echo(f"Error: '{folder_path_obj}' is not a directory.")
            raise typer.Exit(1)
        
        typer.echo(f"Processing keywords in folder: {folder_path_obj}")
        
        # Initialize monitor with the folder path
        monitor = VaultMonitor(folder_path_obj, config)
        
        # Process keywords for the folder
        asyncio.run(monitor.process_keywords_for_folder(folder_path_obj))
        
        typer.echo("Keyword processing completed successfully.")
        
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
