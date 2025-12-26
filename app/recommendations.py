"""
Recommendation Engine - Suggests what to learn next
"""

from typing import List, Dict, Any
from collections import defaultdict
import networkx as nx

class RecommendationEngine:
    """Generates learning recommendations based on the knowledge graph"""
    
    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph
    
    def get_recommendations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get learning recommendations"""
        recommendations = []
        
        # Strategy 1: Find nodes with prerequisites that are already learned
        recommendations.extend(self._recommend_by_prerequisites(limit))
        
        # Strategy 2: Find highly connected nodes that aren't learned yet
        recommendations.extend(self._recommend_by_connectivity(limit))
        
        # Strategy 3: Find nodes that bridge different knowledge areas
        recommendations.extend(self._recommend_by_bridging(limit))
        
        # Remove duplicates and sort by score
        unique_recs = {}
        for rec in recommendations:
            node_id = rec['node']
            if node_id not in unique_recs or rec['score'] > unique_recs[node_id]['score']:
                unique_recs[node_id] = rec
        
        return sorted(unique_recs.values(), key=lambda x: x['score'], reverse=True)[:limit]
    
    def _recommend_by_prerequisites(self, limit: int) -> List[Dict[str, Any]]:
        """Recommend nodes where prerequisites are met"""
        recommendations = []
        all_nodes = set(self.kg.graph.nodes())
        
        for node_id in all_nodes:
            # Check if this node has prerequisites
            in_edges = list(self.kg.graph.in_edges(node_id))
            prerequisite_edges = [
                e for e in in_edges 
                if self.kg.graph.edges[e].get('relationship') == 'prerequisite'
            ]
            
            if prerequisite_edges:
                # Check if all prerequisites are met
                prerequisites = [e[0] for e in prerequisite_edges]
                if all(prereq in all_nodes for prereq in prerequisites):
                    recommendations.append({
                        'node': node_id,
                        'reason': f'Prerequisites met: {", ".join(prerequisites)}',
                        'score': len(prerequisites) * 10,
                        'type': 'prerequisite'
                    })
        
        return recommendations[:limit]
    
    def _recommend_by_connectivity(self, limit: int) -> List[Dict[str, Any]]:
        """Recommend highly connected nodes"""
        degrees = dict(self.kg.graph.degree())
        sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for node_id, degree in sorted_nodes[:limit * 2]:
            if degree > 0:
                recommendations.append({
                    'node': node_id,
                    'reason': f'Highly connected ({degree} connections)',
                    'score': degree * 5,
                    'type': 'connectivity'
                })
        
        return recommendations[:limit]
    
    def _recommend_by_bridging(self, limit: int) -> List[Dict[str, Any]]:
        """Recommend nodes that bridge different knowledge areas"""
        try:
            # Find nodes with high betweenness centrality
            betweenness = nx.betweenness_centrality(self.kg.graph)
            sorted_nodes = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)
            
            recommendations = []
            for node_id, centrality in sorted_nodes[:limit]:
                if centrality > 0:
                    recommendations.append({
                        'node': node_id,
                        'reason': 'Bridges different knowledge areas',
                        'score': centrality * 100,
                        'type': 'bridging'
                    })
        except:
            # If graph is too small, return empty
            pass
        
        return recommendations[:limit]

