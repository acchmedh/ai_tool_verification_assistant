import os
from dotenv import load_dotenv
from openai import OpenAI

def get_openai_client():
    """
      Load environment variables and create an OpenAI client instance.

      Returns:
          OpenAI: Configured OpenAI client

      Raises:
          ValueError: If OPENAI_API_KEY is not found in environment variables or .env
      """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables or .env file")
    
    base_url = os.getenv("OPENAI_BASE_URL", "https://litellm.ai.paas.htec.rs")

    return OpenAI(api_key=api_key, base_url=base_url)