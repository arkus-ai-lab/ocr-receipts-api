import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PROJECT_SETUP = {
    "project_id": os.getenv("PROJECT_ID"),
    "location": "us",
    "processor_id": os.getenv("PROCESSOR_ID"),
    "endpoint": "us-documentai.googleapis.com",     
}