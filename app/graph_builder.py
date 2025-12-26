"""
Knowledge Graph Builder - Core graph management
"""

import networkx as nx
from typing import Dict, List, Any, Optional
from collections import defaultdict
from app.models import Node, Edge

class KnowledgeGraph:
    """Manages the knowledge graph structure"""
    
    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph
        self.nodes_data: Dict[str, Dict] = {}
        self.edges_data: List[Dict] = []
    
    def add_node(self, node_id: str, node_type: str, properties: Dict[str, Any] = None):
        """Add a node to the graph"""
        if properties is None:
            properties = {}
        
        self.graph.add_node(node_id, node_type=node_type, **properties)
        self.nodes_data[node_id] = {
            'id': node_id,
            'type': node_type,
            'properties': properties
        }
    
    def add_edge(self, source: str, target: str, relationship: str = 'related_to', weight: float = 1.0):
        """Add an edge between two nodes"""
        if source not in self.graph or target not in self.graph:
            raise ValueError(f"Both nodes must exist: {source} -> {target}")
        
        self.graph.add_edge(source, target, relationship=relationship, weight=weight)
        self.edges_data.append({
            'source': source,
            'target': target,
            'relationship': relationship,
            'weight': weight
        })
    
    def remove_node(self, node_id: str):
        """Remove a node from the graph"""
        if node_id in self.graph:
            self.graph.remove_node(node_id)
            self.nodes_data.pop(node_id, None)
            # Remove associated edges
            self.edges_data = [
                e for e in self.edges_data 
                if e['source'] != node_id and e['target'] != node_id
            ]
    
    def get_node_count(self) -> int:
        """Get total number of nodes"""
        return self.graph.number_of_nodes()
    
    def get_edge_count(self) -> int:
        """Get total number of edges"""
        return self.graph.number_of_edges()
    
    def get_node_types(self) -> Dict[str, int]:
        """Get count of nodes by type"""
        type_counts = defaultdict(int)
        for node_id in self.graph.nodes():
            node_type = self.graph.nodes[node_id].get('node_type', 'unknown')
            type_counts[node_type] += 1
        return dict(type_counts)
    
    def get_most_connected_nodes(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get the n most connected nodes"""
        degrees = dict(self.graph.degree())
        sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:n]
        return [{'node': node, 'connections': degree} for node, degree in sorted_nodes]
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get all neighbors of a node"""
        if node_id not in self.graph:
            return []
        return list(self.graph.neighbors(node_id))
    
    def find_path(self, source: str, target: str) -> Optional[List[str]]:
        """Find shortest path between two nodes"""
        try:
            return nx.shortest_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return None
    
    def get_subgraph(self, node_ids: List[str]) -> nx.DiGraph:
        """Get a subgraph containing specified nodes"""
        return self.graph.subgraph(node_ids)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary for serialization"""
        return {
            'nodes': list(self.nodes_data.values()),
            'edges': self.edges_data
        }
    
    def load_from_dict(self, data: Dict[str, Any]):
        """Load graph from dictionary"""
        self.graph.clear()
        self.nodes_data.clear()
        self.edges_data.clear()
        
        # Load nodes
        for node_data in data.get('nodes', []):
            self.add_node(
                node_data['id'],
                node_data['type'],
                node_data.get('properties', {})
            )
        
        # Load edges
        for edge_data in data.get('edges', []):
            self.add_edge(
                edge_data['source'],
                edge_data['target'],
                edge_data.get('relationship', 'related_to'),
                edge_data.get('weight', 1.0)
            )

