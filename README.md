# Auto Analytics - AI-Powered Data Analysis System

An intelligent multi-agent system that democratizes data analysis by enabling natural language interactions with databases, built with Google's Agent Development Kit (ADK) and Gemini 2.5 Flash.

## 🏗️ Decoupled Architecture

The system is designed with **complete separation** between analysis and display services:

```
┌─────────────────────┐    📁 File System    ┌─────────────────────┐
│                     │    Communication      │                     │
│   🤖 AI Agent       │◄──────────────────────┤  🌐 FastAPI Server  │
│   (Port 8000)       │                       │   (Port 9000)       │
│                     │                       │                     │
│ • Data Analysis     │     reports/          │ • Report Display    │
│ • SQL Generation    │   *.html files        │ • Web Interface     │
│ • Report Creation   │                       │ • REST API          │
│ • Gemini 2.5 Flash  │                       │ • Report Management │
└─────────────────────┘                       └─────────────────────┘
```

### Benefits of Decoupled Design
- ✅ **True Independence**: Each service can start/stop independently
- ✅ **Technology Separation**: Different frameworks for different purposes
- ✅ **Scalability**: Easy to scale or replace either component
- ✅ **Development Efficiency**: Teams can work on services independently
- ✅ **Operational Flexibility**: Separate deployment, monitoring, and logging

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- PostgreSQL (for data analysis)

### Installation

```bash
# Clone and navigate to project
cd auto-analytics

# Install dependencies
uv sync
```

### Running the System

#### Option 1: Start Both Services (Recommended)
```bash
# Automatically starts both services in separate terminals
./scripts/start-both.sh
```

#### Option 2: Start Services Individually

**AI Agent** (Generates reports):
```bash
./scripts/start-agent.sh
# Or: cd /workspace && adk web --port 8000
```

**FastAPI Server** (Displays reports):
```bash
./scripts/start-fastapi.sh
# Or: cd fastapi-server && python main.py --port 9000
```

### Access Points
- **🤖 AI Agent Interface**: http://localhost:8000
- **🌐 Report Display Server**: http://localhost:9000
- **📊 API Documentation**: http://localhost:9000/api/docs

## 📖 How to Use

### 1. Generate Reports with AI Agent
1. Go to http://localhost:8000
2. Enter your data analysis request in natural language
3. The AI agent will:
   - Interpret your request
   - Explore the database schema
   - Generate and execute SQL queries
   - Analyze the results
   - Create an HTML report in `reports/` directory

### 2. View Reports with FastAPI Server
1. Go to http://localhost:9000
2. Browse the list of generated reports
3. Click on any report to view it
4. Use the API endpoints for programmatic access

## 🏗️ Project Structure

```
auto-analytics/
├── auto-analytics-agent/          # 🤖 AI Agent Service
│   ├── agent.py                   # Main ADK agent
│   ├── workflow.py                # Multi-agent workflow
│   └── tools/                     # Agent tools
│       ├── html_report_generator.py
│       ├── simple_link_generator.py
│       └── templates/
├── fastapi-server/                # 🌐 FastAPI Display Service
│   ├── main.py                    # FastAPI application
│   ├── requirements.txt           # FastAPI dependencies
│   └── templates/                 # Jinja2 templates
├── scripts/                       # 🚀 Startup Scripts
│   ├── start-agent.sh             # Start AI agent
│   ├── start-fastapi.sh           # Start FastAPI server
│   ├── start-both.sh              # Start both services
│   └── *.bat                      # Windows scripts
├── reports/                       # 📁 Shared Reports Directory
├── config/                        # ⚙️ Configuration
└── doc/                          # 📚 Documentation
```

## 🔧 Development

### Code Quality
```bash
# Format code
black .
isort .

# Type checking
mypy auto-analytics-agent/

# Linting
flake8 auto-analytics-agent/

# Run tests
pytest
```

### Agent Testing
```bash
# Start local API server for testing
adk api_server --port 8000

# Run agent tests
pytest tests/test_agent.py -v
```

## 🌟 Features

### AI Agent Service
- **Natural Language Processing**: Understands data analysis requests in Japanese and English
- **Intelligent SQL Generation**: Automatically generates optimized SQL queries
- **Error Recovery**: Self-correcting SQL execution with automatic retry
- **Multi-Agent Workflow**: Specialized agents for different analysis phases
- **HTML Report Generation**: Creates professional, formatted reports

### FastAPI Display Service
- **Modern Web Interface**: Clean, responsive report browsing
- **REST API**: Full programmatic access to reports
- **File Management**: Upload, delete, and organize reports
- **Real-time Updates**: Automatically detects new reports
- **Security**: Input validation and secure file serving

### Integration Features
- **Zero Coupling**: Services communicate only through files
- **Independent Scaling**: Scale analysis and display separately
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Health Monitoring**: Built-in health checks for both services

## 🛡️ Security

- **SQL Injection Prevention**: Parameterized queries and validation
- **File Security**: Restricted file access and validation
- **CORS Support**: Configurable cross-origin policies
- **Input Sanitization**: All user inputs are properly sanitized

## 📝 Configuration

### AI Agent
- Configuration: `config/tools.yaml`
- Environment: Uses ADK configuration
- Models: Gemini 2.5 Flash (configurable)

### FastAPI Server
- Port: 9000 (configurable via `--port`)
- Reports Directory: `../reports` (configurable via `--reports-dir`)
- Host: localhost (configurable via `--host`)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: See the `doc/` directory
- **Issues**: Report bugs and feature requests via GitHub issues
- **Development Guide**: See `CLAUDE.md` for detailed development instructions

---

Built with ❤️ using Google ADK, Gemini 2.5 Flash, and FastAPI