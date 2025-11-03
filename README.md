# Telex.im AI Code Reviewer Agent

A production-ready FastAPI-based AI agent that provides intelligent code reviews and explanations. Fully compliant with the A2A (Agent-to-Agent) protocol and seamlessly integrates with Telex.im.

## ✨ Features

### 🤖 AI Capabilities
- **Code Review**: Comprehensive code analysis with best practice suggestions
- **Code Explanation**: Clear explanations of complex code logic
- **AI Chat**: Interactive conversations about programming concepts
- **Multi-language Support**: Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#

### 🔌 Integration Options
- **A2A Protocol**: Full JSON-RPC 2.0 compliance for modern agent communication
- **Webhook Integration**: Legacy webhook support for existing Telex.im setups
- **RESTful API**: Well-documented endpoints for custom integrations

### 🏗️ Architecture
- **Service-based Design**: Clean separation of concerns with dedicated services
- **Type-safe Configuration**: Pydantic-based settings management
- **Comprehensive Error Handling**: Standardized error responses
- **Health Monitoring**: Built-in health checks and monitoring endpoints

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone the repository
git clone <your-repo-url>
cd telex-ai-agent

# Copy environment template
cp .env.example .env

# Edit .env and add your Mistral API key
MISTRAL_API_KEY=your_actual_api_key_here
```

### 2. Run Locally
```bash
# Using the deployment helper
python deploy.py check    # Check requirements
python deploy.py test     # Test locally

# Or manually
python start_server.py
```

### 3. Deploy to Leapcell.io
```bash
# Prepare for deployment
python deploy.py leapcell

# Push to GitHub and deploy via Leapcell dashboard
# See LEAPCELL_DEPLOYMENT.md for detailed instructions
```

## 📡 API Endpoints

### Core Endpoints
- `GET /` - Service information and available endpoints
- `GET /health` - Health check with service status
- `GET /test-llm` - Test LLM connection and functionality

### Integration Endpoints
- `POST /webhook` - Telex.im webhook integration (legacy)
- `POST /a2a` - A2A protocol JSON-RPC endpoint (recommended)

### A2A Methods
- `ping` - Connectivity test
- `capabilities` - Agent capabilities and supported methods
- `ai.chat` - Interactive AI conversations
- `ai.review_code` - Code review and analysis
- `ai.explain_code` - Code explanation and documentation
- `task.create` - Asynchronous task creation

## 🔧 Configuration

### Environment Variables
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MISTRAL_API_KEY` | ✅ | - | Your Mistral AI API key |
| `MISTRAL_MODEL` | ❌ | `mistral-small-latest` | AI model to use |
| `APP_NAME` | ❌ | `Telex AI Code Reviewer` | Application name |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |
| `DEBUG` | ❌ | `false` | Debug mode |

### Deployment Configuration
- **Dockerfile**: Optimized for cloud deployment
- **leapcell.yaml**: Leapcell.io deployment configuration
- **Health Checks**: Automatic health monitoring
- **Auto-scaling**: Configurable scaling based on load

## 🏗️ Project Structure

```
telex-ai-agent/
├── app/
│   ├── main.py                 # FastAPI application setup
│   ├── config.py              # Configuration management
│   ├── api/                   # API routes
│   │   ├── routes.py          # Main API routes
│   │   └── a2a_routes.py      # A2A protocol routes
│   ├── services/              # Business logic
│   │   ├── llm_service.py     # LLM interactions
│   │   ├── telex_service.py   # Telex message processing
│   │   └── a2a_service.py     # A2A protocol implementation
│   ├── schemas/               # Data models
│   │   ├── a2a_models.py      # A2A and webhook models
│   │   └── a2a_protocol.py    # A2A protocol schemas
│   ├── core/                  # Core utilities
│   │   └── logging.py         # Logging configuration
│   └── agent/                 # Legacy agent code
│       ├── core.py            # Backward compatibility
│       └── a2a_handler.py     # A2A request handler
├── deploy.py                  # Deployment helper script
├── start_server.py           # Development server
├── test_a2a_compliance.py    # A2A compliance tests
├── Dockerfile                # Container configuration
├── leapcell.yaml            # Leapcell deployment config
└── requirements.txt         # Python dependencies
```

## 🧪 Testing

### Local Testing
```bash
# Run all checks and tests
python deploy.py test

# Manual testing
curl http://localhost:8000/health
curl -X POST http://localhost:8000/a2a \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "ping", "id": "test"}'
```

### A2A Compliance Testing
```bash
# Run comprehensive A2A protocol compliance tests
python test_a2a_compliance.py http://localhost:8000
```

### Docker Testing
```bash
# Build and test Docker image
python deploy.py docker
```

## 🚀 Deployment

### Leapcell.io (Recommended)
1. **Prepare**: `python deploy.py leapcell`
2. **Deploy**: Follow [LEAPCELL_DEPLOYMENT.md](LEAPCELL_DEPLOYMENT.md)
3. **Configure**: Set environment variables in Leapcell dashboard
4. **Test**: Verify endpoints are working

### Other Platforms
- **Railway**: Use `railway.json` configuration
- **Render**: Use `render.yaml` configuration
- **Docker**: Use provided Dockerfile for any container platform

## 🔗 Telex.im Integration

### A2A Protocol Integration (Recommended)
```yaml
Agent Type: A2A Protocol
Endpoint: https://your-app.leapcell.dev/a2a
Protocol: JSON-RPC 2.0
Methods: ping, capabilities, ai.chat, ai.review_code, ai.explain_code
```

### Webhook Integration (Legacy)
```yaml
Agent Type: Webhook
Webhook URL: https://your-app.leapcell.dev/webhook
Method: POST
Content-Type: application/json
```

See [TELEX_INTEGRATION_GUIDE.md](TELEX_INTEGRATION_GUIDE.md) for detailed integration instructions.

## 📊 Monitoring

### Health Checks
- `/health` - Overall application health
- `/test-llm` - LLM service connectivity
- Built-in Docker health checks

### Logging
- Structured logging with configurable levels
- Request/response logging
- Error tracking and reporting

### Metrics
Monitor key performance indicators:
- Response times
- Error rates
- LLM API usage
- Request volume

## 🔒 Security

### Best Practices
- Non-root Docker user
- Environment variable validation
- Input sanitization
- Rate limiting ready
- CORS configuration

### Optional Security Features
- API key authentication
- Request rate limiting
- IP whitelisting
- SSL/TLS termination

## 📚 Documentation

- [A2A Compliance Analysis](A2A_COMPLIANCE_ANALYSIS.md) - Detailed compliance report
- [Telex Integration Guide](TELEX_INTEGRATION_GUIDE.md) - Complete integration instructions
- [Leapcell Deployment Guide](LEAPCELL_DEPLOYMENT.md) - Leapcell-specific deployment
- [Refactoring Summary](REFACTORING_SUMMARY.md) - Architecture improvements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python deploy.py test`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Mistral AI](https://mistral.ai/) - Powerful language models
- [Telex.im](https://telex.im/) - Agent communication platform
- [Leapcell.io](https://leapcell.io/) - Cloud deployment platform

---

**Ready to deploy?** 🚀 Run `python deploy.py leapcell` to get started!
