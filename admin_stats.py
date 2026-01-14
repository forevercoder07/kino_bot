from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import datetime

from database.db import db
from utils.keyboards import (
    get_admin_main_menu, get_cancel_keyboard,
    get_channel_management_keyboard, get_pagination_keyboard
)
from utils.helpers import format_number, broadcast_message, parse_permissions
from handlers.admin import AdminStates, is_admin_check, has_permission_check

router = Router()


# ==================== USER STATISTICS ====================

@router.message(F.text == "👥 User Statistic")
async def user_statistics(message: Message):
    """Foydalanuvchilar statistikasi"""
    if not await has_permission_check(message.from_user.id, "User Statistic"):
        await message.answer("❌ Sizda bu amalni bajarish uchun ruxsat yo'q!")
        return
    
    # Ma'lumotlarni yig'ish
    total_users = await db.get_users_count()
    daily_users = await db.get_users_by_period(1)
    weekly_users = await db.get_users_by_period(7)
    monthly_users = await db.get_users_by_period(30)
    daily_views = await db.get_daily_views()
    
    text = "👥 <b>Foydalanuvchilar statistikasi</b>\n\n"
    text += f"📊 Jami foydalanuvchilar: <b>{format_number(total_users)}</b>\n\n"
    text += f"📅 Bugun qo'shildi: <b>{format_number(daily_users)}</b>\n"
    text += f"📅 1 hafta ichida: <b>{format_number(weekly_users)}</b>\n"
    text += f"📅 1 oy ichida: <b>{format_number(monthly_users)}</b>\n\n"
    text += f"👁 Bugun ko'rildi: <b>{format_number(daily_views)}</b> ta kino\n"
    
    await message.answer(text, reply_markup=get_admin_main_menu())


# ==================== FILM STATISTICS ====================

@router.message(F.text == "🎞 Film Statistic")
async def film_statistics(message: Message, state: FSMContext):
    """Kinolar statistikasi - sahifalangan"""
    if not await has_permission_check(message.from_user.id, "Film Statistic"):
        await message.answer("❌ Sizda bu amalni bajarish uchun ruxsat yo'q!")
        return
    
    # Birinchi sahifani ko'rsatish
    await show_films_page(message, 0)


async def show_films_page(message: Message, page: int = 0):
    """Kinolar ro'yxatini sahifalab ko'rsatish"""
    films, total = await db.get_films_paginated(offset=page * 30, limit=30)
    
    if not films:
        await message.answer(
            "📊 Hozircha kinolar yo'q!",
            reply_markup=get_admin_main_menu()
        )
        return
    
    total_pages = (total + 29) // 30  # Round up
    
    text = f"🎞 <b>Kinolar ro'yxati</b>\n"
    text += f"📄 Sahifa {page + 1}/{total_pages}\n"
    text += f"📊 Jami: {total} ta kino\n\n"
    
    for idx, film in enumerate(films, start=page * 30 + 1):
        text += f"{idx}. <b>{film['name']}</b>\n"
        text += f"   🔢 Kod: <code>{film['code']}</code>\n\n"
    
    # Pagination keyboard
    keyboard = get_pagination_keyboard(page, total_pages, "films")
    
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("films_page_"))
async def films_page_callback(callback: Message):
    """Sahifa o'zgarganda"""
    page = int(callback.data.split("_")[-1])
    
    films, total = await db.get_films_paginated(offset=page * 30, limit=30)
    total_pages = (total + 29) // 30
    
    text = f"🎞 <b>Kinolar ro'yxati</b>\n"
    text += f"📄 Sahifa {page + 1}/{total_pages}\n"
    text += f"📊 Jami: {total} ta kino\n\n"
    
    for idx, film in enumerate(films, start=page * 30 + 1):
        text += f"{idx}. <b>{film['name']}</b>\n"
        text += f"   🔢 Kod: <code>{film['code']}</code>\n\n"
    
    keyboard = get_pagination_keyboard(page, total_pages, "films")
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


# ==================== CHANNELS MANAGEMENT ====================

@router.message(F.text == "📢 Channels")
async def channels_menu(message: Message, state: FSMContext):
    """Kanallar boshqaruvi"""
    if not await has_permission_check(message.from_user.id, "Channels"):
        await message.answer("❌ Sizda bu amalni bajarish uchun ruxsat yo'q!")
        return
    
    await state.clear()
    await message.answer(
        "📢 <b>Kanallar boshqaruvi</b>\n\n"
        "Quyidagi amallardan birini tanlang:",
        reply_markup=get_channel_management_keyboard()
    )


@router.message(F.text == "➕ Kanal qo'shish")
async def add_channel_start(message: Message, state: FSMContext):
    """Kanal qo'shishni boshlash"""
    if not await has_permission_check(message.from_user.id, "Channels"):
        await message.answer("❌ Sizda bu amalni bajarish uchun ruxsat yo'q!")
        return
    
    await state.set_state(AdminStates.waiting_channel_add)
    await message.answer(
        "➕ <b>Yangi kanal qo'shish</b>\n\n"
        "Kanal ID yoki username kiriting:\n\n"
        "Misol:\n"
        "• <code>-1001234567890</code> (ID)\n"
        "• <code>@mychannel</code> (Username)\n\n"
        "<i>Bot kanal adminlari orasida bo'lishi kerak!</i>",
        reply_markup=get_cancel_keyboard()
    )


@router.message(AdminStates.waiting_channel_add)
async def add_channel_process(message: Message, state: FSMContext):
    """Kanalni qo'shish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await channels_menu(message, state)
        return
    
    channel_input = message.text.strip()
    
    try:
        # Username yoki ID?
        if channel_input.startswith('@'):
            # Username orqali kanal ma'lumotlarini olish
            chat = await message.bot.get_chat(channel_input)
            channel_id = chat.id
            channel_username = channel_input[1:]  # @ ni olib tashlash
            channel_title = chat.title
        else:
            # ID orqali
            channel_id = int(channel_input)
            chat = await message.bot.get_chat(channel_id)
            channel_username = chat.username
            channel_title = chat.title
        
        # Bazaga qo'shish
        await db.add_channel(channel_id, channel_username, channel_title)
        
        await state.clear()
        await message.answer(
            f"✅ <b>Kanal qo'shildi!</b>\n\n"
            f"📢 {channel_title}\n"
            f"🆔 ID: <code>{channel_id}</code>\n"
            f"👤 Username: @{channel_username}" if channel_username else "",
            reply_markup=get_channel_management_keyboard()
        )
    except Exception as e:
        await message.answer(
            f"❌ Xatolik: {e}\n\n"
            "Bot kanal adminlari orasida ekanligini tekshiring!"
        )


@router.message(F.text == "🗑 Kanal o'chirish")
async def delete_channel_start(message: Message, state: FSMContext):
    """Kanalni o'chirishni boshlash"""
    if not await has_permission_check(message.from_user.id, "Channels"):
        await message.answer("❌ Sizda bu amalni bajarish uchun ruxsat yo'q!")
        return
    
    channels = await db.get_all_channels()
    
    if not channels:
        await message.answer(
            "📢 Hozircha kanallar ro'yxati bo'sh!",
            reply_markup=get_channel_management_keyboard()
        )
        return
    
    await state.set_state(AdminStates.waiting_channel_delete)
    
    text = "🗑 <b>Kanalni o'chirish</b>\n\n"
    text += "Quyidagi kanallardan birini tanlang:\n\n"
    
    for idx, channel in enumerate(channels, 1):
        text += f"{idx}. <b>{channel['channel_title'] or 'Kanal'}</b>\n"
        text += f"   🆔 ID: <code>{channel['channel_id']}</code>\n\n"
    
    text += "\nKanal ID sini kiriting:"
    
    await message.answer(text, reply_markup=get_cancel_keyboard())


@router.message(AdminStates.waiting_channel_delete)
async def delete_channel_process(message: Message, state: FSMContext):
    """Kanalni o'chirish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await channels_menu(message, state)
        return
    
    try:
        channel_id = int(message.text.strip())
        
        # Kanalni tekshirish
        channels = await db.get_all_channels()
        channel_exists = any(ch['channel_id'] == channel_id for ch in channels)
        
        if not channel_exists:
            await message.answer("❌ Bunday kanal topilmadi!")
            return
        
        await db.delete_channel(channel_id)
        
        await state.clear()
        await message.answer(
            f"✅ Kanal o'chirildi!\n\n"
            f"🆔 ID: <code>{channel_id}</code>",
            reply_markup=get_channel_management_keyboard()
        )
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")


@router.message(F.text == "📋 Kanallar ro'yxati")
async def channels_list(message: Message):
    """Kanallar ro'yxati"""
    if not await has_permission_check(message.from_user.id, "Channels"):
        await message.answer("❌ Sizda bu amalni bajarish uchun ruxsat yo'q!")
        return
    
    channels = await db.get_all_channels()
    
    if not channels:
        await message.answer(
            "📢 Hozircha kanallar ro'yxati bo'sh!",
            reply_markup=get_channel_management_keyboard()
        )
        return
    
    text = "📋 <b>Majburiy kanallar ro'yxati:</b>\n\n"
    
    for idx, channel in enumerate(channels, 1):
        text += f"{idx}. <b>{channel['channel_title'] or 'Kanal'}</b>\n"
        text += f"   🆔 ID: <code>{channel['channel_id']}</code>\n"
        if channel['channel_username']:
            text += f"   👤 @{channel['channel_username']}\n"
        text += f"   📅 {channel['added_date'].strftime('%d.%m.%Y')}\n\n"
    
    await message.answer(text, reply_markup=get_channel_management_keyboard())


@router.message(F.text == "🔙 Orqaga")
async def back_to_admin(message: Message, state: FSMContext):
    """Admin menyusiga qaytish"""
    await state.clear()
    
    from handlers.admin import admin_panel
    await admin_panel(message, state)


# ==================== ALL WRITE (BROADCAST) ====================

@router.message(F.text == "✍️ All write")
async def broadcast_start(message: Message, state: FSMContext):
    """Barcha foydalanuvchilarga xabar yuborish"""
    if not await has_permission_check(message.from_user.id, "All write"):
        await message.answer("❌ Sizda bu amalni bajarish uchun ruxsat yo'q!")
        return
    
    await state.set_state(AdminStates.waiting_broadcast_content)
    await message.answer(
        "✍️ <b>Xabar yuborish</b>\n\n"
        "Barcha foydalanuvchilarga yuborish uchun xabar, rasm yoki video yuboring:",
        reply_markup=get_cancel_keyboard()
    )


@router.message(AdminStates.waiting_broadcast_content)
async def broadcast_process(message: Message, state: FSMContext):
    """Xabarni barcha foydalanuvchilarga yuborish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        from handlers.admin import admin_panel
        await admin_panel(message, state)
        return
    
    # Yuborilmoqda xabari
    status_msg = await message.answer("📤 Xabar yuborilmoqda...")
    
    # Broadcast
    success, failed = await broadcast_message(message.bot, message)
    
    await state.clear()
    
    await status_msg.edit_text(
        f"✅ <b>Xabar yuborildi!</b>\n\n"
        f"✅ Muvaffaqiyatli: {format_number(success)}\n"
        f"❌ Xatolik: {format_number(failed)}"
    )
    
    await message.answer(
        "Admin menyusiga qaytdingiz:",
        reply_markup=get_admin_main_menu()
    )
