import asyncio
import logging
import uvicorn
from aiogram import Bot, Dispatcher
from fastapi import FastAPI

from database.engine import create_db, drop_db, session_maker
from handlers.commands import router
from config_reader import config
from middelwares.db import DataBaseSession
from webhook_server import router as webhook_router
from automatic_billing import scheduler

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

app = FastAPI()
app.include_router(webhook_router)

@app.on_event("startup")
async def start_scheduler():
    scheduler.start()

async def start_uvicorn():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await create_db()
    dp.include_router(router)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    uvicorn_task = asyncio.create_task(start_uvicorn())
    polling_task = asyncio.create_task(dp.start_polling(bot))

    await asyncio.gather(uvicorn_task, polling_task)
    #await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO) #не для прода
    asyncio.run(main())

