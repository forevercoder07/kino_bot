from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# =============== USER KEYBOARDS ===============

def get_user_main_menu():
    """Foydalanuvchi asosiy menyusi"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("🎬 Kino qidirish"),
        KeyboardButton("📊 Kinolar statistikasi")
    )
    keyboard.add(KeyboardButton("📞 Adminga murojat"))
    return keyboard


def get_back_to_menu():
    """Asosiy menyuga qaytish"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🏠 Asosiy menyu"))
    return keyboard


# =============== ADMIN KEYBOARDS ===============

def get_admin_main_menu(permissions=None):
    """Admin asosiy menyusi"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Agar ruxsatlar ko'rsatilmagan bo'lsa (owner), barcha tugmalarni ko'rsat
    if permissions is None or 'all' in permissions or '7' in permissions:
        keyboard.add(
            KeyboardButton("➕ Add film"),
            KeyboardButton("📹 Add parts")
        )
        keyboard.add(
            KeyboardButton("🗑 Delete film"),
            KeyboardButton("📢 Channels")
        )
        keyboard.add(
            KeyboardButton("👥 User Statistic"),
            KeyboardButton("🎞 Film Statistic")
        )
        keyboard.add(
            KeyboardButton("✍️ All write"),
            KeyboardButton("👨‍💼 Add admin")
        )
        keyboard.add(
            KeyboardButton("📋 Admin statistic"),
            KeyboardButton("🏠 Main menu")
        )
    else:
        # Faqat ruxsat berilgan tugmalarni ko'rsat
        buttons = []
        if 'Add film' in permissions or '1' in permissions:
            buttons.append(KeyboardButton("➕ Add film"))
        if 'Add parts' in permissions or '2' in permissions:
            buttons.append(KeyboardButton("📹 Add parts"))
        if 'Delete film' in permissions or '3' in permissions:
            buttons.append(KeyboardButton("🗑 Delete film"))
        if 'Channels' in permissions or '4' in permissions:
            buttons.append(KeyboardButton("📢 Channels"))
        if 'User Statistic' in permissions or '5' in permissions:
            buttons.append(KeyboardButton("👥 User Statistic"))
        if 'Film Statistic' in permissions or '6' in permissions:
            buttons.append(KeyboardButton("🎞 Film Statistic"))
        if 'All write' in permissions or '8' in permissions:
            buttons.append(KeyboardButton("✍️ All write"))
        if 'Add admin' in permissions or '9' in permissions:
            buttons.append(KeyboardButton("👨‍💼 Add admin"))
        if 'Admin statistic' in permissions or '10' in permissions:
            buttons.append(KeyboardButton("📋 Admin statistic"))
        
        # Tugmalarni 2 tadan qo'shish
        for i in range(0, len(buttons), 2):
            if i + 1 < len(buttons):
                keyboard.add(buttons[i], buttons[i + 1])
            else:
                keyboard.add(buttons[i])
        
        keyboard.add(KeyboardButton("🏠 Main menu"))
    
    return keyboard


def get_cancel_keyboard():
    """Bekor qilish tugmasi"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("❌ Bekor qilish"))
    return keyboard


# =============== INLINE KEYBOARDS ===============

def get_film_parts_keyboard(parts_count: int, film_code: str):
    """Kino qismlari uchun inline keyboard"""
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = []
    
    for i in range(1, parts_count + 1):
        buttons.append(InlineKeyboardButton(
            text=f"📹 {i}-qism",
            callback_data=f"part_{film_code}_{i}"
        ))
    
    # 3 tadan tugma qo'yish
    for i in range(0, len(buttons), 3):
        keyboard.row(*buttons[i:i+3])
    
    return keyboard


def get_channels_keyboard(channels):
    """Kanallar ro'yxati uchun inline keyboard"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    for idx, channel in enumerate(channels, 1):
        channel_name = channel['channel_title'] or channel['channel_username'] or f"Kanal {idx}"
        channel_url = f"https://t.me/{channel['channel_username']}" if channel['channel_username'] else None
        
        if channel_url:
            keyboard.add(InlineKeyboardButton(
                text=f"{idx}. {channel_name}",
                url=channel_url
            ))
        else:
            # Agar username bo'lmasa, channel_id orqali link yaratish
            keyboard.add(InlineKeyboardButton(
                text=f"{idx}. {channel_name}",
                url=f"https://t.me/c/{str(channel['channel_id'])[4:]}/1"
            ))
    
    keyboard.add(InlineKeyboardButton(
        text="✅ Tekshirish",
        callback_data="check_subscription"
    ))
    
    return keyboard


def get_pagination_keyboard(current_page: int, total_pages: int, prefix: str = "films"):
    """Sahifalash uchun keyboard"""
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = []
    
    if current_page > 0:
        buttons.append(InlineKeyboardButton("◀️ Oldingi", callback_data=f"{prefix}_page_{current_page - 1}"))
    
    buttons.append(InlineKeyboardButton(f"{current_page + 1}/{total_pages}", callback_data="current_page"))
    
    if current_page < total_pages - 1:
        buttons.append(InlineKeyboardButton("Keyingi ▶️", callback_data=f"{prefix}_page_{current_page + 1}"))
    
    keyboard.row(*buttons)
    return keyboard


def get_channel_management_keyboard():
    """Kanal boshqaruvi uchun keyboard"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("➕ Kanal qo'shish"),
        KeyboardButton("🗑 Kanal o'chirish")
    )
    keyboard.add(
        KeyboardButton("📋 Kanallar ro'yxati"),
        KeyboardButton("🔙 Orqaga")
    )
    return keyboard
