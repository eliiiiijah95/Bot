"""Background tasks responsible for subscription renewals and notifications."""
from __future__ import annotations

import datetime
import logging
import time

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cleanbot.core.settings import settings
from cleanbot.db.models import Access, Customer
from cleanbot.db.queries import (
    get_subscription_price,
    orm_update_subscription_time,
    orm_update_subscription_time_for_table,
)
from cleanbot.db.session import get_async_session
from cleanbot.integrations.yookassa import create_recurring_payment
from cleanbot.ui.keyboards import (
    unsubscribe_keyboard_access,
    unsubscribe_keyboard_customer,
)

scheduler = AsyncIOScheduler()
bot = Bot(token=settings.bot_token.get_secret_value())


@scheduler.scheduled_job("interval", days=1)
async def check_and_charge_subscriptions() -> None:
    logging.info("🔄 Запущена задача проверки и продления подписок...")

    try:
        async with get_async_session() as session:
            await notify_users_about_expiring_subscriptions(session)
            await renew_expired_subscriptions(session)
    except Exception as exc:  # pragma: no cover - defensive guard
        logging.error("Ошибка при проверке подписок: %s", exc)


async def renew_expired_subscriptions(session: AsyncSession) -> None:
    try:
        current_time = int(time.time())

        stmt = select(Customer).where(Customer.time_sub <= current_time)
        result = await session.execute(stmt)
        users = result.scalars().all()

        for user in users:
            logging.info("Проверка подписки для пользователя %s", user.user_id)
            if user.saved_payment_method_id:
                payment = create_recurring_payment(
                    user.user_id,
                    user.saved_payment_method_id,
                    await get_subscription_price(user.category),
                    "subscription",
                )
                if payment and payment.status == "succeeded":
                    success = await orm_update_subscription_time(session, user.user_id)
                    if success:
                        logging.info("Подписка продлена для пользователя %s", user.user_id)
                    else:
                        logging.error("Не удалось обновить время подписки для пользователя %s", user.user_id)
                else:
                    logging.error("Ошибка при создании платежа для пользователя %s", user.user_id)
            else:
                logging.info("У пользователя %s нет сохраненного метода оплаты", user.user_id)

        stmt_access = select(Access).where(
            Access.time_sub <= current_time,
            Access.auto_renewal.is_(True),
            Access.access_type == "subscription",
        )
        result_access = await session.execute(stmt_access)
        access_users = result_access.scalars().all()

        for user in access_users:
            logging.info("Проверка подписки (Access) для пользователя %s", user.user_id)
            if user.saved_payment_method_id:
                payment = create_recurring_payment(
                    user.user_id,
                    user.saved_payment_method_id,
                    300000,
                    "table",
                )
                if payment and payment.status == "succeeded":
                    success = await orm_update_subscription_time_for_table(session, user.user_id)
                    if success:
                        logging.info("Подписка продлена для пользователя %s (Access)", user.user_id)
                    else:
                        logging.error("Не удалось обновить время подписки для пользователя %s (Access)", user.user_id)
                else:
                    logging.error("Ошибка при создании платежа для пользователя %s (Access)", user.user_id)
            else:
                logging.info("У пользователя %s (Access) нет сохраненного метода оплаты", user.user_id)

    except Exception as exc:  # pragma: no cover - defensive guard
        logging.error("Ошибка при проверке подписок: %s", exc)


async def notify_users_about_expiring_subscriptions(session: AsyncSession) -> None:
    now = datetime.datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + datetime.timedelta(days=1)
    tomorrow_end = tomorrow_start + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)

    notify_time_lower = int(tomorrow_start.timestamp())
    notify_time_upper = int(tomorrow_end.timestamp())

    stmt_customer = select(Customer).where(Customer.time_sub.between(notify_time_lower, notify_time_upper))
    result_customer = await session.execute(stmt_customer)
    customers = result_customer.scalars().all()

    for user in customers:
        try:
            await bot.send_message(
                user.user_id,
                "⏳ Ваша подписка истекает через 1 день. Скоро произойдет списание.",
                reply_markup=unsubscribe_keyboard_customer(),
            )
            logging.info("Отправлено уведомление пользователю %s (Customer)", user.user_id)
        except Exception as exc:  # pragma: no cover - network issues
            logging.error("Ошибка отправки уведомления пользователю %s (Customer): %s", user.user_id, exc)

    stmt_access = select(Access).where(
        Access.time_sub.between(notify_time_lower, notify_time_upper),
        Access.auto_renewal.is_(True),
        Access.access_type == "subscription",
    )
    result_access = await session.execute(stmt_access)
    access_users = result_access.scalars().all()

    for user in access_users:
        try:
            logging.info("Отправка уведомления Access пользователю %s", user.user_id)
            await bot.send_message(
                user.user_id,
                "⏳ Ваш доступ к таблице истекает через 1 день. Скоро произойдет списание.",
                reply_markup=unsubscribe_keyboard_access(),
            )
            logging.info("Отправлено уведомление пользователю %s (Access)", user.user_id)
        except Exception as exc:  # pragma: no cover - network issues
            logging.error("Ошибка отправки уведомления пользователю %s (Access): %s", user.user_id, exc)
