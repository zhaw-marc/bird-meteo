import google.generativeai as genai
import os
import toml

# Pfad zur secrets.toml
secrets_path = ".streamlit/secrets.toml"

if os.path.exists(secrets_path):
    secrets = toml.load(secrets_path)
    api_key = secrets.get("GEMINI_API_KEY")
    
    if api_key:
        genai.configure(api_key=api_key)
        print("Checking available models...\n")
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f"Model: {m.name}")
                    print(f"  Display Name: {m.display_name}")
                    print(f"  Description: {m.description}\n")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("GEMINI_API_KEY not found in secrets.toml")
else:
    print(".streamlit/secrets.toml not found")
