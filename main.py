from aiogram import types
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

import bot_src  # noqa
import web_src
from config import bot, settings, WEBHOOK_PATH, dp
from web_src.tv_remote import router

app = FastAPI()

# Enable CORS for all domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
app.include_router(router)

@app.on_event('startup')
async def startup():
    await bot.delete_webhook(drop_pending_updates=True)
    webhook_url = settings.WEBHOOK_URL + 'webhook/' + WEBHOOK_PATH
    await bot.set_webhook(url=webhook_url)


@app.post('/webhook/{secret_key}')
async def webhook_bot(secret_key: str, update: types.Update):
    if secret_key != WEBHOOK_PATH:
        raise HTTPException(status_code=400, detail='Nima gap jigar?')
    await dp.feed_update(bot, update)
