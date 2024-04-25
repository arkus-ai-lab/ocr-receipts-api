import os

CREDENTIALS = os.getenv("HUGGINGFACE_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PROJECT_SETUP = {
    "project_id": "change-me",
    "location": "us",
    "processor_id": "change-me",
    "endpoint": "us-documentai.googleapis.com",     
}
