# AI Tool Verification Assistant

An AI-powered semantic search chatbot designed to accelerate the verification process for AI tools by analyzing legal and compliance documents using Retrieval-Augmented Generation (RAG).

## 📋 Project Overview

Companies today gain significant value from AI tools that accelerate work, automate tedious tasks, and improve quality. However, these tools differ widely in maturity and business models, creating risks such as:

- Data leakage
- Weak security
- Compliance failures
- GDPR violations
- Storage of user information outside the EU

HTEC's verification team must carefully assess these risks before approving any tool for company-wide use. Currently, verifying a single tool can take several days, involving manual review of multiple long documents like:

- Terms of Service
- Privacy Policy
- AI Model Documentation
- Data Processing Agreements
- Licensing Agreements
- Security Whitepapers

This solution helps automate and accelerate the verification process by providing an intelligent chatbot that can quickly find answers to critical questions like:

- "Is the AI model trained on our company data?"
- "Where is user data stored?"
- "Does this product allow disabling AI training?"
- "Which license tier includes SOC 2 compliance?"

## 🎯 Features

- **Synthetic Data Generation**: Generate realistic legal and compliance documents for verification
- **Semantic Search**: Advanced RAG-based document retrieval using embeddings
- **Intelligent Chatbot**: Natural language Q&A interface for document queries
- **Evaluation Framework**: Standard metrics for performance assessment
- **Configurable Architecture**: Modular design for easy customization

## 🏗️ Project Structure

```
ai_tool_verification_assistant/
├── data/                  # Data directory (synthetic datasets, documents)
│   ├── raw/              # Raw data files
│   └── processed/        # Processed data files
├── src/                  # Source code
│   ├── __init__.py
│   ├── config.py         # Configuration management
│   ├── data_ingestion/   # Data ingestion and indexing modules
│   ├── chatbot/          # RAG chatbot implementation
│   ├── evaluation/       # Evaluation metrics and analysis
│   └── utils/            # Utility functions
│       ├── __init__.py
│       └── logger.py     # Logging configuration
├── logs/                 # Application logs (generated)
├── rag_store/            # ChromaDB vector store (generated)
├── .gitignore           # Git ignore patterns
├── env.example          # Environment variables template
├── pyproject.toml       # Project configuration and dependencies
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── main.py             # Entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Access to HTEC network (in office or via VPN)

### Installation

1. **Navigate to the project directory**
   ```bash
   cd ai_tool_verification_assistant
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   For development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up environment variables**
   
   Copy the example environment file:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your API key:
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   OPENAI_BASE_URL=https://litellm.ai.paas.htec.rs
   ```

## ⚙️ Configuration

### Environment Variables

All configuration is managed through environment variables (loaded from `.env` file):

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your HTEC LiteLLM API key | **Required** |
| `OPENAI_BASE_URL` | API base URL | `https://litellm.ai.paas.htec.rs` |
| `DEFAULT_MODEL` | Default LLM model | `l2-gpt-4o-mini` |
| `EMBEDDING_MODEL` | Embedding model for RAG | `l2-text-embedding-3-small` |
| `TEMPERATURE` | LLM temperature (0.0-2.0) | `0.7` |
| `MAX_TOKENS` | Maximum tokens per request | `2000` |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB persistence directory | `./rag_store` |
| `CHUNK_SIZE` | Text chunk size for splitting | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap size | `200` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FILE` | Log file path | `logs/app.log` |
| `DATA_DIR` | Data directory path | `./data` |

## 📖 Usage

### Running the Application

```bash
python main.py
```

### Development Workflow

1. **Code Formatting**
   ```bash
   black src/ main.py
   ```

2. **Linting**
   ```bash
   ruff check src/
   ```

3. **Type Checking**
   ```bash
   mypy src/
   ```

## 🛠️ Development

### Code Quality Tools

This project uses several tools to ensure code quality:

- **Black**: Code formatting
- **Ruff**: Fast Python linter
- **MyPy**: Static type checking

### Adding Dependencies

1. Add the package to `requirements.txt` with version pinning
2. Update `pyproject.toml` if it's a project dependency
3. Install and verify: `pip install -r requirements.txt`

## 📝 Code Style

This project follows PEP 8 style guidelines:

- Maximum line length: 100 characters
- Use 4 spaces for indentation
- Use type hints where possible
- Write docstrings for all public functions and classes
- Follow clean code principles

## 🤝 Development Guidelines

1. Follow the code style guidelines outlined above
2. Keep code quality checks green before committing
4. Document your changes in code comments and docstrings

## 📚 Documentation

- Code is documented with docstrings following Google style
- Configuration options are documented in this README
- API documentation will be available in the code

## 🔒 Security

- Never commit `.env` files with real API keys
- Use environment variables for sensitive configuration
- Keep dependencies up to date for security patches

## 📄 License

This project is developed for HTEC L2 AI Course completion.

## 🗺️ Roadmap

- [ ] Implement synthetic data generation
- [ ] Build document ingestion pipeline
- [ ] Create vector store indexing
- [ ] Develop RAG-based chatbot
- [ ] Add evaluation metrics framework
- [ ] Performance optimization
- [ ] User interface development

## 📞 Support

For questions or issues, please contact the HTEC verification team.

---

**Note**: This is an internal tool for HTEC's software whitelisting and verification processes.