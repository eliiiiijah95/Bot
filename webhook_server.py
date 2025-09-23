from fastapi import APIRouter, Request, Depends
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot

from database.engine import get_async_session_dependency
from database.orm_query import orm_update_subscription_time, orm_save_payment_method_id, \
    orm_update_subscription_time_for_table, orm_save_payment_method_id_for_table, orm_update_access_type_for_table, \
    orm_update_trial_time
from config_reader import config
from keyboards.keyboard import keyboard_start_questionnaire, get_table_to_view

router = APIRouter()
bot = Bot(token=config.bot_token.get_secret_value())

@router.post("/webhook/yookassa")
async def yookassa_webhook(request: Request,  session: AsyncSession = Depends(get_async_session_dependency)):
    data = await request.json()
    logging.info(f"Webhook от Юкассы: {data}")

    if data['event'] == 'payment.succeeded':
        payment = data['object']
        user_id = int(payment['metadata']['user_id'])
        payment_type = payment['metadata'].get('type')


        if payment_type == 'subscription':
            await orm_update_subscription_time(session, user_id, days=30)
            payment_method_id = payment.get('payment_method', {}).get('id')
            if payment_method_id:
                await orm_save_payment_method_id(session, user_id, payment_method_id)
                await bot.send_message(
                    user_id,
                    "✅ Оплата прошла успешно! Нажмите кнопку ниже, чтобы заполнить анкету.",
                    reply_markup=keyboard_start_questionnaire()
                )

        elif payment_type == 'table':
            await orm_update_subscription_time_for_table(session, user_id, days=30)
            payment_method_id = payment.get('payment_method', {}).get('id')
            if payment_method_id:
                await orm_save_payment_method_id_for_table(session, user_id, payment_method_id)
                await bot.send_message(
                    user_id,
                    "✅ Оплата за доступ к таблице прошла успешно! Вам открыт доступ на 30 дней.\n"
                    "Правила:\n"
                    "1. Распространение таблицы и передача доступа третьим лицам — запрещены.\n"
                    "2.  Деньги за подписку не возвращаются, если доступ уже открыт.\n"
                    "3. Вся информация предоставляется для сотрудничества, а не массовых рассылок.\n"
                    "4. При нарушении правил доступ может быть ограничен.\n",
                    reply_markup=get_table_to_view()
                )


        elif payment_type == 'table_lifetime':
            await orm_update_access_type_for_table(session, user_id, 'lifetime')
            payment_method_id = payment.get('payment_method', {}).get('id')
            if payment_method_id:
                await orm_save_payment_method_id_for_table(session, user_id, payment_method_id)

            await bot.send_message(
                user_id,
                "✅ Вам предоставлен бессрочный доступ к таблице!\n"
                "Правила:\n"
                "1. Распространение таблицы и передача доступа третьим лицам — запрещены.\n"
                "2.  Деньги за подписку не возвращаются, если доступ уже открыт.\n"
                "3. Вся информация предоставляется для сотрудничества, а не массовых рассылок.\n"
                "4. При нарушении правил доступ может быть ограничен.",
                reply_markup=get_table_to_view()
            )


        elif payment_type == 'trial':
            await orm_update_trial_time(session, user_id, days = 30)
            payment_method_id = payment.get('payment_method', {}).get('id')
            if payment_method_id:
                await orm_save_payment_method_id(session, user_id, payment_method_id)
                await bot.send_message(
                    user_id,
                    "✅ Вы активировали пробный период на 30 дней за 1 ₽. \n"
                    "Нажмите кнопку ниже, чтобы заполнить анкету.\n"
                    "Пробный доступ для блогеров и контент специалистов:\n"
                    "1 месяц с момента оплаты\n"
                    "Дальше автоматическая подписка ❤️\n",
                    reply_markup=keyboard_start_questionnaire()
                )

    return {"status": "ok"}
