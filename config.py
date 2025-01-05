from hashlib import md5

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from pydantic_settings import BaseSettings
from starlette.templating import Jinja2Templates

render = Jinja2Templates(directory="templates").TemplateResponse


class Settings(BaseSettings):
    BOT_TOKEN: str
    WEBHOOK_URL: str

    class Config:
        env_file = ".env"


settings = Settings()

bot = Bot(settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode='html'))
dp = Dispatcher()

WEBHOOK_PATH = md5(settings.BOT_TOKEN.encode()).hexdigest()
ROOM_MANAGER = {}
