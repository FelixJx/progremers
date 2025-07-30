# AI Agent Development Team

An AI-powered development team that simulates enterprise software development workflows using multiple specialized agents.

## 🚀 Features

- **Multi-Agent Collaboration**: 8 specialized agents working together (Manager, PM, Architect, Developer, QA, UI, Scrum Master, Code Reviewer)
- **Multi-Project Management**: Support for multiple concurrent projects with isolated contexts
- **Sprint Memory System**: Intelligent memory management with meeting minutes and context compression
- **Knowledge Transfer**: Cross-project experience reuse and pattern recognition
- **MCP Integration**: Enhanced capabilities for Dev, QA, and Architect agents

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 7+
- Node.js 18+ (for MCP servers)
- Docker & Docker Compose (optional)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-agent-team.git
cd ai-agent-team
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Copy the environment file and configure:
```bash
cp .env.example .env
# Edit .env with your API keys and configurations
```

4. Set up the database:
```bash
# Start PostgreSQL and Redis (using Docker)
docker-compose up -d postgres redis

# Run migrations
poetry run python scripts/setup_database.py
```

5. Install MCP servers (optional but recommended):
```bash
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-shell
npm install -g @modelcontextprotocol/server-puppeteer
```

## 🏃‍♂️ Quick Start

1. Start the API server:
```bash
poetry run python -m src.main
```

2. Create a new project:
```bash
poetry run python -m src.cli create-project --name "My E-commerce App" --type "web"
```

3. Start development:
```bash
poetry run python -m src.cli start-sprint --project-id <project-id> --goal "Implement user authentication"
```

## 🏗️ Architecture

```
src/
├── agents/                 # Agent implementations
│   ├── base/              # Base agent classes
│   └── implementations/   # Specific agent implementations
├── core/                  # Core functionality
│   ├── memory/           # Memory management system
│   ├── communication/    # Inter-agent communication
│   └── project_manager/  # Multi-project management
├── config/               # Configuration management
└── utils/                # Utility functions
```

## 🤖 Available Agents

1. **Manager Agent**: Orchestrates the team, validates work, resolves conflicts
2. **PM Agent**: Manages requirements, creates PRDs, defines user stories
3. **Architect Agent**: Designs system architecture, selects tech stack
4. **Developer Agent**: Implements code, writes tests (MCP-enabled)
5. **QA Agent**: Creates test cases, runs automated tests (MCP-enabled)
6. **UI Agent**: Designs interfaces, creates design systems
7. **Scrum Agent**: Manages sprints, facilitates meetings
8. **Review Agent**: Reviews code quality, ensures standards

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Agent Guide](docs/agents.md)
- [Configuration Guide](docs/configuration.md)
- [Development Guide](docs/development.md)

## 🧪 Testing

Run the test suite:
```bash
poetry run pytest
```

Run with coverage:
```bash
poetry run pytest --cov=src
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.