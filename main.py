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
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize components
kg = KnowledgeGraph()
recommender = RecommendationEngine(kg)
visualizer = GraphVisualizer(kg)

# Data file paths - try multiple locations for different deployment environments
DATA_FILE = 'data/knowledge_graph.json'
TMP_DATA_FILE = '/tmp/knowledge_graph.json'

# Track if we can write to filesystem
CAN_SAVE_TO_FILE = True

def load_data():
    """Load knowledge graph data from file"""
    global DATA_FILE
    
    # Try to load from primary location
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                kg.load_from_dict(data)
                return
        except Exception as e:
            logging.warning(f"Failed to load from {DATA_FILE}: {e}")
    
    # Try to load from /tmp (for Vercel/serverless environments)
    if os.path.exists(TMP_DATA_FILE):
        try:
            with open(TMP_DATA_FILE, 'r') as f:
                data = json.load(f)
                kg.load_from_dict(data)
                DATA_FILE = TMP_DATA_FILE  # Use /tmp for future saves
                return
        except Exception as e:
            logging.warning(f"Failed to load from {TMP_DATA_FILE}: {e}")
    
    # Initialize with some example data if no file exists
    kg.add_node('Python', 'concept', {'level': 'intermediate', 'started': '2024-01-01'})
    kg.add_node('Flask', 'concept', {'level': 'beginner', 'started': '2024-02-01'})
    kg.add_node('Graph Theory', 'concept', {'level': 'beginner', 'started': '2024-03-01'})
    kg.add_edge('Python', 'Flask', 'prerequisite')
    kg.add_edge('Python', 'Graph Theory', 'related_to')

def save_data():
    """Save knowledge graph data to file - handles read-only filesystem gracefully"""
    global CAN_SAVE_TO_FILE, DATA_FILE
    
    if not CAN_SAVE_TO_FILE:
        return  # Skip saving if we know filesystem is read-only
    
    data_dict = kg.to_dict()
    
    # Try primary location first
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump(data_dict, f, indent=2)
        return
    except (OSError, IOError, PermissionError) as e:
        # If primary location fails, try /tmp (for Vercel/serverless)
        if DATA_FILE != TMP_DATA_FILE:
            try:
                with open(TMP_DATA_FILE, 'w') as f:
                    json.dump(data_dict, f, indent=2)
                DATA_FILE = TMP_DATA_FILE  # Switch to /tmp for future saves
                logging.info(f"Switched to {TMP_DATA_FILE} for data storage")
                return
            except (OSError, IOError, PermissionError) as e2:
                # Both locations failed - filesystem is read-only
                CAN_SAVE_TO_FILE = False
                logging.warning(f"Cannot save to filesystem (read-only). Data will be in-memory only. Error: {e2}")
                return
        else:
            # Already tried /tmp, give up
            CAN_SAVE_TO_FILE = False
            logging.warning(f"Cannot save to filesystem (read-only). Data will be in-memory only. Error: {e}")
            return

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.before_request
def ensure_data_loaded():
    """Ensure graph data is loaded before each request (for serverless compatibility)"""
    # Only reload if graph is empty (might have been reset in serverless environment)
    # But don't reload if we already have nodes (to preserve in-memory state)
    if kg.get_node_count() == 0:
        try:
            load_data()
        except Exception as e:
            logging.warning(f"Failed to load data in before_request: {e}")

@app.route('/api/graph', methods=['GET'])
def get_graph():
    """Get the current knowledge graph structure"""
    graph_data = visualizer.get_graph_data()
    return jsonify(graph_data)

@app.route('/api/nodes', methods=['POST'])
def add_node():
    """Add a new node to the graph"""
    try:
        # Ensure data is loaded
        if kg.get_node_count() == 0:
            load_data()
        
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        node_id = data.get('id')
        node_type = data.get('type', 'concept')
        properties = data.get('properties', {})
        
        if not node_id:
            return jsonify({'success': False, 'error': 'Node ID is required'}), 400
        
        # Check if node already exists
        if node_id in kg.graph:
            return jsonify({'success': False, 'error': f'Node {node_id} already exists'}), 400
        
        kg.add_node(node_id, node_type, properties)
        save_data()
        
        # Verify node was added
        if node_id not in kg.graph:
            return jsonify({'success': False, 'error': f'Failed to add node {node_id}'}), 500
        
        return jsonify({
            'success': True, 
            'message': f'Node {node_id} added',
            'total_nodes': kg.get_node_count()
        })
    except Exception as e:
        logging.error(f"Error adding node: {e}", exc_info=True)
        return jsonify({'success': False, 'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/edges', methods=['POST'])
def add_edge():
    """Add a new edge to the graph"""
    try:
        # Ensure data is loaded
        if kg.get_node_count() == 0:
            load_data()
        
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        source = data.get('source')
        target = data.get('target')
        relationship = data.get('relationship', 'related_to')
        
        if not source or not target:
            return jsonify({'success': False, 'error': 'Source and target are required'}), 400
        
        if source == target:
            return jsonify({'success': False, 'error': 'Source and target cannot be the same'}), 400
        
        # Check if nodes exist BEFORE trying to add edge
        missing_nodes = []
        if source not in kg.graph:
            missing_nodes.append(f'"{source}"')
        if target not in kg.graph:
            missing_nodes.append(f'"{target}"')
        
        if missing_nodes:
            available_nodes = list(kg.graph.nodes())
            error_msg = f"Node(s) {', '.join(missing_nodes)} do not exist. "
            if available_nodes:
                error_msg += f"Available nodes: {', '.join(available_nodes[:10])}"
                if len(available_nodes) > 10:
                    error_msg += f" (and {len(available_nodes) - 10} more)"
            else:
                error_msg += "No nodes exist yet. Please add nodes first."
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Check if edge already exists
        if kg.graph.has_edge(source, target):
            return jsonify({'success': False, 'error': f'Edge between {source} and {target} already exists'}), 400
        
        kg.add_edge(source, target, relationship)
        save_data()
        return jsonify({'success': True, 'message': f'Edge added between {source} and {target}'})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error adding edge: {e}", exc_info=True)
        return jsonify({'success': False, 'error': f'Internal error: {str(e)}'}), 500

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
        'most_connected': kg.get_most_connected_nodes(5),
        'all_nodes': list(kg.graph.nodes())  # Include list of all node IDs for debugging
    }
    return jsonify(stats)

@app.route('/api/debug/nodes', methods=['GET'])
def debug_nodes():
    """Debug endpoint to list all nodes in the graph"""
    return jsonify({
        'nodes': list(kg.graph.nodes()),
        'nodes_data': kg.nodes_data,
        'graph_nodes': list(kg.graph.nodes(data=True)),
        'node_count': kg.get_node_count(),
        'edge_count': kg.get_edge_count(),
        'can_save': CAN_SAVE_TO_FILE,
        'data_file': DATA_FILE
    })

@app.route('/api/verify', methods=['GET'])
def verify_graph():
    """Verify graph state - useful for debugging"""
    return jsonify({
        'node_count': kg.get_node_count(),
        'edge_count': kg.get_edge_count(),
        'all_nodes': list(kg.graph.nodes()),
        'all_edges': [{'source': s, 'target': t} for s, t in kg.graph.edges()],
        'nodes_data_keys': list(kg.nodes_data.keys()),
        'edges_data_count': len(kg.edges_data)
    })

if __name__ == '__main__':
    load_data()
    app.run(debug=True, port=5000)

