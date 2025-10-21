"""Database helper queries used across the bot."""
from __future__ import annotations

import logging
import time

from sqlalchemy import select, update
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from cleanbot.db.models import Access, Customer

async def orm_add_profession_and_category(session: AsyncSession, profession, category, user_id):
    obj = Customer(
        user_id = user_id,
        profession=profession,
        category=category
    )
    session.add(obj)
    await session.commit()


async def orm_add_customer(session: AsyncSession, data: dict, user_id: int):
    existing_user = await session.execute(select(Customer).where(Customer.user_id == user_id))
    user = existing_user.scalar_one_or_none()

    if user:
        user.name = data['name']
        user.lastname = data['lastname']
        user.link_to_instagram=data['link_to_instagram']
        user.city=data['city']
        user.blog_category=data['blog_category']
        user.number_of_subscribers=data['number_of_subscribers']
        user.coverages=data['coverages']
        user.er=data['er']
        user.link_to_telegram=data['link_to_telegram']
        user.link_to_vk=data['link_to_vk']
        user.link_to_youtube=data['link_to_youtube']
        user.advertising_formats=data['advertising_formats']
        user.cost_of_advertising_in_stories=data['cost_of_advertising_in_stories']
        user.cost_of_advertising_in_a_post=data['cost_of_advertising_in_a_post']
        user.cost_of_advertising_in_reels=data['cost_of_advertising_in_reels']
        user.phone_number=data['phone_number']
        user.email=data['email']
        await session.commit()
        return True
    else:
        return False


async def orm_get_category(session: AsyncSession, user_id: int):
    try:
        query = select(Customer.category).where(Customer.user_id == user_id)
        result = await session.execute(query)
        customer = result.scalar_one_or_none()

        return customer
    except Exception as e:
        logging.error("Не удалось получить категорию клиента %s: %s", user_id, e)
        return None


async def orm_get_profession(session: AsyncSession, user_id: int):
    try:
        query = select(Customer.profession).where(Customer.user_id == user_id)
        result = await session.execute(query)
        customer = result.scalar_one_or_none()

        return customer
    except Exception as e:
        logging.error("Не удалось получить профессию клиента %s: %s", user_id, e)
        return None


async def orm_get_information(session: AsyncSession, user_id: int):
    try:
        query = select(Customer.name, Customer.lastname, Customer.profession, Customer.link_to_instagram,
                       Customer.city, Customer.blog_category, Customer.number_of_subscribers,
                       Customer.coverages, Customer.er, Customer.link_to_telegram, Customer.link_to_vk,
                       Customer.link_to_youtube, Customer.advertising_formats, Customer.cost_of_advertising_in_stories,
                       Customer.cost_of_advertising_in_a_post, Customer.cost_of_advertising_in_reels, Customer.phone_number,
                       Customer.email).where(Customer.user_id == user_id)
        result = await session.execute(query)
        customer = result.fetchone()

        return customer
    except Exception as e:
        logging.error("Не удалось получить данные клиента %s: %s", user_id, e)
        return None


async def orm_update_customer_field(session: AsyncSession, user_id: int, field: str, value: str):
    try:
        query = update(Customer).where(Customer.user_id == user_id).values({field: value})
        await session.execute(query)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e


async def orm_get_information_for_exel(session: AsyncSession):
    try:
        query = select(Customer.name, Customer.lastname, Customer.profession,Customer.link_to_instagram,
                       Customer.city, Customer.blog_category, Customer.number_of_subscribers,
                       Customer.coverages, Customer.er, Customer.link_to_telegram, Customer.link_to_vk,
                       Customer.link_to_youtube, Customer.advertising_formats, Customer.cost_of_advertising_in_stories,
                       Customer.cost_of_advertising_in_a_post, Customer.cost_of_advertising_in_reels, Customer.phone_number,
                       Customer.email)
        result = await session.execute(query)
        customer = result.all()

        return customer
    except Exception as e:
        logging.error("Не удалось получить список клиентов: %s", e)
        return None


async def orm_get_time_sub(session: AsyncSession, user_id: int):
    try:
        query = select(Customer.time_sub).where(Customer.user_id == user_id)
        result = await session.execute(query)
        customer = result.scalar_one_or_none()

        return customer
    except Exception as e:
        logging.error("Не удалось получить время подписки клиента %s: %s", user_id, e)
        return None


async def get_sub_status(session: AsyncSession, user_id: int):
    try:
        query = select(Customer.time_sub).where(Customer.user_id == user_id)
        result = await session.execute(query)
        customer = result.scalar_one_or_none()

        if customer is None:
            return False

        return int(customer) > int(time.time())
    except Exception as e:
        logging.error("Не удалось получить статус подписки клиента %s: %s", user_id, e)
        return None


async def get_type_access(session: AsyncSession, user_id: int):
    try:
        query = select(Access.access_type).where(Access.user_id == user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    except Exception as e:
        logging.error("Не удалось получить тип доступа пользователя %s: %s", user_id, e)
        return None


async def get_sub_end(session: AsyncSession, user_id: int):
    try:
        query = select(Access.time_sub).where(Access.user_id == user_id)
        result = await session.execute(query)
        subscription_end = result.scalar_one_or_none()

        if subscription_end is None:
            return False

        return int(subscription_end) > int(time.time())
    except Exception as e:
        logging.error("Не удалось получить окончание доступа пользователя %s: %s", user_id, e)
        return None



async def save_business_access(session: AsyncSession, user_id: int, access_type: str, subscription_end: int | None):
    try:
        result = await session.execute(select(Access).where(Access.user_id == user_id))
        access = result.scalar_one_or_none()

        if access:
            access.access_type = access_type
            access.subscription_end = subscription_end
        else:
            session.add(Access(user_id=user_id, access_type=access_type, subscription_end=subscription_end))

        await session.commit()
        return True
    except SQLAlchemyError as e:
        logging.error("Ошибка при сохранении доступа пользователя %s: %s", user_id, e)
        await session.rollback()
        return False


async def orm_update_subscription_time(session: AsyncSession, user_id: int, days: int = 30):
    try:
        query = select(Customer).where(Customer.user_id == user_id)
        result = await session.execute(query)
        customer = result.scalar_one_or_none()

        if not customer:
            logging.error(f"Пользователь с user_id={user_id} не найден.")
            return False

        customer.time_sub = int(time.time()) + days * 24 * 60 * 60
        customer.auto_renewal = True
        await session.commit()
        return True
    except Exception as e:
        logging.error(f"Error updating subscription time: {e}")
        return False


async def orm_update_subscription_time_for_table(session: AsyncSession, user_id: int, days: int = 30):
    try:
        query = select(Access).where(Access.user_id == user_id)
        result = await session.execute(query)
        customer = result.scalar_one_or_none()

        if not customer:
            logging.error(f"Пользователь с user_id={user_id} не найден.")
            return False

        customer.time_sub = int(time.time()) + days * 24 * 60 * 60
        customer.access_type = 'subscription'
        customer.auto_renewal = True
        await session.commit()
        return True
    except Exception as e:
        logging.error(f"Error updating subscription time: {e}")
        return False


async def orm_update_trial_time(session: AsyncSession, user_id: int, days: int):
    try:
        query = select(Customer).where(Customer.user_id == user_id)
        result = await session.execute(query)
        customer = result.scalar_one_or_none()

        if not customer:
            logging.error(f"Пользователь с user_id={user_id} не найден.")
            return False

        customer.time_sub = int(time.time()) + days * 24 * 60 * 60
        customer.auto_renewal = True
        customer.is_trial_used = True
        await session.commit()
        return True
    except Exception as e:
        logging.error(f"Error updating subscription time: {e}")
        return False

async def orm_update_access_type_for_table(session: AsyncSession, user_id: int, access_type: str):
    try:
        query = select(Access).where(Access.user_id == user_id)
        result = await session.execute(query)
        customer = result.scalar_one_or_none()

        if not customer:
            logging.error(f"Пользователь с user_id={user_id} не найден.")
            return False

        customer.access_type = access_type
        await session.commit()
        return True
    except Exception as e:
        logging.error(f"Error updating access type: {e}")
        return False


async def orm_unsubscribe_customer(session: AsyncSession, user_id: int):
    try:
        query = select(Customer).where(Customer.user_id == user_id)
        result = await session.execute(query)
        customer_record = result.scalar_one_or_none()

        if not customer_record:
            logging.error(f"Пользователь с user_id={user_id} не найден в Customer.")
            return False

        customer_record.auto_renewal = False
        await session.commit()
        logging.info(f"Подписка отменена для пользователя {user_id} (Customer).")
        return True

    except Exception as e:
        logging.error(f"Ошибка отмены подписки для пользователя {user_id} (Customer): {e}")
        return False


async def orm_unsubscribe_access(session: AsyncSession, user_id: int):
    try:
        query = select(Access).where(Access.user_id == user_id)
        result = await session.execute(query)
        access_record = result.scalar_one_or_none()

        if not access_record:
            logging.error(f"Пользователь с user_id={user_id} не найден в Access.")
            return False

        access_record.auto_renewal = False
        await session.commit()
        logging.info(f"Подписка отменена для пользователя {user_id} (Access).")
        return True

    except Exception as e:
        logging.error(f"Ошибка отмены подписки для пользователя {user_id} (Access): {e}")
        return False


async def orm_save_payment_method_id(session: AsyncSession, user_id: int, payment_method_id: str):
    try:
        logging.info(f"Session type in orm_save_payment_method_id: {type(session)}")
        query = select(Customer).where(Customer.user_id == user_id)
        result = await session.execute(query)
        customer = result.scalar_one_or_none()

        if not customer:
            logging.error(f"Пользователь с user_id={user_id} не найден.")
            return False

        customer.saved_payment_method_id = payment_method_id
        await session.commit()
        return True
    except Exception as e:
        logging.error(f"[orm_save_payment_method_id] Ошибка: {e}")
        return False


async def orm_save_payment_method_id_for_table(session: AsyncSession, user_id: int, payment_method_id: str):
    try:
        logging.info(f"Session type in orm_save_payment_method_id: {type(session)}")
        query = select(Access).where(Access.user_id == user_id)
        result = await session.execute(query)
        customer = result.scalar_one_or_none()

        if not customer:
            logging.error(f"Пользователь с user_id={user_id} не найден.")
            return False

        customer.saved_payment_method_id = payment_method_id
        await session.commit()
        return True
    except Exception as e:
        logging.error(f"[orm_save_payment_method_id] Ошибка: {e}")
        return False




async def get_users_with_expiring_subscriptions(session: AsyncSession, days_before_expiry: int = 0):
    current_time = int(time.time())
    threshold_time = current_time + days_before_expiry * 24 * 60 * 60
    query = select(Customer).where(Customer.time_sub <= threshold_time)
    result = await session.execute(query)
    users = result.scalars().all()

    return users


async def get_save_card_id(session: AsyncSession, user_id: int):
    stmt = select(Customer).where(Customer.user_id == user_id)
    result = await session.execute(stmt)
    customer = result.scalar_one_or_none()

    if customer and customer.saved_payment_method_id:
        return customer.saved_payment_method_id

    return None


async def get_subscription_price(category: str):
    if category == 'blogger':
        return 40000
    else:
        return 30000


async def orm_add_user_id_access(session: AsyncSession, user_id: int):
    try:
        query = select(Access).where(Access.user_id == user_id)
        result = await session.execute(query)
        existing = result.scalar_one_or_none()

        if not existing:
            stmt = insert(Access).values(user_id=user_id)
            await session.execute(stmt)
            await session.commit()
    except Exception as e:
        logging.error(f"Ошибка при добавлении пользователя в Access: {e}")


async def orm_check_trial(session: AsyncSession, user_id: int):
    try:
        query = select(Customer).where(Customer.user_id == user_id)
        result = await session.execute(query)
        customer = result.scalar_one_or_none()

        if customer and not customer.is_trial_used:
            return True
        return False
    except Exception as e:
        logging.error(f"Ошибка проверки пробного периода для user_id={user_id}: {e}")
        return False


async def orm_save_user_consent(session: AsyncSession, user_id: int):
    try:
        result = await session.execute(
            select(Customer).where(Customer.user_id == user_id)
        )
        customer = result.scalars().first()
        if customer:
            customer.is_policy_accepted = True
            await session.commit()
        else:
            logging.warning(f"User with id {user_id} not found when saving consent")
    except Exception as e:
        logging.error(f"Error saving user consent for user_id {user_id}: {e}")
