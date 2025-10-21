"""Application entrypoint that ties together bot polling and FastAPI webhooks."""
from __future__ import annotations

import asyncio
import logging

import uvicorn
from aiogram import Bot, Dispatcher
from fastapi import FastAPI

from cleanbot.core.settings import settings
from cleanbot.db.session import create_db, session_maker
from cleanbot.handlers.registry import private, router
from cleanbot.middleware.db_session import DatabaseSessionMiddleware
from cleanbot.services.subscription_scheduler import scheduler
from cleanbot.web.hooks import router as webhook_router

bot = Bot(token=settings.bot_token.get_secret_value())
dispatcher = Dispatcher()

app = FastAPI()
app.include_router(webhook_router)


@app.on_event("startup")
async def start_scheduler() -> None:
    scheduler.start()


async def start_uvicorn() -> None:
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    await create_db()
    dispatcher.include_router(router)
    dispatcher.update.middleware(DatabaseSessionMiddleware(session_pool=session_maker))

    await bot.set_my_commands(commands=private)

    uvicorn_task = asyncio.create_task(start_uvicorn())
    polling_task = asyncio.create_task(dispatcher.start_polling(bot))

    await asyncio.gather(uvicorn_task, polling_task)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
