from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("GOOGLE_API_KEY")

if key:
    print(f"✅ API key loaded: {key[:6]}...{key[-4:]}")
else:
    print("❌ API key not found.")
