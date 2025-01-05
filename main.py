from aiogram import types
from fastapi import FastAPI, HTTPException

import bot_src, web_src  # noqa
from web_src.tv_remote import router
from config import bot, settings, WEBHOOK_PATH, dp

app = FastAPI()
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
