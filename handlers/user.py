from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import db
from utils.keyboards import (
    get_user_main_menu, get_film_parts_keyboard, 
    get_channels_keyboard, get_back_to_menu
)
from utils.helpers import check_user_subscription, format_film_info, format_number

router = Router()


class UserStates(StatesGroup):
    waiting_for_film_code = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Start komandasi - foydalanuvchini ro'yxatga olish"""
    await state.clear()
    
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # Foydalanuvchini bazaga qo'shish
    await db.add_user(user_id, username, full_name)
    
    # Kanalga obuna tekshirish
    channels = await db.get_all_channels()
    
    if channels:
        is_subscribed, not_subscribed = await check_user_subscription(message.bot, user_id)
        
        if not is_subscribed:
            keyboard = get_channels_keyboard(not_subscribed)
            await message.answer(
                "👋 Assalomu aleykum!\n\n"
                "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
                reply_markup=keyboard
            )
            return
    
    # Agar obuna bo'lgan bo'lsa yoki kanallar bo'lmasa
    await message.answer(
        f"👋 Assalomu aleykum, {full_name}!\n\n"
        "🎬 Kino botiga xush kelibsiz!\n\n"
        "Botdan foydalanish uchun quyidagi tugmalardan birini tanlang:",
        reply_markup=get_user_main_menu()
    )


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery):
    """Obuna tekshirish tugmasi bosilganda"""
    user_id = callback.from_user.id
    
    is_subscribed, not_subscribed = await check_user_subscription(callback.bot, user_id)
    
    if is_subscribed:
        await callback.message.delete()
        await callback.message.answer(
            f"✅ Obuna tasdiqlandi!\n\n"
            f"👋 {callback.from_user.full_name}, botga xush kelibsiz!\n\n"
            "Quyidagi tugmalardan birini tanlang:",
            reply_markup=get_user_main_menu()
        )
    else:
        keyboard = get_channels_keyboard(not_subscribed)
        await callback.answer(
            "❌ Siz hali barcha kanallarga obuna bo'lmadingiz!",
            show_alert=True
        )
        await callback.message.edit_reply_markup(reply_markup=keyboard)


@router.message(F.text == "🎬 Kino qidirish")
async def search_film(message: Message, state: FSMContext):
    """Kino qidirish tugmasi"""
    # Obuna tekshirish
    is_subscribed, not_subscribed = await check_user_subscription(message.bot, message.from_user.id)
    if not is_subscribed:
        keyboard = get_channels_keyboard(not_subscribed)
        await message.answer(
            "❌ Botdan foydalanish uchun kanallarga obuna bo'ling:",
            reply_markup=keyboard
        )
        return
    
    await state.set_state(UserStates.waiting_for_film_code)
    await message.answer(
        "🔍 Kino kodini kiriting:\n\n"
        "Misol: <code>101</code>",
        reply_markup=get_back_to_menu(),
        parse_mode="HTML"
    )


@router.message(UserStates.waiting_for_film_code)
async def process_film_code(message: Message, state: FSMContext):
    """Kino kodini qabul qilish"""
    if message.text == "🏠 Asosiy menyu":
        await state.clear()
        await message.answer(
            "Asosiy menyuga qaytdingiz:",
            reply_markup=get_user_main_menu()
        )
        return
    
    film_code = message.text.strip()
    
    # Kinoni topish
    film = await db.get_film(film_code)
    
    if not film:
        await message.answer(
            "❌ Bu kod bo'yicha kino topilmadi!\n\n"
            "Iltimos, to'g'ri kodni kiriting:"
        )
        return
    
    # Kino qismlarini olish
    parts = await db.get_film_parts(film_code)
    
    if not parts:
        await message.answer(
            "❌ Bu kino uchun qismlar yuklanmagan!\n\n"
            "Iltimos, boshqa kino kodini kiriting:"
        )
        return
    
    await state.clear()
    
    # Agar bitta qism bo'lsa, darhol yuborish
    if len(parts) == 1:
        part = parts[0]
        
        # Thumbnail bilan birga video yuborish
        if film['thumbnail_file_id']:
            await message.answer_photo(
                photo=film['thumbnail_file_id'],
                caption=format_film_info(film, len(parts))
            )
        
        await message.answer_video(
            video=part['video_file_id'],
            caption=f"🎬 <b>{film['name']}</b>\n📹 Video",
            reply_markup=get_user_main_menu()
        )
        
        # Ko'rilganini qayd qilish
        await db.add_film_view(film_code, message.from_user.id)
    
    else:
        # Ko'p qismli bo'lsa, qismlar menyusini ko'rsatish
        keyboard = get_film_parts_keyboard(len(parts), film_code)
        
        if film['thumbnail_file_id']:
            await message.answer_photo(
                photo=film['thumbnail_file_id'],
                caption=format_film_info(film, len(parts)) + "\n\n👇 Qismni tanlang:",
                reply_markup=keyboard
            )
        else:
            await message.answer(
                format_film_info(film, len(parts)) + "\n\n👇 Qismni tanlang:",
                reply_markup=keyboard
            )


@router.callback_query(F.data.startswith("part_"))
async def send_film_part(callback: CallbackQuery):
    """Tanlangan qismni yuborish"""
    # part_CODE_NUMBER
    _, film_code, part_num = callback.data.split("_")
    part_number = int(part_num)
    
    # Qismni topish
    part = await db.get_film_part(film_code, part_number)
    film = await db.get_film(film_code)
    
    if not part or not film:
        await callback.answer("❌ Qism topilmadi!", show_alert=True)
        return
    
    # Videoni yuborish
    await callback.message.answer_video(
        video=part['video_file_id'],
        caption=f"🎬 <b>{film['name']}</b>\n📹 {part_number}-qism",
        reply_markup=get_user_main_menu()
    )
    
    await callback.answer(f"✅ {part_number}-qism yuborildi!")
    
    # Ko'rilganini qayd qilish
    await db.add_film_view(film_code, callback.from_user.id)
    
    # Qolgan qismlar uchun keyboard qayta yuborish
    parts_count = await db.get_parts_count(film_code)
    if parts_count > 1:
        keyboard = get_film_parts_keyboard(parts_count, film_code)
        await callback.message.edit_reply_markup(reply_markup=keyboard)


@router.message(F.text == "📊 Kinolar statistikasi")
async def films_statistics(message: Message):
    """Kinolar statistikasi - top 20"""
    # Obuna tekshirish
    is_subscribed, not_subscribed = await check_user_subscription(message.bot, message.from_user.id)
    if not is_subscribed:
        keyboard = get_channels_keyboard(not_subscribed)
        await message.answer(
            "❌ Botdan foydalanish uchun kanallarga obuna bo'ling:",
            reply_markup=keyboard
        )
        return
    
    top_films = await db.get_top_films(20)
    
    if not top_films:
        await message.answer(
            "📊 Hozircha statistika mavjud emas!",
            reply_markup=get_user_main_menu()
        )
        return
    
    text = "📊 <b>TOP 20 eng ko'p ko'rilgan kinolar:</b>\n\n"
    
    for idx, film in enumerate(top_films, 1):
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
        text += f"{medal} <b>{film['name']}</b>\n"
        text += f"   👁 Ko'rildi: {format_number(film['views_count'])} marta\n"
    
    await message.answer(text, reply_markup=get_user_main_menu())


@router.message(F.text == "📞 Adminga murojat")
async def contact_admin(message: Message):
    """Adminga murojat"""
    # Obuna tekshirish
    is_subscribed, not_subscribed = await check_user_subscription(message.bot, message.from_user.id)
    if not is_subscribed:
        keyboard = get_channels_keyboard(not_subscribed)
        await message.answer(
            "❌ Botdan foydalanish uchun kanallarga obuna bo'ling:",
            reply_markup=keyboard
        )
        return
    
    # Admin contact link ni olish
    admin_link = await db.get_setting('admin_contact_link')
    
    if not admin_link:
        admin_link = "https://t.me/forever_projects"
    
    await message.answer(
        f"📞 <b>Adminga murojat uchun quyidagi havolaga bosing:</b>\n\n"
        f"👉 {admin_link}",
        reply_markup=get_user_main_menu(),
        disable_web_page_preview=True
    )


@router.message(F.text == "🏠 Asosiy menyu")
async def main_menu(message: Message, state: FSMContext):
    """Asosiy menyuga qaytish"""
    await state.clear()
    await message.answer(
        "Asosiy menyu:",
        reply_markup=get_user_main_menu()
    )
