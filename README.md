# Personal Knowledge Graph & Learning Tracker

A unique Python project that helps you visualize and track your learning journey through an interactive knowledge graph. Connect concepts, resources, projects, and skills to see how your knowledge grows over time.

## Features

- 📊 **Knowledge Graph Visualization**: Create nodes for concepts, resources, and projects, and connect them to build your personal knowledge network
- 📈 **Learning Progress Tracking**: Track your progress on different skills and topics
- 🔍 **Smart Recommendations**: Get suggestions for what to learn next based on your current knowledge graph
- 📱 **Interactive Dashboard**: Beautiful web-based interface to explore your knowledge graph
- 💾 **Data Persistence**: Save and load your knowledge graph
- 📊 **Analytics**: View statistics about your learning journey

## Tech Stack

- **Backend**: Python (Flask/FastAPI)
- **Graph Database**: NetworkX for graph operations
- **Visualization**: Plotly/D3.js for interactive graphs
- **Frontend**: HTML/CSS/JavaScript (or React for advanced version)
- **Data Storage**: JSON/SQLite (or Neo4j for advanced version)

## Project Structure

```
personal-knowledge-graph/
├── app/
│   ├── __init__.py
│   ├── models.py          # Graph data models
│   ├── graph_builder.py   # Graph construction logic
│   ├── recommendations.py # Recommendation engine
│   └── visualizer.py      # Visualization utilities
├── data/
│   └── knowledge_graph.json
├── static/
│   ├── css/
│   └── js/
├── templates/
│   └── index.html
├── requirements.txt
└── main.py
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Visit `http://localhost:5000` to start building your knowledge graph!

## Future Enhancements

- AI-powered concept extraction from notes
- Integration with learning platforms (Coursera, Udemy, etc.)
- Collaborative knowledge graphs
- Mobile app version
- Export to various formats (PDF, Markdown, etc.)

