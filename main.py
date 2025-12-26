"""
Personal Knowledge Graph & Learning Tracker
Main application entry point
"""

from flask import Flask, render_template, request, jsonify
from app.graph_builder import KnowledgeGraph
from app.recommendations import RecommendationEngine
from app.visualizer import GraphVisualizer
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize components
kg = KnowledgeGraph()
recommender = RecommendationEngine(kg)
visualizer = GraphVisualizer(kg)

# Data file path
DATA_FILE = 'data/knowledge_graph.json'

def load_data():
    """Load knowledge graph data from file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            kg.load_from_dict(data)
    else:
        # Initialize with some example data
        kg.add_node('Python', 'concept', {'level': 'intermediate', 'started': '2024-01-01'})
        kg.add_node('Flask', 'concept', {'level': 'beginner', 'started': '2024-02-01'})
        kg.add_node('Graph Theory', 'concept', {'level': 'beginner', 'started': '2024-03-01'})
        kg.add_edge('Python', 'Flask', 'prerequisite')
        kg.add_edge('Python', 'Graph Theory', 'related_to')

def save_data():
    """Save knowledge graph data to file"""
    os.makedirs('data', exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(kg.to_dict(), f, indent=2)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/graph', methods=['GET'])
def get_graph():
    """Get the current knowledge graph structure"""
    graph_data = visualizer.get_graph_data()
    return jsonify(graph_data)

@app.route('/api/nodes', methods=['POST'])
def add_node():
    """Add a new node to the graph"""
    data = request.json
    node_id = data.get('id')
    node_type = data.get('type', 'concept')
    properties = data.get('properties', {})
    
    kg.add_node(node_id, node_type, properties)
    save_data()
    return jsonify({'success': True, 'message': f'Node {node_id} added'})

@app.route('/api/edges', methods=['POST'])
def add_edge():
    """Add a new edge to the graph"""
    data = request.json
    source = data.get('source')
    target = data.get('target')
    relationship = data.get('relationship', 'related_to')
    
    kg.add_edge(source, target, relationship)
    save_data()
    return jsonify({'success': True, 'message': f'Edge added between {source} and {target}'})

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get learning recommendations"""
    recommendations = recommender.get_recommendations()
    return jsonify(recommendations)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get graph statistics"""
    stats = {
        'total_nodes': kg.get_node_count(),
        'total_edges': kg.get_edge_count(),
        'node_types': kg.get_node_types(),
        'most_connected': kg.get_most_connected_nodes(5)
    }
    return jsonify(stats)

if __name__ == '__main__':
    load_data()
    app.run(debug=True, port=5000)

