"""YooKassa payment helpers."""
from __future__ import annotations

import uuid

from yookassa import Configuration, Payment

from cleanbot.core.settings import settings

Configuration.account_id = settings.yookassa_account_id
Configuration.secret_key = settings.yookassa_secret_key.get_secret_value()


def create_initial_payment(user_id: int, amount_rub: int, payment_type: str):
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create(
        {
            "amount": {
                "value": f"{amount_rub / 100:.2f}",
                "currency": "RUB",
            },
            "payment_method_data": {
                "type": "bank_card",
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/offical_blogger_registry_bot",
            },
            "description": "Оплата подписки",
            "save_payment_method": True,
            "capture": True,
            "metadata": {
                "user_id": str(user_id),
                "type": payment_type,
            },
        },
        idempotence_key,
    )

    return payment.confirmation.confirmation_url, payment.id


def create_recurring_payment(user_id: int, saved_card_id: int, amount_rub: int, payment_type: str):
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create(
        {
            "amount": {
                "value": f"{amount_rub / 100:.2f}",
                "currency": "RUB",
            },
            "capture": True,
            "payment_method_id": saved_card_id,
            "description": "Автосписание подписки",
            "metadata": {
                "user_id": str(user_id),
                "type": payment_type,
            },
        },
        idempotence_key,
    )
    return payment
