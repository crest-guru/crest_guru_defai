from eth_account.messages import encode_defunct
from web3.auto import w3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

# Создаем модель для запроса
class WalletCreateRequest(BaseModel):
    address: str

app = FastAPI()

# Настройка CORS - оставляем только одну настройку
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

def verify_signature(address: str, message: str, signature: str) -> bool:
    message_hash = encode_defunct(text=message)
    recovered_address = w3.eth.account.recover_message(message_hash, signature=signature)
    return recovered_address.lower() == address.lower()

@app.post("/api/wallet/create")
async def create_wallet(request: WalletCreateRequest):
    try:
        # Здесь ваша логика создания кошелька
        # Пример ответа:
        return {
            "safe_address": "0x64518d15e6306ce4FCa2eedD19480172a244b0E5",
            "cobo_address": "0xF948b577A7cd235e439616DdDbC844211E5a5087",
            "approve_authorizer_address": "0x80C3ed92F216a91F9485f79F252791937fF2134f",
            "transfer_authorizer_address": "0xD1E18B60234D394bd700D2D6AdeB392699Db6B66"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wallet/info")
async def get_wallet_info(address: str):
    try:
        # Здесь будет реальный запрос к API
        response = await get_actual_wallet_info(address)  # Это просто для примера
        return response  # Просто возвращаем то, что пришло от API
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 