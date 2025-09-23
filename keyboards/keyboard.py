from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.dialects.mssql.information_schema import columns


def create_inline_keyboard(*, buttons: list[tuple[str, str]] , columns: int):
    builder = InlineKeyboardBuilder()

    for text, callback in buttons:
        builder.button(text=text, callback_data=callback)

    builder.adjust(columns)
    return builder.as_markup()


def help_keyboard():
    builder = InlineKeyboardBuilder()

    buttons = [
        ('Написать поддержке', 'https://t.me/reestrblogerov')
    ]

    for text, url in buttons:
        builder.button(text=text, url=url)
    return builder.as_markup()

def social_media_keyboard():
    builder = InlineKeyboardBuilder()
    buttons = [
        ('Мой телеграм канал', 'https://t.me/miramediche'),
        ('Мой инстаграм', 'https://www.instagram.com/mira_mediche')
    ]

    for text, url in buttons:
        builder.button(text=text, url=url)
    builder.adjust(1)
    return builder.as_markup()


def skip(callback: str = 'skip'):
    buttons = [
        ('Пропустить', callback)
    ]

    return create_inline_keyboard(buttons=buttons, columns=1)


def main_menu_keyboard():
    buttons = [
        ('Я здесь впервые', 'first_time'),
        ('Уже с вами', 'already_with_you'),
        ('Хочу попасть в таблицу', 'into_table'),
        ('Хочу получить доступ к таблице', 'access_table'),
    ]

    return create_inline_keyboard(buttons=buttons, columns=1)


def first_time_menu_keyboard():
    buttons = [
        ('О проекте', 'about_project'),
        ('Обо мне', 'about_me'),
        ('Правила и соглашения', 'rules_and_conventions'),
    ]

    return create_inline_keyboard(buttons=buttons, columns=2)


def existing_user_menu_keyboard():
    buttons = [
        ('Узнать информацию о себе', 'inf_for_me'),
        ('Изменить информацию о себе', 'change_inf_about_yourself'),
        # ('Продвижение в таблице и реклама', 'promtoion_table')
    ]

    return create_inline_keyboard(buttons=buttons, columns=1)


def profession_selection_keyboard():
    buttons = [
        ('Блогер', 'blogger'),
        ('Визажист', 'visagiste'),
        ('Стилист', 'stylist'),
        ('Фотограф', 'photographer'),
        ('Мобильный фотограф', 'mobile_photographer'),
        ('Видеограф', 'videographer'),
        ('PR-менеджер','pr_manager'),
        ('SMM', 'smm'),
        ('Модель', 'model'),
        ('Агенство', 'agency')
    ]

    return create_inline_keyboard(buttons=buttons, columns=2)


def confirm_conditions():
    buttons = [
        ('Я согласен с правилами, соглашением и передачей данных', 'accept_policy')
    ]
    return create_inline_keyboard(buttons=buttons, columns=1)

def action_selection_keyboard():
    buttons = [
        ('Подписка и условия', 'subscription_and_conditions'),
        ('Оплата', 'payment')
    ]

    return create_inline_keyboard(buttons=buttons, columns=1)


def company_check_keyboard():
    buttons = [
        ('да', 'yes'),
        ('нет', 'into_table')
    ]

    return create_inline_keyboard(buttons=buttons, columns=2)


def subscription_options_keyboard():
    buttons = [
        ('Подписка на 1 месяц (700₽)', 'sub_3000'),
        ('Разовая покупка навсегда (2300₽)', 'sub_10_000'),
        ('Получить таблицу (доступно только после покупки подписки или разового доступа)', 'check_table')
    ]

    return create_inline_keyboard(buttons=buttons, columns=1)


def get_table_to_view():
    buttons = [
        ('Посмотреть таблицу', 'check_table')
    ]

    return create_inline_keyboard(buttons=buttons, columns=1)

def confirm_subscription_keyboard():
    buttons = [
        ('Да, уверен', 'sure'),
        ('Нет, хочу разовую', 'sub_10_000')
    ]

    return create_inline_keyboard(buttons=buttons, columns=2)

def to_change_information():
    buttons = [
        ('Имя', 'name'),
        ('Фамилия', 'lastname'),
        ('Ссылка в Instagram', 'link_to_instagram'),
        ('Город', 'city'),
        ('Категория блога', 'blog_category'),
        ('Количество подписчииков', 'number_of_subscribers'),
        ('Охваты', 'coverages'),
        ('Процент вовлеченности', 'er'),
        ('Ссылка на телеграм', 'link_to_telegram'),
        ('Ссылка на VK', 'link_to_vk'),
        ('Ссылка на Ютуб ', 'link_to_youtube'),
        ('Форматы рекламы', 'advertising_formats'),
        ('Стоимость рекламы в сторис', 'cost_of_advertising_in_stories'),
        ('Стоимость рекламы в посте','cost_of_advertising_in_a_post'),
        ('Стоимость рекламы в рилс', 'cost_of_advertising_in_reels'),
        ('Контакты для связи', 'contacts_for_communication'),
    ]

    return create_inline_keyboard(buttons=buttons, columns=1)

def to_change_contacts():
    buttons = [
        ('Номер телефона', 'phone_number'),
        ('Почта', 'email')
    ]

    return create_inline_keyboard(buttons=buttons, columns=1)

def keyboard_start_questionnaire():
    buttons =[
        ('Заполнить анкету 📋', 'start_form')
    ]
    return create_inline_keyboard(buttons=buttons, columns=1)


def unsubscribe_keyboard_customer():
    buttons = [
        ('Отменить подписку ❌', 'unsubscribe_customer')
    ]

    return create_inline_keyboard(buttons=buttons, columns=1)


def unsubscribe_keyboard_access():
    buttons = [
        ('Отменить подписку ❌', 'unsubscribe_access')
    ]

    return create_inline_keyboard(buttons=buttons, columns=1)