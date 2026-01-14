from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
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
    waiting_film_description = State()
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
    """Admin tekshiruvi"""
    return await db.is_admin(user_id)


async def has_permission_check(user_id: int, permission: str) -> bool:
    """Ruxsat tekshiruvi"""
    return await db.has_permission(user_id, permission)


@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    """Admin panel"""
    await state.clear()
    
    if not await is_admin_check(message.from_user.id):
        return
    
    # Ruxsatlarni olish
    if message.from_user.id == config.OWNER_ID:
        permissions = None  # Owner barcha ruxsatlarga ega
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
    """Kino qo'shishni boshlash"""
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
    """Kino kodini qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await admin_panel(message, state)
        return
    
    film_code = message.text.strip()
    
    # Kod mavjudligini tekshirish
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
    """Kino nomini qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await admin_panel(message, state)
        return
    
    await state.update_data(film_name=message.text)
    await state.set_state(AdminStates.waiting_film_description)
    
    await message.answer(
        "3️⃣ Kino haqida izoh kiriting:\n\n"
        "Misol: <code>Terminator franshizasining ikkinchi qismi. Jahon kinosi tarixidagi eng yaxshi aktsion filmi.</code>"
    )


@router.message(AdminStates.waiting_film_description)
async def add_film_description(message: Message, state: FSMContext):
    """Kino izohi qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await admin_panel(message, state)
        return
    
    await state.update_data(film_description=message.text)
    await state.set_state(AdminStates.waiting_film_thumbnail)
    
    await message.answer(
        "4️⃣ Kino uchun rasm (thumbnail) yuboring:\n\n"
        "📸 Rasmni yuboring yoki bekor qilish tugmasini bosing."
    )


@router.message(AdminStates.waiting_film_thumbnail, F.photo)
async def add_film_thumbnail(message: Message, state: FSMContext):
    """Kino rasmini qabul qilish va saqlash"""
    data = await state.get_data()
    
    # Eng katta rasmni olish
    photo_file_id = message.photo[-1].file_id
    
    # Bazaga saqlash
    try:
        await db.add_film(
            code=data['film_code'],
            name=data['film_name'],
            description=data['film_description'],
            thumbnail_file_id=photo_file_id
        )
        
        await state.clear()
        
        await message.answer(
            f"✅ <b>Kino muvaffaqiyatli qo'shildi!</b>\n\n"
            f"🔢 Kod: <code>{data['film_code']}</code>\n"
            f"🎬 Nom: {data['film_name']}\n"
            f"📝 Izoh: {data['film_description']}\n\n"
            f"📹 Endi bu kinoga qismlar qo'shishingiz mumkin (Add parts).",
            reply_markup=get_admin_main_menu()
        )
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
    """Kino qismlarini qo'shishni boshlash"""
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
    """Kino kodini qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await admin_panel(message, state)
        return
    
    film_code = message.text.strip()
    
    # Kinoni tekshirish
    film = await db.get_film(film_code)
    if not film:
        await message.answer(
            "❌ Bu kod bo'yicha kino topilmadi!\n\n"
            "Avval kinoni qo'shing (Add film)."
        )
        return
    
    # Hozirgi qismlar sonini olish
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
    """Video qismni qabul qilish"""
    data = await state.get_data()
    film_code = data['film_code']
    part_number = data['current_part']
    
    video_file_id = message.video.file_id
    
    try:
        # Qismni saqlash
        await db.add_film_part(film_code, part_number, video_file_id)
        
        await message.answer(
            f"✅ {part_number}-qism qo'shildi!\n\n"
            f"Keyingi qismni yuboring yoki 'Bekor qilish' tugmasini bosing."
        )
        
        # Keyingi qism uchun tayyorlanish
        await state.update_data(current_part=part_number + 1)
        
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")


@router.message(AdminStates.waiting_parts_videos, F.text == "❌ Bekor qilish")
async def finish_adding_parts(message: Message, state: FSMContext):
    """Qismlar qo'shishni yakunlash"""
    data = await state.get_data()
    film_code = data['film_code']
    added_parts = data['current_part'] - await db.get_parts_count(film_code) - 1
    
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
    """Kino o'chirishni boshlash"""
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
    """Kino o'chirish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await admin_panel(message, state)
        return
    
    code_input = message.text.strip()
    
    # Butun kino yoki qism?
    if '-' in code_input:
        # Qismni o'chirish
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
        # Butun kinoni o'chirish
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
    """Admin asosiy menyusiga qaytish"""
    if not await is_admin_check(message.from_user.id):
        await message.answer(
            "Asosiy menyu:",
            reply_markup=get_user_main_menu()
        )
        return
    
    await state.clear()
    await admin_panel(message, state)
