"""
Knowledge Graph module for Cognitive Weaver
Handles storage and management of user profile as a graph structure
with nodes (concepts) and edges (relationships)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class GraphNode:
    """Represents a node in the knowledge graph"""
    id: str
    label: str
    type: str
    importance: float = 1.0
    first_seen: str = None
    last_updated: str = None
    occurrences: int = 1

@dataclass
class GraphEdge:
    """Represents an edge in the knowledge graph"""
    source: str
    target: str
    relationship: str
    strength: float = 1.0
    first_seen: str = None
    last_updated: str = None
    occurrences: int = 1

class KnowledgeGraph:
    """Manages the user's personal knowledge graph with nodes and edges"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Set[str] = set()  # Store edges as "source|target|relationship" for uniqueness
        self.edge_objects: Dict[str, GraphEdge] = {}
        self.storage_path = storage_path or Path("user_knowledge_graph.json")
        
        # Load existing graph if available
        self.load()
    
    def add_node(self, node_id: str, label: str, node_type: str = "concept", importance: float = 1.0) -> GraphNode:
        """
        Add or update a node in the graph.
        
        Args:
            node_id (str): The unique identifier for the node.
            label (str): The display label for the node.
            node_type (str, optional): The type of the node (e.g., "concept"). Defaults to "concept".
            importance (float, optional): The importance weight of the node. Defaults to 1.0.
        
        Returns:
            GraphNode: The added or updated node object.
        """
        current_time = datetime.now().isoformat()
        
        if node_id in self.nodes:
            # Update existing node
            node = self.nodes[node_id]
            node.last_updated = current_time
            node.occurrences += 1
            # Gradually adjust importance based on new occurrences
            node.importance = (node.importance * (node.occurrences - 1) + importance) / node.occurrences
        else:
            # Create new node
            node = GraphNode(
                id=node_id,
                label=label,
                type=node_type,
                importance=importance,
                first_seen=current_time,
                last_updated=current_time,
                occurrences=1
            )
            self.nodes[node_id] = node
        
        return node
    
    def add_edge(self, source: str, target: str, relationship: str, strength: float = 1.0) -> Optional[GraphEdge]:
        """
        Add or update an edge between nodes.
        
        Args:
            source (str): The source node ID.
            target (str): The target node ID.
            relationship (str): The type of relationship between nodes.
            strength (float, optional): The strength of the relationship. Defaults to 1.0.
        
        Returns:
            Optional[GraphEdge]: The added or updated edge object, or None if nodes don't exist.
        """
        # Check if both nodes exist
        if source not in self.nodes or target not in self.nodes:
            return None
        
        edge_key = f"{source}|{target}|{relationship}"
        current_time = datetime.now().isoformat()
        
        if edge_key in self.edges:
            # Update existing edge
            edge = self.edge_objects[edge_key]
            edge.last_updated = current_time
            edge.occurrences += 1
            # Gradually adjust strength based on new occurrences
            edge.strength = (edge.strength * (edge.occurrences - 1) + strength) / edge.occurrences
        else:
            # Create new edge
            edge = GraphEdge(
                source=source,
                target=target,
                relationship=relationship,
                strength=strength,
                first_seen=current_time,
                last_updated=current_time,
                occurrences=1
            )
            self.edges.add(edge_key)
            self.edge_objects[edge_key] = edge
        
        return edge
    
    def to_json(self) -> dict:
        """
        Convert the graph to JSON format.
        
        Returns:
            dict: A dictionary representation of the graph with nodes and edges.
        """
        return {
            "nodes": [asdict(node) for node in self.nodes.values()],
            "edges": [asdict(edge) for edge in self.edge_objects.values()]
        }
    
    def save(self, path: Optional[Path] = None):
        """
        Save the graph to a JSON file.
        
        Args:
            path (Optional[Path]): The path to save the graph to. If None, uses the default storage path.
        """
        save_path = path or self.storage_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_json(), f, ensure_ascii=False, indent=2)
    
    def load(self, path: Optional[Path] = None):
        """
        Load the graph from a JSON file.
        
        Args:
            path (Optional[Path]): The path to load the graph from. If None, uses the default storage path.
        """
        load_path = path or self.storage_path
        
        if not load_path.exists():
            return
        
        try:
            with open(load_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load nodes
            for node_data in data.get("nodes", []):
                node = GraphNode(**node_data)
                self.nodes[node.id] = node
            
            # Load edges
            for edge_data in data.get("edges", []):
                edge = GraphEdge(**edge_data)
                edge_key = f"{edge.source}|{edge.target}|{edge.relationship}"
                self.edges.add(edge_key)
                self.edge_objects[edge_key] = edge
                
        except Exception as e:
            print(f"Error loading knowledge graph: {e}")
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """
        Get a node by ID.
        
        Args:
            node_id (str): The ID of the node to retrieve.
        
        Returns:
            Optional[GraphNode]: The node object if found, otherwise None.
        """
        return self.nodes.get(node_id)
    
    def get_edges(self, node_id: str = None) -> List[GraphEdge]:
        """
        Get all edges or edges for a specific node.
        
        Args:
            node_id (str, optional): The node ID to filter edges by. If None, returns all edges.
        
        Returns:
            List[GraphEdge]: A list of edge objects.
        """
        if node_id is None:
            return list(self.edge_objects.values())
        
        return [edge for edge in self.edge_objects.values() 
                if edge.source == node_id or edge.target == node_id]
    
    def export_json(self) -> str:
        """
        Export the graph as JSON string.
        
        Returns:
            str: A JSON string representation of the graph.
        """
        return json.dumps(self.to_json(), ensure_ascii=False, indent=2)
    
    def clear(self):
        """
        Clear the graph by removing all nodes and edges.
        """
        self.nodes.clear()
        self.edges.clear()
        self.edge_objects.clear()
