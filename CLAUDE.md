# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Auto Analytics is an AI-powered multi-agent system that democratizes data analysis by enabling natural language interactions with databases. The system uses Google's Agent Development Kit (ADK) with Gemini 2.5 Flash for intelligent data analysis and report generation.

## Architecture

### Core Components

- **ADK Agent System**: Built on Google Agent Development Kit, the main agent (`auto-analytics-agent/agent.py`) orchestrates all interactions
- **Multi-Agent Architecture**: Designed for specialized agents (NLP, Data Analyst, Report Generation) that coordinate through a shared context
- **MCP Integration**: Uses Model Context Protocol for secure database access via PostgreSQL toolsets
- **Gemini 2.5 Flash**: Primary AI model for natural language understanding, SQL generation, and insight extraction

### Key Technologies

- **Backend**: Python 3.11+, asyncio for concurrent operations
- **AI Framework**: Google ADK, Gemini 2.5 Flash API
- **Database**: PostgreSQL with MCP server for secure access
- **Data Processing**: pandas, matplotlib, plotly for analysis and visualization
- **Configuration**: YAML-based tool configuration in `config/tools.yaml`

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Install development dependencies
uv sync --group dev
```

### Running the System
```bash
# Start the development UI
cd /workspace
adk web --port 8000
```

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
pytest --cov=auto-analytics-agent --cov-report=html
```

### Agent Testing
```bash
# Start local API server for testing
adk api_server --port 8000

# Run agent tests
pytest tests/test_agent.py -v

# Run integration tests with coverage
pytest --cov=auto-analytics-agent --cov-report=html
```

**Critical Testing Points:**
- **SQL Generation Accuracy**: Verify 95%+ accuracy in SQL query generation from natural language
- **Security Validation**: Test SQL injection prevention and data privacy protection
- **MCP Integration**: Validate all database tool connections and error handling
- **Performance**: Ensure <3s response time for 95% of queries
- **Multi-language Support**: Test both Japanese and English interactions

**Test Endpoints:**
- `/run`: Synchronous testing (collects all events)
- `/run_sse`: Real-time testing with Server-Sent-Events

See `doc/testing/agent-testing-guide.md` for comprehensive testing procedures.

### Database Tools
The system uses MCP (Model Context Protocol) for database interactions. Tools are configured in `config/tools.yaml`:

- `test-connection`: Verify PostgreSQL connectivity
- `get-users`: Retrieve user data
- `get-tables`: List database tables
- `get-table-schema`: Get table structure
- `execute-query`: Run dynamic SQL queries

## Development Approach

### Phase-Based Implementation
The project follows a 4-phase approach:
1. **Phase 1**: Environment setup and basic ADK agent functionality
2. **Phase 2**: MVP with PostgreSQL MCP integration and basic NLP→SQL→Analysis flow
3. **Phase 3**: Advanced multi-agent features and enhanced analysis capabilities
4. **Phase 4**: HTML report generation and visualization

### Agent Design Patterns

- **Non-deterministic Approach**: Agents use exploratory analysis patterns, dynamically determining next steps based on current findings
- **Context Sharing**: Agents maintain shared conversation context and analysis state
- **Error Recovery**: Comprehensive error handling with fallback strategies for SQL errors, API failures, and data quality issues

### Security Considerations

- **Data Privacy**: PII detection and masking capabilities
- **SQL Injection Prevention**: Query validation and parameterized statements
- **Access Control**: Role-based permissions for database operations
- **Audit Logging**: Comprehensive logging of all data access and analysis operations

## Configuration

### Agent Configuration
The main agent is configured in `auto-analytics-agent/agent.py` with:
- Gemini 2.5 Flash model integration
- MCP toolset for PostgreSQL operations
- Support for weather/time utilities (placeholder functions)

### Database Configuration
MCP server configuration in `config/tools.yaml` defines:
- PostgreSQL connection parameters
- Pre-defined SQL tools and queries
- Analytics toolset with common operations
- Dynamic query execution capabilities

## Documentation Structure

- `doc/requirement/`: Requirements specification
- `doc/design/`: System architecture and design documents
- `doc/phase-plan/`: Phase-specific implementation plans
- `doc/report/`: Development progress reports

## Development Workflow

### Progress Reporting
- **Always document progress**: Create progress reports in `doc/report/` during implementation phases
- **Report naming**: Use format `NNNNN_description.md` (e.g., `00005_phase2_implementation.md`)
- **Update frequency**: Create new reports for major milestones, feature completions, and phase transitions
- **Include metrics**: Document implementation progress, blockers, and next steps

### Documentation Maintenance
- **Living documentation**: Update `doc/` files when implementation reveals design issues or improvements
- **Immediate updates**: Fix documentation errors as soon as they are discovered during implementation
- **Version alignment**: Ensure documentation stays synchronized with actual implementation

## Key Implementation Notes

- The system is designed for internal use only (not external-facing)
- Gemini API rate limits and token usage must be carefully managed
- MCP server acts as a security boundary for database access
- All SQL operations should use parameterized queries to prevent injection
- Analysis results should include data quality assessments and confidence scores
- HTML report generation uses structured templates with embedded visualizations