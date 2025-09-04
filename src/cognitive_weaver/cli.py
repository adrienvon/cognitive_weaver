#!/usr/bin/env python3
"""
Cognitive Weaver CLI - Main entry point for the AI-powered Obsidian knowledge graph structuring engine
"""

import typer
from pathlib import Path
from typing import Optional
import asyncio
import json
from .monitor import VaultMonitor
from .config import load_config
from .knowledge_graph import KnowledgeGraph

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
    
    Args:
        vault_path (str): Path to the Obsidian vault directory to monitor.
        config_file (Optional[str]): Path to a custom configuration file.
        watch (bool): Whether to enable file watching mode for real-time processing.
        batch (bool): Whether to process the entire vault in batch mode.
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
    
    Args:
        folder_path (str): Path to the folder containing markdown files to process.
        config_file (Optional[str]): Path to a custom configuration file.
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
    
    Args:
        config_file (Optional[str]): Path to a custom configuration file.
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
    
    Args:
        folder_path (str): Path to the folder containing markdown files to process.
        config_file (Optional[str]): Path to a custom configuration file.
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
def export_knowledge_graph(
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path for the knowledge graph"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file")
):
    """
    Export the user's knowledge graph to a JSON file.
    
    Args:
        output_file (Optional[str]): Output file path for the knowledge graph JSON.
        config_file (Optional[str]): Path to a custom configuration file.
    """
    try:
        # Load configuration
        config = load_config(config_file)
        
        # Initialize knowledge graph
        knowledge_graph = KnowledgeGraph()
        
        # Export to JSON
        graph_data = knowledge_graph.to_json()
        
        if output_file:
            output_path = Path(output_file).absolute()
            knowledge_graph.save(output_path)
            typer.echo(f"Knowledge graph exported to: {output_path}")
        else:
            # Print to stdout
            typer.echo(json.dumps(graph_data, ensure_ascii=False, indent=2))
            
    except Exception as e:
        typer.echo(f"Error exporting knowledge graph: {e}")
        raise typer.Exit(1)

@app.command()
def show_knowledge_graph(
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file")
):
    """
    Display the current knowledge graph structure.
    
    Args:
        config_file (Optional[str]): Path to a custom configuration file.
    """
    try:
        # Load configuration
        config = load_config(config_file)
        
        # Initialize knowledge graph
        knowledge_graph = KnowledgeGraph()
        
        # Get graph data
        graph_data = knowledge_graph.to_json()
        
        typer.echo("Knowledge Graph Summary:")
        typer.echo(f"Nodes: {len(graph_data['nodes'])}")
        typer.echo(f"Edges: {len(graph_data['edges'])}")
        typer.echo("")
        
        if graph_data['nodes']:
            typer.echo("Nodes:")
            for node in graph_data['nodes']:
                typer.echo(f"  - {node['id']} ({node['type']}): {node['label']} [Occurrences: {node['occurrences']}]")
        
        if graph_data['edges']:
            typer.echo("")
            typer.echo("Edges:")
            for edge in graph_data['edges']:
                typer.echo(f"  - {edge['source']} --[{edge['relationship']}]--> {edge['target']} [Strength: {edge['strength']:.2f}]")
                
    except Exception as e:
        typer.echo(f"Error showing knowledge graph: {e}")
        raise typer.Exit(1)

@app.command()
def clear_knowledge_graph(
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file")
):
    """
    Clear the current knowledge graph.
    
    Args:
        config_file (Optional[str]): Path to a custom configuration file.
    """
    try:
        # Load configuration
        config = load_config(config_file)
        
        # Initialize knowledge graph
        knowledge_graph = KnowledgeGraph()
        knowledge_graph.clear()
        knowledge_graph.save()
        
        typer.echo("Knowledge graph cleared successfully.")
        
    except Exception as e:
        typer.echo(f"Error clearing knowledge graph: {e}")
        raise typer.Exit(1)

@app.command()
def update_knowledge_graph(
    vault_path: str = typer.Argument(..., help="Path to your Obsidian vault directory"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file")
):
    """
    Update knowledge graph from all existing files, including those with relation links.
    
    Args:
        vault_path (str): Path to the Obsidian vault directory to update.
        config_file (Optional[str]): Path to a custom configuration file.
    """
    try:
        # Load configuration
        config = load_config(config_file)
        
        vault_path = Path(vault_path).absolute()
        if not vault_path.exists():
            typer.echo(f"Error: Vault path '{vault_path}' does not exist.")
            raise typer.Exit(1)
        
        typer.echo(f"Updating knowledge graph from vault: {vault_path}")
        
        # Initialize monitor
        monitor = VaultMonitor(vault_path, config)
        
        # Update knowledge graph from existing files
        asyncio.run(monitor.update_knowledge_graph_from_existing_files())
        
        typer.echo("Knowledge graph update completed successfully.")
        
    except Exception as e:
        typer.echo(f"Error updating knowledge graph: {e}")
        raise typer.Exit(1)

@app.command()
def version():
    """Show the version of Cognitive Weaver."""
    from . import __version__
    typer.echo(f"Cognitive Weaver v{__version__}")

if __name__ == "__main__":
    app()
