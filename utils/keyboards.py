from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# =============== USER KEYBOARDS ===============

def get_user_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🎬 Kino qidirish"),
                KeyboardButton(text="📊 Kinolar statistikasi")
            ],
            [KeyboardButton(text="📞 Adminga murojat")]
        ],
        resize_keyboard=True
    )


def get_back_to_menu():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🏠 Asosiy menyu")]],
        resize_keyboard=True
    )

def get_admin_main_menu(permissions=None):
    keyboard = []

    if permissions is None or 'all' in permissions or '7' in permissions:
        keyboard = [
            [KeyboardButton(text="➕ Add film"), KeyboardButton(text="📹 Add parts")],
            [KeyboardButton(text="🗑 Delete film"), KeyboardButton(text="📢 Channels")],
            [KeyboardButton(text="👥 User Statistic"), KeyboardButton(text="🎞 Film Statistic")],
            [KeyboardButton(text="✍️ All write"), KeyboardButton(text="👨‍💼 Add admin")],
            [KeyboardButton(text="📋 Admin statistic"), KeyboardButton(text="🏠 Main menu")]
        ]
    else:
        row = []
        rows = []

        def add_btn(condition, text):
            if condition:
                row.append(KeyboardButton(text=text))
                if len(row) == 2:
                    rows.append(row.copy())
                    row.clear()

        add_btn('Add film' in permissions or '1' in permissions, "➕ Add film")
        add_btn('Add parts' in permissions or '2' in permissions, "📹 Add parts")
        add_btn('Delete film' in permissions or '3' in permissions, "🗑 Delete film")
        add_btn('Channels' in permissions or '4' in permissions, "📢 Channels")
        add_btn('User Statistic' in permissions or '5' in permissions, "👥 User Statistic")
        add_btn('Film Statistic' in permissions or '6' in permissions, "🎞 Film Statistic")
        add_btn('All write' in permissions or '8' in permissions, "✍️ All write")
        add_btn('Add admin' in permissions or '9' in permissions, "👨‍💼 Add admin")
        add_btn('Admin statistic' in permissions or '10' in permissions, "📋 Admin statistic")

        if row:
            rows.append(row)

        rows.append([KeyboardButton(text="🏠 Main menu")])
        keyboard = rows

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True
    )

def get_film_parts_keyboard(parts_count: int, film_code: str):
    keyboard = []

    row = []
    for i in range(1, parts_count + 1):
        row.append(
            InlineKeyboardButton(
                text=f"📹 {i}-qism",
                callback_data=f"part_{film_code}_{i}"
            )
        )
        if len(row) == 3:
            keyboard.append(row.copy())
            row.clear()

    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_channels_keyboard(channels, invite_links: dict = None):
    """
    Kanallar keyboard.
    invite_links = {channel_id: 'https://t.me/+xxxx'} — yopiq kanallar uchun
    """
    keyboard = []
    invite_links = invite_links or {}

    for idx, channel in enumerate(channels, 1):
        name = channel['channel_title'] or channel['channel_username'] or f"Kanal {idx}"

        if channel['channel_username']:
            # Ochiq kanal — username orqali
            url = f"https://t.me/{channel['channel_username']}"
        elif channel['channel_id'] in invite_links:
            # Yopiq kanal — settings da saqlangan invite link
            url = invite_links[channel['channel_id']]
        else:
            # Yopiq kanal — standart format (ba'zida ishlamaydi)
            url = f"https://t.me/c/{str(channel['channel_id'])[4:]}/1"

        keyboard.append([
            InlineKeyboardButton(text=f"{'🔒' if not channel['channel_username'] else '📢'} {idx}. {name}", url=url)
        ])

    keyboard.append([
        InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subscription")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_pagination_keyboard(current_page: int, total_pages: int, prefix: str = "films"):
    buttons = []

    if current_page > 0:
        buttons.append(
            InlineKeyboardButton(
                text="◀️ Oldingi",
                callback_data=f"{prefix}_page_{current_page - 1}"
            )
        )

    buttons.append(
        InlineKeyboardButton(
            text=f"{current_page + 1}/{total_pages}",
            callback_data="current_page"
        )
    )

    if current_page < total_pages - 1:
        buttons.append(
            InlineKeyboardButton(
                text="Keyingi ▶️",
                callback_data=f"{prefix}_page_{current_page + 1}"
            )
        )

    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def get_channel_management_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➕ Kanal qo'shish"),
                KeyboardButton(text="🗑 Kanal o'chirish")
            ],
            [
                KeyboardButton(text="📋 Kanallar ro'yxati"),
                KeyboardButton(text="🔙 Orqaga")
            ]
        ],
        resize_keyboard=True
    )
