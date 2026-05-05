import httpx
import os
from dotenv import load_dotenv

load_dotenv()

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
HELIUS_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

async def fetch_transaction_logs(signature: str):
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {"encoding": "json", "maxSupportedTransactionVersion": 0}
        ]
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(HELIUS_URL, json=payload)
        data = response.json()

    if "error" in data:
        return None, f"RPC Error: {data['error']['message']}"

    result = data.get("result")
    if not result:
        return None, "Transaction not found."

    logs = result.get("meta", {}).get("logMessages", [])
    error = result.get("meta", {}).get("err", None)

    return {"logs": logs, "error": error}, None