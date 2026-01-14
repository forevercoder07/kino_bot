from aiogram import Bot
from aiogram.types import ChatMemberStatus
from database.db import db


async def check_user_subscription(bot: Bot, user_id: int) -> tuple[bool, list]:
    """
    Foydalanuvchining barcha majburiy kanallarga obuna ekanligini tekshirish
    Returns: (is_subscribed, not_subscribed_channels)
    """
    channels = await db.get_all_channels()
    
    if not channels:
        return True, []
    
    not_subscribed = []
    
    for channel in channels:
        try:
            member = await bot.get_chat_member(channel['channel_id'], user_id)
            if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
                not_subscribed.append(channel)
        except Exception as e:
            # Agar kanal yopiq bo'lsa yoki bot kanalda bo'lmasa, xatolikni e'tiborsiz qoldirish
            print(f"Kanal tekshirishda xatolik: {channel['channel_id']} - {e}")
            continue
    
    return len(not_subscribed) == 0, not_subscribed


def format_film_info(film, parts_count=0):
    """Kino ma'lumotlarini formatlash"""
    info = f"🎬 <b>{film['name']}</b>\n\n"
    info += f"📝 <b>Izoh:</b> {film['description']}\n"
    info += f"🔢 <b>Kod:</b> <code>{film['code']}</code>\n"
    if parts_count > 0:
        info += f"📹 <b>Qismlar soni:</b> {parts_count}\n"
    return info


def format_number(num):
    """Raqamlarni chiroyli formatlash"""
    return "{:,}".format(num).replace(",", " ")


async def broadcast_message(bot: Bot, message_to_send, from_chat_id=None):
    """
    Barcha foydalanuvchilarga xabar yuborish
    message_to_send - forward qilinadigan message object
    """
    users = await db.get_all_users()
    success = 0
    failed = 0
    
    for user in users:
        try:
            await message_to_send.copy_to(user['user_id'])
            success += 1
        except Exception as e:
            failed += 1
            print(f"Foydalanuvchiga yuborishda xatolik {user['user_id']}: {e}")
    
    return success, failed


def get_permission_name(perm_code):
    """Ruxsat kodini nomga aylantirish"""
    permissions_map = {
        '1': 'Add film',
        '2': 'Add parts',
        '3': 'Delete film',
        '4': 'Channels',
        '5': 'User Statistic',
        '6': 'Film Statistic',
        '7': 'Barcha ruxsatlar',
        '8': 'All write',
        '9': 'Add admin',
        '10': 'Admin statistic'
    }
    return permissions_map.get(perm_code, perm_code)


def parse_permissions(permissions_text):
    """
    Ruxsatlar matnini parse qilish
    Misol: "1,2,3" -> ['Add film', 'Add parts', 'Delete film']
    """
    if not permissions_text:
        return []
    
    codes = [code.strip() for code in permissions_text.split(',')]
    
    if '7' in codes:
        return ['all']
    
    permissions = []
    for code in codes:
        perm_name = get_permission_name(code)
        if perm_name != code:  # Agar valid kod bo'lsa
            permissions.append(perm_name)
    
    return permissions
