"""Configuration for Streamlit frontend."""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8001")
PROCESSING_SERVICE_URL = os.getenv("PROCESSING_SERVICE_URL", "http://localhost:8000")

# App Configuration
APP_TITLE = "AI Research Trends Discovery"
APP_ICON = "🔬"
APP_DESCRIPTION = "Discover emerging AI research trends using natural language"

# UI Configuration
MAX_RESULTS = 10
DEFAULT_TOP_K = 5
QUERY_TIMEOUT = 30  # seconds

# Example queries
EXAMPLE_QUERIES = [
    "What are the latest developments in transformer models?",
    "Explain vision transformers and their applications",
    "What are emerging trends in large language models?",
    "How is reinforcement learning being used in robotics?",
    "What are the recent advances in multi-modal learning?",
    "Explain self-supervised learning techniques",
    "What are the challenges in training large neural networks?",
    "How are diffusion models being used for image generation?"
]

# arXiv Categories
ARXIV_CATEGORIES = {
    "cs.AI": "Artificial Intelligence",
    "cs.CL": "Computation and Language",
    "cs.CV": "Computer Vision",
    "cs.LG": "Machine Learning",
    "cs.NE": "Neural and Evolutionary Computing",
    "cs.RO": "Robotics",
    "stat.ML": "Machine Learning (Statistics)"
}

# Major AI Venues
AI_VENUES = [
    "NeurIPS", "ICML", "ICLR", "CVPR", "ICCV", "ECCV",
    "ACL", "EMNLP", "AAAI", "IJCAI", "AISTATS"
]
