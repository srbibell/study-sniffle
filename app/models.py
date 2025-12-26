"""
Data models for the knowledge graph
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class Node:
    """Represents a node in the knowledge graph"""
    id: str
    node_type: str  # 'concept', 'resource', 'project', 'skill'
    properties: Dict[str, Any]
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class Edge:
    """Represents an edge (relationship) in the knowledge graph"""
    source: str
    target: str
    relationship: str  # 'prerequisite', 'related_to', 'uses', 'learned_from'
    weight: float = 1.0
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

