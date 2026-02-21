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

- **Synthetic Data Generation** (implemented): Generate realistic legal and compliance documents for verification:
  - **Ideation**: Fictional tool names and metadata (`tool_info.json`) via structured outputs.
  - **TOC**: Table-of-contents JSON per document type via structured outputs.
  - **Sections**: Section-by-section HTML generation with 2–3 data quality issues per document; strict HTML validation (lxml); rate-limit retry and pacing.
- **Configurable models**: Separate model and temperature per task (ideation, TOC, section) in `config/generation.yaml`.
- **Semantic Search**: Advanced RAG-based document retrieval using embeddings (planned).
- **Intelligent Chatbot**: Natural language Q&A interface for document queries (planned).
- **Evaluation Framework**: Standard metrics for performance assessment (planned).

## 🏗️ Project Structure

```
ai_tool_verification_assistant/
├── config/
│   ├── generation.yaml   # Models (ideation, toc, section), dataset (categories, document_types)
│   └── prompts.yaml      # System/user prompts for ideation, toc, section generation
├── data/                 # Generated dataset (one folder per tool)
│   └── <ToolName>/
│       ├── tool_info.json
│       ├── toc_<document_type>.json
│       └── <document_type>.html
├── scripts/
│   ├── dataset/
│   │   └── generate_dataset.py   # CLI: --tools, --tocs, --sections, --all
│   └── utils/
│       ├── constants.py          # TOC/TOOL_INFO JSON schemas for structured outputs
│       ├── generation_config.py # Load prompts, models, DATA_DIR from config
│       ├── section_generator.py # HTML sections, rate-limit retry, validation (lxml)
│       ├── toc_generator.py     # TOC generation (structured outputs)
│       ├── tool_generator.py    # Ideation / tool_info (structured outputs)
│       └── typings.py           # GeneratorConfig, DatasetConfig
├── src/
│   ├── core/
│   │   └── settings.py   # Pydantic settings from .env
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── openai_client.py    # get_openai_client()
├── logs/                 # Application logs (generated)
├── rag_store/            # ChromaDB vector store (generated)
├── .gitignore
├── env.example           # Environment variables template
├── main.py               # Application entry point
├── Makefile              # install, lint, format, type-check, run, test-connection
├── pyproject.toml        # Project config, black/ruff/mypy
├── requirements.txt      # Python dependencies
├── setup.py              # Minimal setup for backward compatibility
├── test_connection.py    # Test OpenAI/LiteLLM chat and embeddings
└── README.md
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
   Or: `make install-dev`

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
| `DEFAULT_MODEL` | Default LLM model (fallback when no model_key) | `l2-gpt-4o-mini` |
| `EMBEDDING_MODEL` | Embedding model for RAG | `l2-text-embedding-3-small` |
| `TEMPERATURE` | LLM temperature (0.0–2.0) | `0.7` |
| `MAX_TOKENS` | Maximum tokens per request | `2000` |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB persistence directory | `./rag_store` |
| `CHUNK_SIZE` | Text chunk size for splitting | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap size | `200` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FILE` | Log file path | `logs/app.log` |
| `DATA_DIR` | Data directory path | `./data` |

### Generation Config (`config/generation.yaml`)

- **models**: Separate model and temperature per task:
  - `ideation_model`: Tool names and metadata (e.g. `l2-gpt-4o-mini`, temperature 0.8).
  - `toc_model`: Table-of-contents (e.g. `l2-gpt-4o`, temperature 0.7).
  - `section_model`: Section HTML (e.g. `l2-gpt-4.1-nano`, temperature 0.7).
- **dataset**: `num_tools`, `docs_per_tool`, `categories`, `user_bases`, `document_types`.

Prompts for each task are in `config/prompts.yaml`.

## 📖 Usage

### Running the Application

```bash
python main.py
```

Or: `make run`

### Generating the Synthetic Dataset

Use the dataset generation script to create tools, TOCs, and HTML documents:

```bash
# Generate everything (tools → TOCs → sections)
python scripts/dataset/generate_dataset.py --all

# Or step by step:
python scripts/dataset/generate_dataset.py --tools    # Tool folders and tool_info.json
python scripts/dataset/generate_dataset.py --tocs     # toc_<document_type>.json per tool
python scripts/dataset/generate_dataset.py --sections # <document_type>.html per tool
```

If no flag is passed, the script prints help.

### Testing the API Connection

```bash
python test_connection.py
```

Or: `make test-connection`

Tests both chat completions and embeddings using your `.env` configuration.

## 🛠️ Development

### Code Quality Tools

- **Black**: Code formatting
- **Ruff**: Linting and formatting
- **MyPy**: Static type checking

### Commands

```bash
make help           # List all make targets
make lint           # Run ruff check on src/
make lint-fix       # Ruff with auto-fix
make format         # Black and ruff format (src/, main.py)
make type-check     # mypy src/
make clean          # Remove __pycache__, build artifacts
```

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
3. Document your changes in code comments and docstrings

## 📚 Documentation

- Code is documented with docstrings following Google style
- Configuration options are documented in this README and in `config/`
- Prompts and model settings are in `config/prompts.yaml` and `config/generation.yaml`

## 🔒 Security

- Never commit `.env` files with real API keys
- Use environment variables for sensitive configuration
- Keep dependencies up to date for security patches

## 📄 License

This project is developed for HTEC L2 AI Course completion.

## 🗺️ Roadmap

- [x] Implement synthetic data generation (ideation, TOC, sections)
- [x] Structured outputs for JSON (TOC, tool_info)
- [x] Configurable models and temperature per task
- [x] Rate-limit handling and HTML validation for section generation
- [ ] Build document ingestion pipeline
- [ ] Create vector store indexing
- [ ] Develop RAG-based chatbot
- [ ] Add evaluation metrics framework
- [ ] Performance optimization
- [ ] User interface development

---

**Note**: This is an internal tool for HTEC's software whitelisting and verification processes.
