import re
import time


import pandas as pd
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, FSInputFile, LabeledPrice, PreCheckoutQuery, ReplyKeyboardRemove, \
    BotCommand

from sqlalchemy.ext.asyncio import AsyncSession

import logging

from config_reader import config
from database.orm_query import (orm_add_customer, orm_get_information, orm_update_customer_field,
                                orm_get_information_for_exel, orm_get_time_sub, orm_add_profession_and_category,
                                orm_get_category, orm_get_profession, get_sub_status, save_business_access,
                                get_type_access, get_sub_end, orm_add_user_id_access, orm_unsubscribe_access,
                                orm_unsubscribe_customer, orm_check_trial, orm_save_user_consent)

from keyboards.keyboard import (main_menu_keyboard, first_time_menu_keyboard, social_media_keyboard,
                                profession_selection_keyboard, action_selection_keyboard, company_check_keyboard,
                                subscription_options_keyboard, confirm_subscription_keyboard,
                                existing_user_menu_keyboard, to_change_information, to_change_contacts, skip,
                                confirm_conditions, help_keyboard)
from payment import days_to_seconds, time_sub_day
from handlers.auto_payment import create_initial_payment

router = Router()



class AddCustomer(StatesGroup):
    name = State()
    profession = State() # Отдельно
    lastname = State()
    link_to_instagram = State()
    city = State()
    blog_category = State ()
    number_of_subscribers = State()
    coverages = State()
    er = State()
    link_to_telegram = State()
    link_to_vk = State()
    link_to_youtube = State()
    advertising_formats = State()
    cost_of_advertising_in_stories = State()
    cost_of_advertising_in_a_post = State()
    cost_of_advertising_in_reels = State()
    phone_number = State()
    email = State()
    time_sub = State() # Отдельно
    category = State()

class EditCustomer(StatesGroup):
    waiting_for_value = State()
    current_field = State()




@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(f'Привет, {message.from_user.first_name}. Выбери пункт ниже ⬇️',
                        reply_markup=main_menu_keyboard())


private = [
    BotCommand(command='menu', description='Перейти в главное меню'),
    BotCommand(command='help', description='Написать в поддержку')
]


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.reply(f'{message.from_user.first_name}. Это главное меню ⬇️',
                        reply_markup=main_menu_keyboard())


@router.message(Command("help"))
async def cmd_menu(message: Message):
    await message.reply(f'{message.from_user.first_name}. Если у вас возник вопрос или проблема, напишите поддержку',
                        reply_markup=help_keyboard())


@router.callback_query(F.data == 'first_time')
async def first_time(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(f'{callback.from_user.first_name}, '
                                  f'о чем ты хочешь больше всего узнать?',
                                  reply_markup=first_time_menu_keyboard())


@router.callback_query(F.data == 'about_project')
async def about_project(callback: CallbackQuery):
    await callback.answer()
    text = """Реестр блогеров и контент-специалистов

Реестр — это закрытая база, которая соединяет блогеров, бренды и специалистов в сфере контента. Здесь бизнес находит идеальных инфлюенсеров и профессионалов для продвижения, а блогеры получают рекламные предложения, новые связи и возможности для роста.  

Как это работает?
✅ Блогеры добавляют себя в реестр, заполняя анкету с данными о своей аудитории, тематике и расценках.  
✅ Контент-специалисты (фотографы, стилисты, SMM-менеджеры, пиарщики, модели, визажисты и др.) предлагают свои услуги блогерам и брендам.  
✅ Бренды покупают доступ к базе и находят подходящих блогеров и специалистов для рекламы и контента.  

Почему это выгодно блогерам?  
🔥 Больше рекламы – бренды сами находят тебя и делают предложения.  
📢 Прозрачные условия – твои расценки сразу видны, нет бесконечных переговоров.  
🤝 Нетворкинг и новые коллаборации – доступ к профессиональным фотографам, стилистам, моделям, которые помогут сделать контент топовым.  
🚀 Растущий спрос – бизнесу нужны блогеры и эксперты в контенте, а ты уже в числе первых в удобном реестре.  

Почему это выгодно контент-специалистам?  
📸 Новые клиенты – тебя увидят блогеры и бренды, которые ищут услуги.  
📌 Легче продавать себя – нет нужды тратить время на поиск заказчиков и оплату рекламу — они сами тебя находят.  
💡 Совместные проекты – возможность участвовать в съемках, рекламных кампаниях и развивать личный бренд.  
🎯 Выход на новый уровень – в реестре собраны активные блогеры и бизнес, готовый работать с профессионалами.  

Почему это выгодно бизнесу?  
🎯 Экономия времени – больше не нужно искать блогеров и специалистов вручную, вся база под рукой.  
💡 Только проверенные контакты – актуальные расценки, аудитория и др данные в одной таблице .  
💰 Прозрачность цен – сразу видно, сколько стоят услуги, без переплат и посредников.  
📈 Эффективность и экономия времени  – больше не надо тратить время на поиски, бесконечные переписки, ожидание ответа, согласование, поиск команды — все можно выбрать даже по ключевым словам и все в одном месте, кто уже готов работать и ждет вас! 

Важное обновление: Реестр помогает ЗАКОННО обойти рекламные ограничения  
С 1 сентября вступает в силу закон, регулирующий рекламу в соцсетях. Многие бренды и блогеры столкнутся с трудностями в размещении рекламы.  

✅ В реестре есть ссылки не только на Instagram*, но и на другие соцсети: Telegram, VK, Дзен и т. д.  
✅ Бренды смогут находить блогеров и специалистов для нативных интеграций, обходя жесткие рекламные ограничения.  
✅ Блогеры и контент-специалисты не теряют рекламные возможности, а наоборот — становятся ещё ценнее для бизнеса.  

> В новом мире рекламы выигрывают те, кто адаптируется первым. Будь в числе первых – попади в реестр! 🚀  

(*Instagram принадлежит компании Meta, признанной экстремистской и запрещённой в России.)"""

    await callback.message.answer(text)


@router.callback_query(F.data == 'about_me')
async def about_me(callback: CallbackQuery):
    await callback.answer()
    text = """  

Привет! Я Мира — блогер, предприниматель и создатель реестра блогеров. Веду Instagram и Telegram о стиле, моде, отношениях и жизни в ритме большого города. Мне доверяют бренды, ко мне приходят за вдохновением, а я помогаю блогерам и бизнесу находить друг друга.  

📌 Что я делаю?  
— Развиваю реестр блогеров и контент-специалистов — удобную платформу для коллабораций и рекламы.  
— Веду закрытый контент-клуб, где делюсь инсайдами о продвижении и трендах
— Помогаю блогерам расти, анализировать ошибки, быть востребованными и зарабатывать.  

Почему я создала реестр блогеров?  
Я побывала по обе стороны — и как блогер, и как предприниматель.  

Когда у меня был свой онлайн магазин косметики и я работала с брендами, столкнулась с тем, что найти подходящего блогера — это хаос:   
❌ Бесконечные поиски через знакомых  
❌ Завышенные или скрытые расценки  
❌ Недостоверные охваты, отказ от показа статистики и непонятный результат рекламы  

Когда у меня был прокат одежды для фотосессий и мероприятий — я столкнулась с тем, чтобы собрать команду для того, чтобы отснять каталог, поиск нужной локации, модели и прочие нюансы 
❌ Все специалисты по контенту разбросаны по инстаграм 
❌ Поиск не всегда полный. Он показывает лишь часть страниц специалистов по своим алгоритмам и ты не можешь просмотреть все предложения 
❌ Долго ждать озвучивание цены и согласования 

А когда я начала развивать свой блог, поняла, что брендам сложно нас найти:  
❌ Либо обращаются только к уже известным блогерам  
❌ Либо предлагают бартер вместо денег  
❌ Либо просто не понимают, как работать с блогерами правильно  

Так появилась идея простого и удобного реестра, где:  
✔️ Бренды находят блогеров с понятными расценками  
✔️ Блогеры получают реальные предложения и монетизируют контент  
✔️ Контент-специалисты (фотографы, стилисты, модели, SMM) находят клиентов  

Это не просто таблица — это новый формат работы с блогерами и контентом. Если ты блогер, бренд или контент-специалист, добро пожаловать в наш мир! 🚀

"""
    await callback.message.answer(text,
                                  reply_markup=social_media_keyboard())


@router.callback_query(F.data == 'rules_and_conventions')
async def rules_and_conventions(callback: CallbackQuery):
    file_rules_and_conventions = FSInputFile('files/ПРАВИЛА_И_СОГЛАШЕНИЕ_О_ПОЛЬЗОВАНИИ_РЕЕСТРОМ_БЛОГЕРОВ_И_КОНТЕНТ.pdf',
                                             filename='terms_of_use.pdf')
    await callback.answer()
    await callback.message.answer_document(file_rules_and_conventions,
                                           caption='Правила и соглашения о пользовании реестром блогеров')


@router.callback_query(F.data == 'already_with_you')
async def already_with_you(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    sub_status = await get_sub_status(session, user_id)

    if sub_status:
        await callback.answer()
        await callback.message.answer(f'Что тебя интересует?',
                                      reply_markup=existing_user_menu_keyboard())
    else:
        await callback.answer()
        await callback.message.answer('Приобритите подписку')

@router.callback_query(F.data == 'subscription_and_conditions')
async def sub(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(f'Отправляем документ с условиями подписки')


def is_valid_name(name: str) -> bool:
    return re.fullmatch(r"[A-Za-zА-Яа-яЁё\s\-]{2,100}", name) is not None


def is_valid_city(name: str) -> bool:
    city_list = [city.strip() for city in name.split(",")]
    pattern = re.compile(r"^[A-Za-zА-Яа-яЁё\s\-]{2,100}$")
    return all(pattern.fullmatch(city) for city in city_list)

def is_valid_category(category: str) -> list[str]:
    parts = [cat.strip().capitalize() for cat in category.split(',')]

    return [p for p in parts if re.fullmatch(r"[A-Za-zА-Яа-яЁё\s\-]{2,100}", p)]


@router.callback_query(F.data == 'into_table')
async def into_table(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    sub_status = await get_sub_status(session, user_id)

    if sub_status:
        await callback.answer()
        await callback.message.answer('Вы уже есть в таблице')
    else:
        profession = await orm_get_profession(session, user_id)
        if not profession:
            await callback.answer()
            await callback.message.answer(f'Выбери свою профессию:',
                                      reply_markup=profession_selection_keyboard())
        else:
            await callback.answer()
            await callback.message.answer(f'Что делаем дальше?',
                                          reply_markup=action_selection_keyboard())


PROFESSION_CATEGORIES = {
    'blogger': 'blogger',
    'visagiste': 'specialist',
    'stylist': 'specialist',
    'photographer': 'specialist',
    'mobile_photographer': 'specialist',
    'videographer': 'specialist',
    'pr_manager': 'specialist',
    'smm': 'specialist',
    'model': 'specialist',
    'agency': 'specialist'
}


PROFESSION_TRANSLATION = {
    'blogger': 'Блогер',
    'visagiste': 'Визажист',
    'stylist': 'Стилист',
    'photographer': 'Фотограф',
    'mobile_photographer': 'Мобильный фотограф',
    'videographer': 'Видеограф',
    'pr_manager': 'PR-менеджер',
    'smm': 'SMM',
    'model': 'Модель',
    'agency': 'Агентство'
}


@router.callback_query(F.data.in_(PROFESSION_CATEGORIES.keys()))
async def save_profession_and_categories(callback: CallbackQuery, session: AsyncSession):
    profession = callback.data
    category = PROFESSION_CATEGORIES[profession]
    translate_profession = PROFESSION_TRANSLATION.get(profession, profession)

    user_id = callback.from_user.id
    await orm_add_profession_and_category(session, translate_profession, category, user_id)
    await callback.message.answer("✅Профессия сохранена")
    await callback.message.answer(f'Что делаем дальше?',
                                  reply_markup=action_selection_keyboard())
    await callback.answer()

@router.callback_query(F.data == 'payment')
async def handel_buy_confirm_conditions(callback: CallbackQuery):
    await callback.answer()
    try:

        await callback.message.answer(
            f"Перед началом заполнения анкеты, пожалуйста, ознакомьтесь с правилами и политикой конфиденциальности.\n"
            f"Нажимая кнопку ниже, вы подтверждаете согласие на обработку ваших данных.",
            reply_markup=confirm_conditions()
        )

        file_rules_and_conventions = FSInputFile(
            'files/Правила_и_соглашения.pdf',
            filename='rules_and_conventions.pdf')
        await callback.message.answer_document(file_rules_and_conventions,
                                               caption='Правила и соглашения')

    except Exception as e:
        logging.error(f"Ошибка при сохранении согласия: {e}")


@router.callback_query(F.data == 'accept_policy')
async def handle_buy_subscription(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    try:
        user_id = callback.from_user.id
        await orm_save_user_consent(session, user_id)

        can_use_trail = await orm_check_trial(session, user_id)

        if can_use_trail:
            payment_url, payment_id = create_initial_payment(user_id, 100, payment_type='trial')
            await callback.message.answer(
                f"🎉 Вам доступен пробный период на 30 дней за 1 ₽! Перейдите по ссылке для активации:\n\n🔗 {payment_url}",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            category = await orm_get_category(session, user_id)
            if category == 'blogger':
                subscription_price = 40000
            else:
                subscription_price = 30000

            payment_url, payment_id = create_initial_payment(user_id, subscription_price, payment_type='subscription')


            await callback.message.answer(
                f"Перейди по ссылке для оплаты подписки:\n\n🔗 {payment_url}",
                reply_markup=ReplyKeyboardRemove()
            )

    except Exception as e:
            logging.error(f"Ошибка при покупке подписки: {e}")
            await callback.answer("Произошла ошибка при обработке команды!")
            current_state = await state.get_state()
            if current_state is not None:
                await state.clear()


@router.callback_query(F.data == 'start_form')
async def start_form(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    user_id = callback.from_user.id

    has_sub = await get_sub_status(session, user_id)

    if not has_sub:
        await callback.message.answer("❌ У вас нет активной подписки. Пожалуйста, оплатите для доступа к анкете.")
        return

    try:
        await callback.message.answer("Теперь давайте начнём анкету. Введите ваше имя:")
        await state.set_state(AddCustomer.name)
    except Exception as e:
        logging.error(f"Ошибка при обработке имени: {e}")


@router.message(AddCustomer.name, F.text)
async def ask_lastname(message: Message, state: FSMContext):
    try:
        name = message.text.strip()
        if not is_valid_name(name):
            await message.answer("Имя должно содержать только буквы. Попробуйте снова:")
            return
        await state.update_data(name=name)
        await message.answer('Введите вашу фамилию:')
        await state.set_state(AddCustomer.lastname)
    except Exception as e:
        logging.error("Произошла ошибка при обработке имени. Попробуйте снова.")
        logging.error(f"[Ошибка в имени] {e}")


@router.message(AddCustomer.lastname, F.text)
async def ask_instagram(message: Message, state: FSMContext):
    try:
        lastname = message.text.strip()
        if not is_valid_name(lastname):
            await message.answer('Фамилия должна содержать только буквы. Попробуйте снова:')
            return
        await state.update_data(lastname=lastname)
        await message.answer('Ссылка на Instagram:')
        await state.set_state(AddCustomer.link_to_instagram)
    except Exception as e:
        logging.error("Произошла ошибка при обработке фамилии. Попробуйте снова.")
        logging.error(f"[Ошибка в фамилии] {e}")


@router.message(AddCustomer.link_to_instagram, F.text)
async def ask_city(message: Message, state: FSMContext):
    try:
        link_to_instagram = message.text.strip()
        instagram_pattern = r"^https://www\.instagram\.com/[A-Za-z0-9_\.]+/?$"

        if not re.match(instagram_pattern, link_to_instagram):
            await message.answer(f'Пожалуйста, введите корректную ссылку на Instagram, которая должна начинаться с '
                                 f'"https://www.instagram.com/" и содержать только буквы, цифры, подчеркивания и точки. Пример: '
                                 f'https://www.instagram.com/username')
            return
        await state.update_data(link_to_instagram=link_to_instagram)
        await message.answer('Введите город проживания:')
        await state.set_state(AddCustomer.city)
    except Exception as e:
        logging.error("Произошла ошибка при обработке ссылки на инстаграм. Попробуйте снова.")
        logging.error(f"[Ошибка в фамилии] {e}")


@router.message(AddCustomer.city, F.text)
async def ask_blog_category(message: Message, state: FSMContext):
    try:
        city = message.text.strip()
        if not is_valid_city(city):
            await message.answer(f'Пожалуйста, введитие корректное название города.')
            return
        await state.update_data(city=city)
        await message.answer('Категория вашего блога:')
        await state.set_state(AddCustomer.blog_category)
    except Exception as e:
        logging.error("Произошла ошибка при вводе города. Попробуйте снова.")
        logging.error(f"[Ошибка ввода города] {e}")


@router.message(AddCustomer.blog_category, F.text)
async def ask_subscribers(message: Message, state: FSMContext):
    try:
        raw_input = message.text.strip()
        blog_category = is_valid_category(raw_input)

        if not blog_category:
            await message.answer(
                "Введите хотя бы одну корректную категорию, разделяя их запятыми (пример: Мода, Путешествия):")
            return

        blog_category_str = ", ".join(blog_category)

        await state.update_data(blog_category=blog_category_str)
        await message.answer('Количество подписчиков:')
        await state.set_state(AddCustomer.number_of_subscribers)

    except Exception as e:
        logging.error("Произошла ошибка при вводе категорий. Попробуйте снова.")
        logging.error(f"[Ошибка blog_category] {e}")


@router.message(AddCustomer.number_of_subscribers, F.text)
async def ask_coverages(message: Message, state: FSMContext):
    try:
        text = message.text.strip()
        if not text.isdigit():
            await message.answer("Пожалуйста, введите количество подписчиков числом. Пример: 15000")
            return

        number_of_subscribers = int(text)

        if number_of_subscribers < 0:
            await message.answer("Количество подписчиков должно быть положительным числом. Попробуйте снова.")
            return

        await state.update_data(number_of_subscribers=number_of_subscribers)
        await message.answer('Средний охват:')
        await state.set_state(AddCustomer.coverages)
    except Exception as e:
        logging.error("Произошла ошибка при вводе количества подписчиков. Попробуйте снова.")
        logging.error(f"[Ошибка number_of_subscribers] {e}")


@router.message(AddCustomer.coverages, F.text)
async def ask_er(message: Message, state: FSMContext):
    try:
        text = message.text.strip()
        if not text.isdigit():
            await message.answer("Пожалуйста, введите значение охвата целым числом. Пример: 15000.")
            return

        coverages = int(text)

        if coverages < 0:
            await message.answer('Охват должен быть положительным числом. Попробуйте снова.')
            return

        await state.update_data(coverages=coverages)
        await message.answer('ER (в процентах): \n'
                             'Посчитать можно здесь'
                             'https://t.me/labelup_bot \n'
                             '*вы несете ответственность и можете быть удалены из таблицы за предоставление ложной информации о себе'
                             )
        await state.set_state(AddCustomer.er)
    except Exception as e:
        logging.error('Произошла ошибка при вводе охвата. Попробуйте снова.')
        logging.error(f'[Ошибка coverages] {e}')


@router.message(AddCustomer.er, F.text)
async def ask_telegram(message: Message, state: FSMContext):
    try:
        text = message.text.strip().replace(',', '.')
        try:
            er = float(text)
        except ValueError:
            await message.answer("Пожалуйста, введите значение ER числом. Пример: 15.5 или 100.")
            return

        if er < 0 or er > 100:
            await message.answer('ER должен быть в пределах от 0 до 100 процентов. Попробуйте снова.')
            return

        await state.update_data(er=er)
        await message.answer('Ссылка на Telegram (если есть):', reply_markup=skip('skip_telegram'))
        await state.set_state(AddCustomer.link_to_telegram)

    except Exception as e:
        logging.error("Произошла ошибка при вводе ER. Попробуйте снова.")
        logging.error(f"[Ошибка ER] {e}")

@router.message(AddCustomer.link_to_telegram, F.text)
async def ask_vk(message: Message, state: FSMContext):
    try:
        link_to_telegram = message.text.strip()
        telegram_pattern = r"^(https?:\/\/)?t\.me\/[A-Za-z0-9_]+$|^@[A-Za-z0-9_]+$"
        if not re.match(telegram_pattern, link_to_telegram):
            await message.answer("Пожалуйста, введите корректную ссылку на ваш Telegram. Пример: https://t.me/username.")
            return
        await state.update_data(link_to_telegram=link_to_telegram)
        await message.answer('Ссылка на VK (если есть):', reply_markup=skip('skip_vk'))
        await state.set_state(AddCustomer.link_to_vk)
    except Exception as e:
        logging.error("Произошла ошибка при вводе ссылки на Telegram. Попробуйте снова.")
        logging.error(f"[Ошибка link_to_telegram] {e}")


@router.message(AddCustomer.link_to_vk, F.text)
async def ask_youtube(message: Message, state: FSMContext):
    try:
        link_to_vk = message.text.strip()
        vk_pattern = r"^https://(m\.)?vk\.com/[A-Za-z0-9_\.]+/?$"

        if not re.match(vk_pattern, link_to_vk):
            await message.answer(f'Пожалуйста, введите корректную ссылку на VK, которая должна начинаться с '
                         f'"https://vk.com/" или "https://m.vk.com/" и содержать только буквы, цифры, подчеркивания и точки. Пример: '
                         f'https://vk.com/username')
            return

        await state.update_data(link_to_vk=link_to_vk)
        await message.answer('Ссылка на YouTube (если есть):', reply_markup=skip('skip_youtube'))
        await state.set_state(AddCustomer.link_to_youtube)
    except Exception as e:
        logging.error("Произошла ошибка при обработке ссылки на VK. Попробуйте снова.")
        logging.error(f"[Ошибка в ссылке на VK] {e}")


@router.message(AddCustomer.link_to_youtube, F.text)
async def ask_formats(message: Message, state: FSMContext):
    try:
        link_to_youtube = message.text.strip()
        youtube_pattern = r"^https://(www\.)?youtube\.com/[A-Za-z0-9_-]+/?$"

        if not re.match(youtube_pattern, link_to_youtube):
            await message.answer(f'Пожалуйста, введите корректную ссылку на канал YouTube, которая должна начинаться с '
                         f'"https://www.youtube.com/" и содержать только буквы, цифры, подчеркивания и дефисы. Пример: '
                         f'https://www.youtube.com/CHANNEL_NAME.')
            return

        await state.update_data(link_to_youtube=link_to_youtube)
        await message.answer('Какие рекламные форматы вы поддерживаете?')
        await state.set_state(AddCustomer.advertising_formats)
    except Exception as e:
        logging.error("Произошла ошибка при обработке ссылки на YouTube. Попробуйте снова.")
        logging.error(f"[Ошибка в ссылке на YouTube] {e}")


@router.message(AddCustomer.advertising_formats, F.text)
async def ask_cost_stories(message: Message, state: FSMContext):
    try:
        raw_input = message.text.strip()
        formats = is_valid_category(raw_input)

        if not formats:
            await message.answer(
                "Введите хотя бы один корректный формат рекламы, разделяя их запятыми (пример: Stories, Пост, Reels):")
            return

        advertising_formats =", ".join(formats)
        await state.update_data(advertising_formats=advertising_formats)
        await message.answer('Стоимость рекламы в Stories:')
        await state.set_state(AddCustomer.cost_of_advertising_in_stories)

    except Exception as e:
        logging.error("Произошла ошибка при обработке форматов рекламы. Попробуйте снова.")
        logging.error(f"[Ошибка advertising_formats] {e}")

@router.message(AddCustomer.cost_of_advertising_in_stories, F.text)
async def ask_cost_post(message: Message, state: FSMContext):
    try:
        raw_input = message.text.strip().replace(',', '.')
        cost = float(raw_input)

        if cost < 0:
            await message.answer("Стоимость не может быть отрицательной. Попробуйте снова.")
            return

        await state.update_data(cost_of_advertising_in_stories=cost)
        await message.answer('Стоимость рекламы в посте:')
        await state.set_state(AddCustomer.cost_of_advertising_in_a_post)
    except ValueError:
        await message.answer("Введите корректное число (например: 1500 или 2500.50)")
    except Exception as e:
        logging.error("Произошла ошибка. Попробуйте снова.")
        logging.error(f"[Ошибка cost_of_advertising_in_stories] {e}")


@router.message(AddCustomer.cost_of_advertising_in_a_post, F.text)
async def ask_cost_reels(message: Message, state: FSMContext):
    try:
        raw_input = message.text.strip().replace(',', '.')
        cost = float(raw_input)

        if cost < 0:
            await message.answer("Стоимость не может быть отрицательной. Попробуйте снова.")
            return

        await state.update_data(cost_of_advertising_in_a_post=cost)
        await message.answer('Стоимость рекламы в Reels:')
        await state.set_state(AddCustomer.cost_of_advertising_in_reels)
    except ValueError:
        await message.answer("Введите корректное число (например: 1500 или 2500.50)")
    except Exception as e:
        logging.error("Произошла ошибка. Попробуйте снова.")
        logging.error(f"[Ошибка cost_of_advertising_in_a_post] {e}")


@router.message(AddCustomer.cost_of_advertising_in_reels, F.text)
async def ask_phone(message: Message, state: FSMContext):
    try:
        raw_input = message.text.strip().replace(',', '.')
        cost = float(raw_input)

        if cost < 0:
            await message.answer("Стоимость не может быть отрицательной. Попробуйте снова.")
            return

        await state.update_data(cost_of_advertising_in_reels=cost)
        await message.answer('Ваш номер телефона:')
        await state.set_state(AddCustomer.phone_number)
    except ValueError:
        await message.answer("Введите корректное число (например: 1500 или 2500.50)")
    except Exception as e:
        logging.error("Произошла ошибка. Попробуйте снова.")
        print(f"[Ошибка cost_of_advertising_in_reels] {e}")

@router.message(AddCustomer.phone_number, F.text)
async def ask_email(message: Message, state: FSMContext):
    try:
        phone = message.text.strip()

        if not re.fullmatch(r"(\+7|8|7)\d{10}", phone):
            await message.answer("Введите корректный номер телефона (пример: +79001234567).")
            return

        await state.update_data(phone_number=phone)
        await message.answer('Ваш email:')
        await state.set_state(AddCustomer.email)
    except Exception as e:
        logging.error("Произошла ошибка. Попробуйте снова.")
        print(f"[Ошибка phone_number] {e}")

@router.message(AddCustomer.email, F.text)
async def save_and_finish(message: Message, state: FSMContext, session: AsyncSession):
    email = message.text.strip()
    user_id = message.from_user.id

    if not re.fullmatch(r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+", email):
        await message.answer("Пожалуйста, введите корректный email (пример: name@example.com).")
        return

    await state.update_data(email=email)
    data = await state.get_data()

    try:
        success = await orm_add_customer(session, data, user_id)
        if not success:
            await message.answer("Ошибка при добавлении пользователя")
            return

        customer_data = await orm_get_information(session, user_id)
        get_time = await orm_get_time_sub(session, user_id)
        user_sub = time_sub_day(get_time)

        if user_sub is None:
            user_sub = "Отсутствует"
        elif user_sub is False:
            user_sub = "Истекла"
        else:
            user_sub = f"Осталось {user_sub}"

        if customer_data:
            response_text = (
                f"Имя: {customer_data[0]}\n"
                f"Фамилия: {customer_data[1]}\n"
                f"Профессия: {customer_data[2]}\n"
                f"Instagram: {customer_data[3]}\n"
                f"Город: {customer_data[4]}\n"
                f"Категория блога: {customer_data[5]}\n"
                f"Подписчиков: {customer_data[6]}\n"
                f"Охват: {customer_data[7]}\n"
                f"ER: {customer_data[8]}\n"
                f"Telegram: {customer_data[9]}\n"
                f"VK: {customer_data[10]}\n"
                f"YouTube: {customer_data[11]}\n"
                f"Форматы рекламы: {customer_data[12]}\n"
                f"Stories: {customer_data[13]}\n"
                f"Пост: {customer_data[14]}\n"
                f"Reels: {customer_data[15]}\n"
                f"Телефон: {customer_data[16]}\n"
                f"Email: {customer_data[17]}\n"
                f"Подписка: {user_sub}\n"
                f"✅ Анкета успешно принята! Напоминаем про период 30 дней в стоимость 1 ₽. "
                f"Дальше будет автоматическое списание согласно условиям подписки. \n"
                f"Если вы хотите изменить данные, то это можно сделать в меню с помощью кнопки «уже с вами»."
            )
            await message.answer(response_text)
        else:
            await message.answer("Информация о вас не найдена")
    except Exception as e:
        logging.error(f'❌ Ошибка при сохранении: {str(e)}')
    finally:
        await state.clear()


@router.callback_query(F.data == 'access_table')
async def access_table(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(f'Давай смерим! Ты компания, бизнес, бренд?',
                                  reply_markup=company_check_keyboard())


@router.callback_query(F.data == 'yes')
async def info_table(callback: CallbackQuery, session: AsyncSession):

    user_id = callback.from_user.id
    await orm_add_user_id_access(session, user_id)

    await callback.answer()
    await callback.message.answer(f'Супер! Получи полную таблицу, где все в одном месте '
                                  f'для успешного развития своего бизнеса'
                                  f' модели, блогеры, смм, фотографы, видеографы и другие контент специалисты '
                                  f'Хочешь подписку или разовую покупку навсегда?',
                                  reply_markup=subscription_options_keyboard())


@router.callback_query(F.data == 'inf_for_me')
async def user_information(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    customer_data = await orm_get_information(session, user_id)
    get_time = await orm_get_time_sub(session, user_id)

    user_sub = time_sub_day(get_time)

    if user_sub is None:
        user_sub = "Отсутствует"
    elif user_sub is False:
        user_sub = "Истекла"
    else:
        user_sub = f"Осталось {user_sub}"

    if customer_data:
        response_text = (
            f"Имя: {customer_data[0]}\n"
            f"Фамилия: {customer_data[1]}\n"
            f"Профессия: {customer_data[2]}\n"
            f"Instagram: {customer_data[3]}\n"
            f"Город: {customer_data[4]}\n"
            f"Категория блога: {customer_data[5]}\n"
            f"Подписчиков: {customer_data[6]}\n"
            f"Охват: {customer_data[7]}\n"
            f"ER: {customer_data[8]}\n"
            f"Telegram: {customer_data[9]}\n" 
            f"VK: {customer_data[10]}\n" 
            f"YouTube: {customer_data[11]}\n"
            f"Форматы рекламы: {customer_data[12]}\n"
            f"Stories: {customer_data[13]}\n"
            f"Пост: {customer_data[14]}\n"
            f"Reels: {customer_data[15]}\n"
            f"Телефон: {customer_data[16]}\n"
            f"Email: {customer_data[17]}\n"
            f"Подписка: {user_sub}"
        )
    else:
        response_text = "❌ Информация о вас не найдена."
    await callback.answer()
    await callback.message.answer(response_text)


@router.callback_query(F.data == 'change_inf_about_yourself')
async def change_info(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(f'Выберите, что хотите изменить',
                                  reply_markup=to_change_information())


FIELD_TRANSLATIONS = {
    "name": "Имя",
    "lastname": "Фамилия",
    "profession": "Профессия",
    "link_to_instagram": "Ссылка на Instagram",
    "city": "Город",
    "blog_category": "Категория блога",
    "number_of_subscribers": "Количество подписчиков",
    "coverages": "Охваты",
    "er": "ER",
    "link_to_telegram": "Ссылка на Telegram",
    "link_to_vk": "Ссылка на VK",
    "link_to_youtube": "Ссылка на YouTube",
    "advertising_formats": "Форматы рекламы",
    "cost_of_advertising_in_stories": "Цена Stories",
    "cost_of_advertising_in_a_post": "Цена поста",
    "cost_of_advertising_in_reels": "Цена Reels",
    "phone_number": "Телефон",
    "email": "Email",
}


@router.callback_query(lambda c: c.data in FIELD_TRANSLATIONS)
async def change_info(callback: CallbackQuery, state: FSMContext):
    field = callback.data
    readable_field = FIELD_TRANSLATIONS.get(field, field)
    await state.update_data(current_field=field)
    await callback.message.answer(f"Введите новое значение для поля «{readable_field}»:")
    await state.set_state(EditCustomer.waiting_for_value)


@router.message(EditCustomer.waiting_for_value, F.text)
async def update_lastname(message: Message, state: FSMContext, session: AsyncSession):
    new_value = message.text
    user_id = message.from_user.id
    data = await state.get_data()
    field_to_update = data.get('current_field')
    readable_field = FIELD_TRANSLATIONS.get(field_to_update, field_to_update)

    try:
        await orm_update_customer_field(session, user_id, field_to_update, new_value)
        await message.answer(f"✅ Поле '{readable_field}' успешно обновлено!")
    except Exception as e:
        logging.error(f"❌ Ошибка при обновлении: {str(e)}")
    finally:
        await state.clear()


@router.callback_query(F.data == 'contacts_for_communication')
async def change_contacts(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(f'Выберите контакт для связи, который хотите изменить',
                                  reply_markup=to_change_contacts())


@router.callback_query(F.data == 'sub_3000')
async def questions(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(f'Точно хочешь подписку на 1 месяц? Выгодней купить сразу '
                                  f'и иметь всегда под рукой обновляющуюся таблицу. '
                                  f'В дальнейшем с ростом таблицы будет расти и стоимость покупки 🤔',
                                  reply_markup=confirm_subscription_keyboard())


@router.callback_query(F.data == 'sure')
async def handle_buy_monthly_table(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        subscription_price = 70000
        payment_url, payment_id = create_initial_payment(user_id, subscription_price, payment_type = "table")

        await callback.message.answer(
            f"Перейди по ссылке для оплаты подписки:\n\n🔗 {payment_url}",
            reply_markup=ReplyKeyboardRemove()
        )

    except Exception as e:
        logging.error(f"Ошибка при покупке подписки: {e}")
        await callback.answer("Произошла ошибка при обработке команды!")


@router.callback_query(F.data == 'sub_10_000')
async def handle_buy_lifetime_table(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        subscription_price = 230000
        payment_url, payment_id = create_initial_payment(user_id, subscription_price, payment_type = "table_lifetime")

        await callback.message.answer(
            f"Перейди по ссылке для оплаты подписки:\n\n🔗 {payment_url}",
            reply_markup=ReplyKeyboardRemove()
        )

    except Exception as e:
        logging.error(f"Ошибка при покупке подписки: {e}")
        await callback.answer("Произошла ошибка при обработке команды!")


@router.callback_query(F.data == 'check_table')
async def send_exel_table(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id

    access = await get_type_access(session, user_id)
    if not access:
        await callback.answer()
        await callback.message.answer('❌ У вас нет доступа к таблице. Пожалуйста, оформите подписку.')
        return

    if access == 'subscription':
        sub_active = await get_sub_end(session, user_id)
        if not sub_active:
            await callback.answer()
            await callback.message.answer("❌ Ваша подписка истекла. Пожалуйста, продлите её.")
            return

    await callback.answer("⏳ Экспорт данных...")

    customers = await orm_get_information_for_exel(session)
    columns = [
        'Имя',  # Имя
        'Фамилия',  # Фамилия
        'Профессия',  # Профессия
        'Instagram',  # Instagram
        'Город',  # Город
        'Категория блога',  # Категория блога
        'Количество подписчиков',  # number_of_subscribers
        'Охваты',  # coverages
        'ER (вовлеченность)',  # er
        'Ссылка на Telegram',  # link_to_telegram
        'Ссылка на VK',  # link_to_vk
        'Ссылка на YouTube',  # link_to_youtube
        'Форматы рекламы',  # advertising_formats
        'Стоимость рекламы в Stories',  # cost_of_advertising_in_stories
        'Стоимость рекламы в Посте',  # cost_of_advertising_in_a_post
        'Стоимость рекламы в Reels',  # cost_of_advertising_in_reels
        'Номер телефона',  # phone_number
        'Email'  # email
    ]

    df = pd.DataFrame(customers, columns=columns)
    df.to_excel('files/all_customers.xlsx')

    file = FSInputFile('files/all_customers.xlsx')
    await callback.message.answer_document(file, caption='📊 Файл с данными готов!')


@router.callback_query(F.data =='skip_telegram')
async def skip_telegram(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        await state.update_data(link_to_telegram = None)

        await callback.message.edit_reply_markup()

        await callback.message.answer('Ссылка на VK (если есть):', reply_markup=skip('skip_vk'))
        await state.set_state(AddCustomer.link_to_vk)
    except Exception as e:
        logging.error("Произошла ошибка при пропуске Telegram. Попробуйте снова.")
        logging.error(f"[Ошибка при skip Telegram] {e}")


@router.callback_query(F.data =='skip_vk')
async def skip_vk(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        await state.update_data(link_to_vk=None)

        await callback.message.edit_reply_markup()

        await callback.message.answer('Ссылка на YouTube (если есть):', reply_markup=skip('skip_youtube'))
        await state.set_state(AddCustomer.link_to_youtube)
    except Exception as e:
        logging.error("Произошла ошибка при пропуске Telegram. Попробуйте снова.")
        logging.error(f"[Ошибка при skip VK] {e}")


@router.callback_query(F.data == 'skip_youtube')
async def skip_youtube(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        await state.update_data(link_to_youtube=None)

        await callback.message.edit_reply_markup()

        await callback.message.answer('Какие рекламные форматы вы поддерживаете?')
        await state.set_state(AddCustomer.advertising_formats)
    except Exception as e:
        logging.error("Произошла ошибка при пропуске Telegram. Попробуйте снова.")
        logging.error(f"[Ошибка при skip YouTube] {e}")


@router.callback_query(F.data == 'unsubscribe_customer')
async def process_unsubscribe_customer(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id

    success = await orm_unsubscribe_customer(session, user_id)
    if success:
        await callback.answer("Подписка отменена")
    else:
        await callback.answer("Ошибка при отмене подписки")
    await callback.answer()


@router.callback_query(F.data == 'unsubscribe_access')
async def process_unsubscribe_access(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id

    success = await orm_unsubscribe_access(session, user_id)
    if success:
        await callback.answer("Подписка отменена")
    else:
        await callback.answer("Ошибка при отмене подписки")
    await callback.answer()
