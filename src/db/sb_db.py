import os
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

url: str | None = os.getenv("SUPABASE_URL")
key: str | None = os.getenv("SUPABASE_KEY")

if url is None or key is None:
    raise ValueError("Missing Supabase Credentials!")

supabase: Client = create_client(url, key)