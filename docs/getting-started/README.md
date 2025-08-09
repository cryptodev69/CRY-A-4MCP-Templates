# Getting Started with CRY-A-4MCP Enhanced Templates

Welcome to the CRY-A-4MCP Enhanced Templates Package! This guide will help you get up and running quickly with our production-ready cryptocurrency analysis platform.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Node.js**: 16.x or higher
- **Docker**: Latest version with Docker Compose
- **Git**: For cloning and version control
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: At least 10GB free space

### Required API Keys
You'll need at least one of these LLM provider API keys:
- **OpenAI API Key** (recommended for best results)
- **OpenRouter API Key** (cost-effective alternative)
- **Groq API Key** (fastest inference)
- **Anthropic API Key** (Claude models)

## 🚀 Quick Start Options

### Option 1: One-Command Setup (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd CRY-A-4MCP-Templates

# Run the interactive setup wizard
python setup_wizard.py
```

The setup wizard will:
- ✅ Detect your use case and recommend the best variant
- ✅ Configure environment variables
- ✅ Install dependencies
- ✅ Start all services
- ✅ Validate the installation

### Option 2: Unified Development Environment
```bash
# Start both frontend and backend with one command
npm run dev
```

**Access Points:**
- Frontend: http://localhost:5000
- Backend API: http://localhost:4000
- API Documentation: http://localhost:4000/docs

### Option 3: Docker Stack (Production-like)
```bash
cd docker-stack
./start.sh
```

## 📖 Step-by-Step Setup Guide

### Step 1: Environment Configuration

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file with your API keys:**
   ```bash
   # Required: At least one LLM provider
   OPENAI_API_KEY=your_openai_key_here
   OPENROUTER_API_KEY=your_openrouter_key_here
   GROQ_API_KEY=your_groq_key_here
   
   # Optional: Database configurations
   NEO4J_PASSWORD=your_secure_password
   QDRANT_API_KEY=your_qdrant_key
   ```

### Step 2: Backend Setup

1. **Navigate to the MCP server directory:**
   ```bash
   cd starter-mcp-server
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server:**
   ```bash
   python -m uvicorn src.main:app --host 0.0.0.0 --port 4000 --reload
   ```

### Step 3: Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

### Step 4: Docker Services (Optional)

For full functionality, start the supporting services:

```bash
cd docker-stack
docker-compose up -d
```

This starts:
- **Qdrant**: Vector database for semantic search
- **Neo4j**: Graph database for relationship mapping
- **Redis**: Message queue and caching
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards

## ✅ Verification Steps

### 1. Backend Health Check
```bash
curl http://localhost:4000/health
```
Expected response: `{"status": "healthy"}`

### 2. Frontend Access
Open http://localhost:5000 in your browser. You should see the CRY-A-4MCP dashboard.

### 3. API Documentation
Visit http://localhost:4000/docs to explore the interactive API documentation.

### 4. Run Test Suite
```bash
# Backend tests
cd starter-mcp-server
pytest tests/

# Frontend tests
cd frontend
npm test
```

## 🎯 Choose Your Template Variant

After basic setup, select the variant that best matches your use case:

### 🔍 Market Sentiment Analysis
```bash
python setup_wizard.py --variant market-sentiment
```
**Best for:** News analysis, social media monitoring, sentiment tracking

### 📈 Trading Signals
```bash
python setup_wizard.py --variant trading-signals
```
**Best for:** Technical analysis, signal generation, backtesting

### 🛡️ Compliance Monitoring
```bash
python setup_wizard.py --variant compliance
```
**Best for:** Regulatory tracking, risk assessment, AML screening

### 🔧 Custom Configuration
```bash
python setup_wizard.py --variant custom
```
**Best for:** Specific requirements or hybrid approaches

## 🚨 Common Issues & Solutions

### Port Conflicts
**Issue:** Port 4000 already in use
**Solution:** 
```bash
# Find and kill the process using port 4000
lsof -ti:4000 | xargs kill -9

# Or use a different port
uvicorn src.main:app --host 0.0.0.0 --port 4001
```

### API Key Issues
**Issue:** "Invalid API key" errors
**Solution:**
1. Verify your API key is correct
2. Check the `.env` file is in the correct location
3. Restart the backend server after updating `.env`

### Docker Issues
**Issue:** Docker services won't start
**Solution:**
```bash
# Check Docker is running
docker --version

# Reset Docker state
docker-compose down
docker system prune -f
docker-compose up -d
```

### Memory Issues
**Issue:** Services crashing due to memory
**Solution:**
1. Increase Docker memory allocation to 8GB+
2. Close unnecessary applications
3. Use the lightweight variant: `--variant minimal`

## 📚 Next Steps

1. **[Configuration Guide](./configuration.md)** - Detailed configuration options
2. **[First Crawl Tutorial](./first-crawl.md)** - Create your first data extraction
3. **[Architecture Overview](../architecture/README.md)** - Understand the system design
4. **[Development Guide](../development/README.md)** - Start building features

## 🆘 Getting Help

- **Documentation**: Check the relevant guide in `/docs`
- **Logs**: Check `logs/` directory for detailed error information
- **Health Check**: Run `scripts/health_check.sh` for system diagnostics
- **Community**: Join our Discord for real-time support
- **Issues**: Create a GitHub issue with logs and reproduction steps

---

**Ready for the next step?** 👉 [Configuration Guide](./configuration.md)