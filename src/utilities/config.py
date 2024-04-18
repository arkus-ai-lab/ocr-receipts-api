import os

CREDENTIALS = os.getenv("HUGGINGFACE_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PROJECT_SETUP = {
    "project_id": os.getenv("PROJECT_ID"),
    "location": os.getenv("LOCATION"),
    "processor_id": os.getenv("PROCESSOR_ID"),
    "endpoint": os.getenv("ENDPOINT"),
}
