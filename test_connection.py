"""
Test script to verify OpenAI/LiteLLM connection and configuration.

This script tests both the chat completion API and embedding API
to ensure the connection is working properly.
"""

from loguru import logger

from src.core.settings import settings
from src.utils.logger import setup_logger
from src.utils.openai_client import get_openai_client


def test_chat_completion() -> bool:
    """Test the chat completion API."""
    try:
        logger.info("Testing chat completion API...")
        client = get_openai_client()

        response = client.chat.completions.create(
            model=settings.default_model,
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello, connection test successful!' and nothing else.",
                }
            ],
            max_tokens=50,
            temperature=0.0,
        )

        message = response.choices[0].message.content
        logger.success(f"✅ Chat completion test passed!")
        logger.info(f"Response: {message}")
        return True

    except Exception as e:
        logger.error(f"❌ Chat completion test failed: {e}")
        return False


def test_embeddings() -> bool:
    """Test the embeddings API."""
    try:
        logger.info("Testing embeddings API...")
        client = get_openai_client()

        response = client.embeddings.create(
            model=settings.embedding_model,
            input="test connection",
        )

        embedding = response.data[0].embedding
        logger.success(f"✅ Embeddings test passed!")
        logger.info(f"Embedding dimension: {len(embedding)}")
        return True

    except Exception as e:
        logger.error(f"❌ Embeddings test failed: {e}")
        return False


def main() -> None:
    """Run all connection tests."""
    setup_logger()

    logger.info("=" * 60)
    logger.info("OpenAI/LiteLLM Connection Test")
    logger.info("=" * 60)
    logger.info(f"Base URL: {settings.openai_base_url}")
    logger.info(f"Chat Model: {settings.default_model}")
    logger.info(f"Embedding Model: {settings.embedding_model}")
    logger.info("=" * 60)
    logger.info("")

    results = {
        "Chat Completion": test_chat_completion(),
        "Embeddings": test_embeddings(),
    }

    logger.info("")
    logger.info("=" * 60)
    logger.info("Test Results Summary")
    logger.info("=" * 60)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name}: {status}")

    all_passed = all(results.values())
    logger.info("=" * 60)

    if all_passed:
        logger.success("🎉 All tests passed! Your OpenAI connection is working.")
        exit(0)
    else:
        logger.error("⚠️  Some tests failed. Please check your configuration.")
        exit(1)


if __name__ == "__main__":
    main()
