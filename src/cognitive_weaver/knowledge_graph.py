"""
Cognitive Weaver 知识图谱模块
处理用户配置文件作为图结构的存储和管理，包含节点（概念）和边（关系）

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
    """表示知识图谱中的一个节点"""
    id: str
    label: str
    type: str
    importance: float = 1.0
    first_seen: str = None
    last_updated: str = None
    occurrences: int = 1

@dataclass
class GraphEdge:
    """表示知识图谱中的一条边"""
    source: str
    target: str
    relationship: str
    strength: float = 1.0
    first_seen: str = None
    last_updated: str = None
    occurrences: int = 1

class KnowledgeGraph:
    """管理用户的个人知识图谱，包含节点和边"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Set[str] = set()  # Store edges as "source|target|relationship" for uniqueness
        self.edge_objects: Dict[str, GraphEdge] = {}
        self.storage_path = storage_path or Path("user_knowledge_graph.json")
        
        # Load existing graph if available
        self.load()
    
    def add_node(self, node_id: str, label: str, node_type: str = "concept", importance: float = 1.0) -> GraphNode:
        """
        在图中添加或更新一个节点。
        
        参数:
            node_id (str): 节点的唯一标识符。
            label (str): 节点的显示标签。
            node_type (str, optional): 节点的类型（例如 "concept"）。默认为 "concept"。
            importance (float, optional): 节点的重要性权重。默认为 1.0。
        
        返回:
            GraphNode: 添加或更新的节点对象。
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
        在节点之间添加或更新一条边。
        
        参数:
            source (str): 源节点ID。
            target (str): 目标节点ID。
            relationship (str): 节点之间的关系类型。
            strength (float, optional): 关系的强度。默认为 1.0。
        
        返回:
            Optional[GraphEdge]: 添加或更新的边对象，如果节点不存在则返回 None。
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
        将图谱转换为JSON格式。
        
        返回:
            dict: 包含节点和边的图谱字典表示。
        """
        return {
            "nodes": [asdict(node) for node in self.nodes.values()],
            "edges": [asdict(edge) for edge in self.edge_objects.values()]
        }
    
    def save(self, path: Optional[Path] = None):
        """
        将图谱保存到JSON文件。
        
        参数:
            path (Optional[Path]): 保存图谱的路径。如果为 None，则使用默认存储路径。
        """
        save_path = path or self.storage_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_json(), f, ensure_ascii=False, indent=2)
    
    def load(self, path: Optional[Path] = None):
        """
        从JSON文件加载图谱。
        
        参数:
            path (Optional[Path]): 加载图谱的路径。如果为 None，则使用默认存储路径。
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
        通过ID获取节点。
        
        参数:
            node_id (str): 要检索的节点ID。
        
        返回:
            Optional[GraphNode]: 如果找到则返回节点对象，否则返回 None。
        """
        return self.nodes.get(node_id)
    
    def get_edges(self, node_id: str = None) -> List[GraphEdge]:
        """
        获取所有边或特定节点的边。
        
        参数:
            node_id (str, optional): 用于过滤边的节点ID。如果为 None，则返回所有边。
        
        返回:
            List[GraphEdge]: 边对象列表。
        """
        if node_id is None:
            return list(self.edge_objects.values())
        
        return [edge for edge in self.edge_objects.values() 
                if edge.source == node_id or edge.target == node_id]
    
    def export_json(self) -> str:
        """
        将图谱导出为JSON字符串。
        
        返回:
            str: 图谱的JSON字符串表示。
        """
        return json.dumps(self.to_json(), ensure_ascii=False, indent=2)
    
    def clear(self):
        """
        通过移除所有节点和边来清空图谱。
        """
        self.nodes.clear()
        self.edges.clear()
        self.edge_objects.clear()
