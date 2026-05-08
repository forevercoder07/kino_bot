from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import config
from database.db import db
from utils.keyboards import get_admin_main_menu, get_cancel_keyboard, get_user_main_menu
from utils.helpers import format_number

router = Router()


class AdminStates(StatesGroup):
    # Add film states
    waiting_film_code = State()
    waiting_film_name = State()
    waiting_film_year = State()
    waiting_film_genre = State()
    waiting_film_country = State()
    waiting_film_thumbnail = State()
    
    # Add parts states
    waiting_parts_code = State()
    waiting_parts_videos = State()
    
    # Delete film states
    waiting_delete_code = State()
    
    # Broadcast states
    waiting_broadcast_content = State()
    
    # Add admin states
    waiting_admin_id = State()
    waiting_admin_permissions = State()
    
    # Channel management states
    waiting_channel_add = State()
    waiting_channel_delete = State()
    
    # Change admin contact
    waiting_new_contact_link = State()


async def is_admin_check(user_id: int) -> bool:
    return await db.is_admin(user_id)


async def has_permission_check(user_id: int, permission: str) -> bool:
    return await db.has_permission(user_id, permission)


async def send_film_announcement(bot, film: dict):
    """
    Yangi kino haqida e'lonni announcement_channel ga yuborish.
    film — dict yoki asyncpg Record (code, name, year, genre, country, thumbnail_file_id)
    """
    channel = await db.get_setting('announcement_channel')
    if not channel or not channel.strip():
        return  # Kanal sozlanmagan — jim o'tib ketamiz

    bot_username = await db.get_setting('bot_username')
    channel_username = await db.get_setting('announcement_channel_username')

    # Shablon
    caption = (
        f"🎬 <b>{film['name']}</b>\n\n"
        f"🔢 Kod: <b>{film['code']}</b>\n\n"
        f"🇺🇿 O'zbek tilida\n"
        f"📆 Yil: <b>{film['year'] or '—'}</b>\n"
        f"🎞 Janr: <b>{film['genre'] or '—'}</b>\n"
        f"🌍 Davlat: <b>{film['country'] or '—'}</b>\n\n"
        f"🌐 My channel: {('@' + channel_username) if channel_username else channel}\n\n"
        f"🤖 My Bot: {('@' + bot_username) if bot_username else '—'}\n\n"
        f"Bizni kuzatishda davom eting, \nBiz esa yurishda davom etamiz."
    )

    # DOWNLOAD inline tugmasi — botga o'tib kodni yuboradi
    download_button = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="DOWNLOAD 🎬",
            url=f"https://t.me/{bot_username}?start={film['code']}" if bot_username else f"https://t.me/{bot_username}"
        )
    ]])

    try:
        if film['thumbnail_file_id']:
            await bot.send_photo(
                chat_id=channel,
                photo=film['thumbnail_file_id'],
                caption=caption,
                reply_markup=download_button
            )
        else:
            await bot.send_message(
                chat_id=channel,
                text=caption,
                reply_markup=download_button
            )
    except Exception as e:
        print(f"Kanalga yuborishda xatolik: {e}")


@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    """Admin panel"""
    await state.clear()
    
    if not await is_admin_check(message.from_user.id):
        return
    
    if message.from_user.id == config.OWNER_ID:
        permissions = None
    else:
        admin_data = await db.get_admin(message.from_user.id)
        permissions = admin_data['permissions'] if admin_data else []
    
    await message.answer(
        f"👨‍💼 <b>Admin Panel</b>\n\n"
        f"Xush kelibsiz, {message.from_user.full_name}!",
        reply_markup=get_admin_main_menu(permissions)
    )


# ==================== ADD FILM ====================

@router.message(F.text == "➕ Add film")
async def add_film_start(message: Message, state: FSMContext):
    if not await has_permission_check(message.from_user.id, "Add film"):
        await message.answer("❌ Sizda bu amalni bajarish uchun ruxsat yo'q!")
        return
    
    await state.set_state(AdminStates.waiting_film_code)
    await message.answer(
        "📝 <b>Yangi kino qo'shish</b>\n\n"
        "1️⃣ Kino kodini kiriting:\n\n"
        "Misol: <code>101</code>\n\n"
        "Bu kod orqali foydalanuvchilar kinoni topadi.",
        reply_markup=get_cancel_keyboard()
    )


@router.message(AdminStates.waiting_film_code)
async def add_film_code(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await admin_panel(message, state)
        return
    
    film_code = message.text.strip()
    
    existing_film = await db.get_film(film_code)
    if existing_film:
        await message.answer(
            "❌ Bu kod allaqachon mavjud!\n\n"
            "Iltimos, boshqa kod kiriting:"
        )
        return
    
    await state.update_data(film_code=film_code)
    await state.set_state(AdminStates.waiting_film_name)
    
    await message.answer(
        "2️⃣ Kino nomini kiriting:\n\n"
        "Misol: <code>Terminator 2</code>"
    )


@router.message(AdminStates.waiting_film_name)
async def add_film_name(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await admin_panel(message, state)
        return
    
    await state.update_data(film_name=message.text.strip())
    await state.set_state(AdminStates.waiting_film_year)
    
    await message.answer(
        "3️⃣ Kino yilini kiriting:\n\n"
        "Misol: <code>2024</code>"
    )


@router.message(AdminStates.waiting_film_year)
async def add_film_year(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await admin_panel(message, state)
        return
    
    await state.update_data(film_year=message.text.strip())
    await state.set_state(AdminStates.waiting_film_genre)
    
    await message.answer(
        "4️⃣ Kino janrini kiriting:\n\n"
        "Misol: <code>Jangari, Ilmiy-fantastika</code>"
    )


@router.message(AdminStates.waiting_film_genre)
async def add_film_genre(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await admin_panel(message, state)
        return
    
    await state.update_data(film_genre=message.text.strip())
    await state.set_state(AdminStates.waiting_film_country)
    
    await message.answer(
        "5️⃣ Kino davlatini kiriting:\n\n"
        "Misol: <code>AQSh</code>"
    )


@router.message(AdminStates.waiting_film_country)
async def add_film_country(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await admin_panel(message, state)
        return
    
    await state.update_data(film_country=message.text.strip())
    await state.set_state(AdminStates.waiting_film_thumbnail)
    
    await message.answer(
        "6️⃣ Kino uchun rasm (thumbnail) yuboring:\n\n"
        "📸 Rasmni yuboring yoki bekor qilish tugmasini bosing."
    )


@router.message(AdminStates.waiting_film_thumbnail, F.photo)
async def add_film_thumbnail(message: Message, state: FSMContext):
    """Kino rasmini qabul qilish, saqlash va kanalga e'lon yuborish"""
    data = await state.get_data()
    photo_file_id = message.photo[-1].file_id
    
    try:
        await db.add_film(
            code=data['film_code'],
            name=data['film_name'],
            year=data['film_year'],
            genre=data['film_genre'],
            country=data['film_country'],
            thumbnail_file_id=photo_file_id
        )
        
        await state.clear()
        
        # Admin uchun tasdiqlash xabari
        await message.answer(
            f"✅ <b>Kino muvaffaqiyatli qo'shildi!</b>\n\n"
            f"🔢 Kod: <code>{data['film_code']}</code>\n"
            f"🎬 Nom: {data['film_name']}\n"
            f"📆 Yil: {data['film_year']}\n"
            f"🎞 Janr: {data['film_genre']}\n"
            f"🌍 Davlat: {data['film_country']}\n\n"
            f"📢 Kanal e'loni yuborilmoqda...\n\n"
            f"📹 Endi bu kinoga qismlar qo'shishingiz mumkin (Add parts).",
            reply_markup=get_admin_main_menu()
        )

        # Kanalga e'lon yuborish
        film = await db.get_film(data['film_code'])
        await send_film_announcement(message.bot, film)

    except Exception as e:
        await message.answer(
            f"❌ Xatolik yuz berdi: {e}\n\n"
            "Iltimos, qaytadan urinib ko'ring.",
            reply_markup=get_admin_main_menu()
        )
        await state.clear()


# ==================== ADD PARTS ====================

@router.message(F.text == "📹 Add parts")
async def add_parts_start(message: Message, state: FSMContext):
    if not await has_permission_check(message.from_user.id, "Add parts"):
        await message.answer("❌ Sizda bu amalni bajarish uchun ruxsat yo'q!")
        return
    
    await state.set_state(AdminStates.waiting_parts_code)
    await message.answer(
        "📹 <b>Kino qismlarini qo'shish</b>\n\n"
        "Kino kodini kiriting:\n\n"
        "Misol: <code>101</code>",
        reply_markup=get_cancel_keyboard()
    )


@router.message(AdminStates.waiting_parts_code)
async def add_parts_code(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await admin_panel(message, state)
        return
    
    film_code = message.text.strip()
    film = await db.get_film(film_code)
    if not film:
        await message.answer(
            "❌ Bu kod bo'yicha kino topilmadi!\n\n"
            "Avval kinoni qo'shing (Add film)."
        )
        return
    
    parts_count = await db.get_parts_count(film_code)
    
    await state.update_data(film_code=film_code, current_part=parts_count + 1)
    await state.set_state(AdminStates.waiting_parts_videos)
    
    await message.answer(
        f"🎬 <b>{film['name']}</b>\n\n"
        f"📹 Hozirgi qismlar: {parts_count}\n\n"
        f"Yangi qism videosini yuboring (keyingisi {parts_count + 1}-qism bo'ladi).\n\n"
        f"Barcha qismlarni yuborib bo'lgach, 'Bekor qilish' tugmasini bosing."
    )


@router.message(AdminStates.waiting_parts_videos, F.video)
async def add_parts_video(message: Message, state: FSMContext):
    data = await state.get_data()
    film_code = data['film_code']
    part_number = data['current_part']
    
    video_file_id = message.video.file_id
    
    try:
        await db.add_film_part(film_code, part_number, video_file_id)
        
        await message.answer(
            f"✅ {part_number}-qism qo'shildi!\n\n"
            f"Keyingi qismni yuboring yoki 'Bekor qilish' tugmasini bosing."
        )
        await state.update_data(current_part=part_number + 1)
        
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")


@router.message(AdminStates.waiting_parts_videos, F.text == "❌ Bekor qilish")
async def finish_adding_parts(message: Message, state: FSMContext):
    data = await state.get_data()
    film_code = data['film_code']
    total_parts = await db.get_parts_count(film_code)
    
    await state.clear()
    await message.answer(
        f"✅ <b>Qismlar qo'shish yakunlandi!</b>\n\n"
        f"🔢 Kod: <code>{film_code}</code>\n"
        f"📹 Jami qismlar: {total_parts}",
        reply_markup=get_admin_main_menu()
    )


# ==================== DELETE FILM ====================

@router.message(F.text == "🗑 Delete film")
async def delete_film_start(message: Message, state: FSMContext):
    if not await has_permission_check(message.from_user.id, "Delete film"):
        await message.answer("❌ Sizda bu amalni bajarish uchun ruxsat yo'q!")
        return
    
    await state.set_state(AdminStates.waiting_delete_code)
    await message.answer(
        "🗑 <b>Kino yoki qismni o'chirish</b>\n\n"
        "Variantlar:\n"
        "1️⃣ Butun kinoni o'chirish: <code>101</code>\n"
        "2️⃣ Bitta qismni o'chirish: <code>101-5</code> (101-kod, 5-qism)\n\n"
        "Kodni kiriting:",
        reply_markup=get_cancel_keyboard()
    )


@router.message(AdminStates.waiting_delete_code)
async def delete_film_process(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await admin_panel(message, state)
        return
    
    code_input = message.text.strip()
    
    if '-' in code_input:
        try:
            film_code, part_num = code_input.split('-')
            part_number = int(part_num)
            
            film = await db.get_film(film_code)
            if not film:
                await message.answer("❌ Kino topilmadi!")
                return
            
            part = await db.get_film_part(film_code, part_number)
            if not part:
                await message.answer("❌ Bu qism topilmadi!")
                return
            
            await db.delete_film_part(film_code, part_number)
            
            await state.clear()
            await message.answer(
                f"✅ <b>Qism o'chirildi!</b>\n\n"
                f"🎬 Kino: {film['name']}\n"
                f"📹 O'chirilgan qism: {part_number}",
                reply_markup=get_admin_main_menu()
            )
        except Exception as e:
            await message.answer(f"❌ Xatolik: {e}")
    else:
        film_code = code_input
        film = await db.get_film(film_code)
        
        if not film:
            await message.answer("❌ Kino topilmadi!")
            return
        
        await db.delete_film(film_code)
        
        await state.clear()
        await message.answer(
            f"✅ <b>Kino to'liq o'chirildi!</b>\n\n"
            f"🎬 {film['name']}\n"
            f"🔢 Kod: {film_code}",
            reply_markup=get_admin_main_menu()
        )


@router.message(F.text == "🏠 Main menu")
async def admin_main_menu(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        await message.answer("Asosiy menyu:", reply_markup=get_user_main_menu())
        return
    
    await state.clear()
    await admin_panel(message, state)
