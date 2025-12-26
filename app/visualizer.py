"""
Graph Visualizer - Creates visualizations of the knowledge graph
"""

import networkx as nx
from typing import Dict, List, Any
import json

class GraphVisualizer:
    """Handles visualization of the knowledge graph"""
    
    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph
    
    def get_graph_data(self) -> Dict[str, Any]:
        """Get graph data in format suitable for visualization"""
        nodes = []
        edges = []
        
        # Prepare nodes
        for node_id in self.kg.graph.nodes():
            node_data = self.kg.graph.nodes[node_id]
            nodes.append({
                'id': node_id,
                'label': node_id,
                'type': node_data.get('node_type', 'concept'),
                'properties': {k: v for k, v in node_data.items() if k != 'node_type'},
                'degree': self.kg.graph.degree(node_id)
            })
        
        # Prepare edges
        for source, target in self.kg.graph.edges():
            edge_data = self.kg.graph.edges[source, target]
            edges.append({
                'source': source,
                'target': target,
                'relationship': edge_data.get('relationship', 'related_to'),
                'weight': edge_data.get('weight', 1.0)
            })
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def get_node_positions(self, layout: str = 'spring') -> Dict[str, List[float]]:
        """Get node positions for visualization"""
        if layout == 'spring':
            pos = nx.spring_layout(self.kg.graph, k=1, iterations=50)
        elif layout == 'circular':
            pos = nx.circular_layout(self.kg.graph)
        elif layout == 'hierarchical':
            pos = nx.nx_agraph.graphviz_layout(self.kg.graph, prog='dot')
        else:
            pos = nx.spring_layout(self.kg.graph)
        
        return {node: [float(pos[node][0]), float(pos[node][1])] for node in pos}
    
    def export_to_cytoscape(self) -> Dict[str, Any]:
        """Export graph in Cytoscape.js format"""
        graph_data = self.get_graph_data()
        return {
            'elements': {
                'nodes': [
                    {
                        'data': {
                            'id': node['id'],
                            'label': node['label'],
                            'type': node['type'],
                            **node['properties']
                        }
                    }
                    for node in graph_data['nodes']
                ],
                'edges': [
                    {
                        'data': {
                            'source': edge['source'],
                            'target': edge['target'],
                            'relationship': edge['relationship'],
                            'weight': edge['weight']
                        }
                    }
                    for edge in graph_data['edges']
                ]
            }
        }

