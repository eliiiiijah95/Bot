from yookassa import Payment, Configuration
import uuid

Configuration.account_id = '1073761'
Configuration.secret_key = 'test_Giw-Q_q9TVUZhcZIUPdAwETdQD1vjtZr8rgtTnxDyZg'

def create_initial_payment(user_id, amount_rub, payment_type):
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": f"{amount_rub / 100:.2f}",
            "currency": "RUB",
        },
        "payment_method_data": {
            "type": "bank_card",
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/alert_for_task_bot"
        },
        "description": "Оплата подписки",
        "save_payment_method": True,
        "capture": True,
        "metadata": {
            "user_id": str(user_id),
            "type" : payment_type
        }
    }, idempotence_key)

    return payment.confirmation.confirmation_url, payment.id


def create_recurring_payment(user_id: int, saved_card_id: int, amount_rub: int, payment_type):
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": f"{amount_rub / 100:.2f}",
            "currency": "RUB"
        },
        "capture": True,
        "payment_method_id": saved_card_id,
        "description": "Автосписание подписки",
        "metadata": {
            "user_id": str(user_id),
            "type": payment_type
        }
    }, idempotence_key)
    return payment