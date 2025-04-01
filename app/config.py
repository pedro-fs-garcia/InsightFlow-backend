from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "default_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "insightflow")
DB_PORT = os.getenv("DB_PORT", "3306")

BACKEND_SERVER=os.getenv("BACKEND_SERVER", "http://localhost:5000")
FRONTEND_SERVER=os.getenv("FRONTEND_SERVER", "http://localhost:5173")