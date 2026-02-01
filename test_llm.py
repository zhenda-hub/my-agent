"""Test LLM API call"""
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Fix Windows console encoding issue
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_direct_openai_sdk():
    """Test direct OpenAI SDK call to OpenRouter"""
    api_key = os.getenv("OPENROUTER_API_KEY", "")

    if not api_key:
        print("[ERROR] Please set OPENROUTER_API_KEY environment variable first!")
        print("\nHow to set:")
        print("  Option 1 - Create .env file:")
        print("    OPENROUTER_API_KEY=sk-or-v1-xxx")
        print("  Option 2 - Set environment variable:")
        print("    CMD: set OPENROUTER_API_KEY=sk-or-v1-xxx")
        print("    PowerShell: $env:OPENROUTER_API_KEY='sk-or-v1-xxx'")
        return False

    print(f"[INFO] Testing with API Key: {api_key[:15]}...{api_key[-4:]}")

    # Initialize OpenAI client with OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    print("\n[TEST 1] Direct OpenAI SDK call (as reference)")
    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Test passed'"
                }
            ]
        )
        result = completion.choices[0].message.content
        print(f"[OK] Test 1 passed! Response: {result}")
    except Exception as e:
        print(f"[ERROR] Test 1 failed: {e}")
        return False

    print("\n[TEST 2] LLMManager.generate() method")
    try:
        from src.chains.llm_manager import LLMManager
        llm = LLMManager(api_key=api_key, default_model="deepseek")
        result = llm.generate("Say 'LLMManager test passed'")
        print(f"[OK] Test 2 passed! Response: {result}")
    except Exception as e:
        print(f"[ERROR] Test 2 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n[TEST 3] LLMManager.chat() method")
    try:
        from src.chains.llm_manager import LLMManager
        llm = LLMManager(api_key=api_key, default_model="deepseek")
        messages = [{"role": "user", "content": "Say 'Chat test passed'"}]
        result = llm.chat(messages)
        print(f"[OK] Test 3 passed! Response: {result}")
    except Exception as e:
        print(f"[ERROR] Test 3 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 50)
    print("[SUCCESS] All tests passed!")
    print("=" * 50)
    return True


if __name__ == "__main__":
    test_direct_openai_sdk()
