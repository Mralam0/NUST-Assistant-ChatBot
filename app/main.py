import os
import json
import logging
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import search

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "query_log.txt")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("faq_chatbot")

app = FastAPI(title="NUST FAQ Chatbot")

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


class QueryRequest(BaseModel):
    query: str


@app.on_event("startup")
def startup():
    logger.info("Initializing FAQ search engine...")
    search.init()
    logger.info("FAQ search engine ready.")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/ask")
async def ask(payload: QueryRequest):
    query = payload.query.strip()
    if not query:
        return JSONResponse({"error": "Empty query"}, status_code=400)

    matches = search.find_matches(query, related_limit=3)
    best_match = matches["best_match"]
    related = matches["related"]

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {query}\n")

    if best_match is None:
        return {
            "answer": "Sorry, I couldn't find a strong direct answer. You can try one of the related questions below or rephrase your question.",
            "related": related,
        }

    return {
        "answer": best_match["answer"],
        "matched_question": best_match["question"],
        "confidence": best_match["score"],
        "related": related,
    }


@app.post("/api/rebuild")
async def rebuild():
    search.rebuild_index()
    return {"status": "Index rebuilt successfully"}


@app.get("/api/faqs")
async def get_faqs():
    from embed import load_faqs
    return load_faqs()


@app.post("/api/faqs")
async def update_faqs(request: Request):
    data = await request.json()
    faq_path = os.path.join(BASE_DIR, "faq.json")
    with open(faq_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    search.rebuild_index()
    return {"status": "FAQs updated and index rebuilt"}
