from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
import time
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
import datetime
from config_reader import config
from database.engine import get_async_session
from database.models import Access, Customer
from database.orm_query import get_users_with_expiring_subscriptions, get_save_card_id, get_subscription_price, \
    orm_update_subscription_time, orm_update_subscription_time_for_table
from handlers.auto_payment import create_recurring_payment
from sqlalchemy import select

from keyboards.keyboard import unsubscribe_keyboard_customer, unsubscribe_keyboard_access

scheduler = AsyncIOScheduler()
bot = Bot(token=config.bot_token.get_secret_value())

@scheduler.scheduled_job('interval', days=1)
async def check_and_charge_subscriptions():
    logging.info("🔄 Запущена задача проверки и продления подписок...")

    try:
        async with get_async_session() as session:
            await notify_users_about_expiring_subscriptions(session)
            await renew_expired_subscriptions(session)
    except Exception as e:
        logging.error(f"Ошибка при проверке подписок: {e}")


async def renew_expired_subscriptions(session: AsyncSession):
    try:
        current_time = int(time.time())

        stmt = select(Customer).where(Customer.time_sub <= current_time)
        result = await session.execute(stmt)
        users = result.scalars().all()

        for user in users:
            logging.info(f"Проверка подписки для пользователя {user.user_id}")
            if user.saved_payment_method_id:
                payment = create_recurring_payment(
                    user.user_id,
                    user.saved_payment_method_id,
                    await get_subscription_price(user.category),
                    "subscription"
                )
                if payment and payment.status == "succeeded":
                    success = await orm_update_subscription_time(session, user.user_id)
                    if success:
                        logging.info(f"Подписка продлена для пользователя {user.user_id}")
                    else:
                        logging.error(f"Не удалось обновить время подписки для пользователя {user.user_id}")
                else:
                    logging.error(f"Ошибка при создании платежа для пользователя {user.user_id}")
            else:
                logging.info(f"У пользователя {user.user_id} нет сохраненного метода оплаты")

        stmt_access = select(Access).where(
            Access.time_sub <= current_time,
            Access.auto_renewal == True,
            Access.access_type == 'subscription'
        )
        result_access = await session.execute(stmt_access)
        access_users = result_access.scalars().all()

        for user in access_users:
            logging.info(f"Проверка подписки (Access) для пользователя {user.user_id}")
            if user.saved_payment_method_id:
                payment = create_recurring_payment(
                    user.user_id,
                    user.saved_payment_method_id,
                    300000,
                    'table'
                )
                if payment and payment.status == "succeeded":
                    success = await orm_update_subscription_time_for_table(session, user.user_id)
                    if success:
                        logging.info(f"Подписка продлена для пользователя {user.user_id} (Access)")
                    else:
                        logging.error(f"Не удалось обновить время подписки для пользователя {user.user_id} (Access)")
                else:
                    logging.error(f"Ошибка при создании платежа для пользователя {user.user_id} (Access)")
            else:
                logging.info(f"У пользователя {user.user_id} (Access) нет сохраненного метода оплаты")

    except Exception as e:
        logging.error(f"Ошибка при проверке подписок: {e}")


async def notify_users_about_expiring_subscriptions(session: AsyncSession):
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
                reply_markup=unsubscribe_keyboard_customer()
            )
            logging.info(f"Отправлено уведомление пользователю {user.user_id} (Customer)")
        except Exception as e:
            logging.error(f"Ошибка отправки уведомления пользователю {user.user_id} (Customer): {e}")



    stmt_access = select(Access).where(
        Access.time_sub.between(notify_time_lower, notify_time_upper),
        Access.auto_renewal == True,
        Access.access_type == 'subscription'
    )
    result_access = await session.execute(stmt_access)
    access_users = result_access.scalars().all()

    for user in access_users:
        try:
            logging.info(f"Отправка уведомления Access пользователю {user.user_id}")
            await bot.send_message(
                user.user_id,
                "⏳ Ваш доступ к таблице истекает через 1 день. Скоро произойдет списание.",
                reply_markup=unsubscribe_keyboard_access()
            )
            logging.info(f"Отправлено уведомление пользователю {user.user_id} (Access)")
        except Exception as e:
            logging.error(f"Ошибка отправки уведомления пользователю {user.user_id} (Access): {e}")
