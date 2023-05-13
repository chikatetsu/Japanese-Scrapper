from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")
search_engine = os.getenv("API_SEARCH_ENGINE")
service = build('customsearch', 'v1', developerKey=api_key)

result = service.cse().list(
    q="search example",
    cx=search_engine,
).execute()

totalResults = result['queries']['request'][0]['totalResults']
print(totalResults+"\n")
