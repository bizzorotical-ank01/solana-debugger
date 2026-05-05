from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from rpc import fetch_transaction_logs
from ai import explain_error
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class DebugRequest(BaseModel):
    input: str

@app.get("/")
def root():
    return {"status": "SolanaDebugger is running"}

@app.post("/debug")
async def debug(req: DebugRequest):
    user_input = req.input.strip()

    # check if it looks like a transaction signature (base58, 87-88 chars)
    if len(user_input) > 60 and "\n" not in user_input:
        tx_data, error = await fetch_transaction_logs(user_input)
        if error:
            return {"error": error}
        logs = tx_data["logs"]
        error_on_chain = tx_data["error"]
    else:
        # treat as raw log paste
        logs = user_input.split("\n")
        error_on_chain = {}

    ai_result = await explain_error(logs, error_on_chain)

    return {
        "logs": logs,
        "error_on_chain": error_on_chain,
        "ai_explanation": ai_result
    }