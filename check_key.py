import os
import openai
from openai import OpenAI, AuthenticationError
from dotenv import load_dotenv

# 1. Load the environment variables from the .env file
load_dotenv()

def check_openai_api_key_from_env() -> bool:
    """
    Checks the validity of the OpenAI API key loaded from the environment 
    variable 'OPENAI_API_KEY'.
    
    Returns:
        True if the API key is valid and authenticated, False otherwise.
    """
    # 2. Retrieve the key from the environment
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ Error: 'OPENAI_API_KEY' not found in environment variables or .env file.")
        return False
        
    print("Attempting to validate API key...")
    
    try:
        # 3. Initialize the client using the retrieved key
        # The OpenAI client will automatically pick up the API key 
        # from the 'api_key' argument.
        client = OpenAI(api_key=api_key)
        
        # 4. Make a minimal API call to test authentication
        client.models.list()
        
    except AuthenticationError:
        # This exception is raised for invalid/expired/revoked keys 
        # or if the account has a billing issue.
        return False
    except Exception as e:
        # Catch other potential errors (e.g., network issues)
        print(f"⚠️ An unexpected error occurred (Network/Rate Limit): {e}")
        return False 
    else:
        # If the API call succeeds without an AuthenticationError
        return True

# --- Execution ---
if check_openai_api_key_from_env():
    print("\n✅ The OpenAI API key loaded from .env is **VALID**.")
else:
    print("\n❌ The OpenAI API key is **INVALID** or has an authentication issue.")