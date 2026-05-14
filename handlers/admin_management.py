from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import config
from database.db import db
from utils.keyboards import get_admin_main_menu, get_cancel_keyboard
from utils.helpers import parse_permissions, get_permission_name
from handlers.admin import AdminStates, is_admin_check, has_permission_check

router = Router()


# ==================== ADD ADMIN ====================

@router.message(F.text == "👨‍💼 Add admin")
async def add_admin_start(message: Message, state: FSMContext):
    if message.from_user.id != config.OWNER_ID:
        await message.answer("❌ Faqat bot egasi admin qo'sha oladi!")
        return
    
    await state.set_state(AdminStates.waiting_admin_id)
    await message.answer(
        "👨‍💼 <b>Yangi admin qo'shish</b>\n\n"
        "1️⃣ Yangi admin ID sini kiriting:\n\n"
        "Misol: <code>123456789</code>\n\n"
        "<i>ID ni @userinfobot dan olishingiz mumkin</i>",
        reply_markup=get_cancel_keyboard()
    )


@router.message(AdminStates.waiting_admin_id)
async def add_admin_id(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        from handlers.admin import admin_panel
        await admin_panel(message, state)
        return
    
    try:
        admin_id = int(message.text.strip())
        
        if admin_id == config.OWNER_ID:
            await message.answer("❌ Bu sizning ID ingiz! Siz allaqachon ownersiz.")
            return
        
        existing_admin = await db.get_admin(admin_id)
        if existing_admin:
            await message.answer("❌ Bu foydalanuvchi allaqachon admin!")
            return
        
        await state.update_data(admin_id=admin_id)
        await state.set_state(AdminStates.waiting_admin_permissions)
        
        permissions_text = (
            "2️⃣ Admin ruxsatlarini kiriting:\n\n"
            "<b>Ruxsatlar ro'yxati:</b>\n"
            "1 - Add film\n"
            "2 - Add parts\n"
            "3 - Delete film\n"
            "4 - Channels\n"
            "5 - User Statistic\n"
            "6 - Film Statistic\n"
            "7 - <b>Barcha ruxsatlar</b>\n"
            "8 - All write\n"
            "9 - Add admin\n"
            "10 - Admin statistic\n\n"
            "Misol:\n"
            "• <code>1,2,3</code> - faqat kino qo'shish, qism qo'shish va o'chirish\n"
            "• <code>7</code> - barcha ruxsatlar\n\n"
            "Ruxsatlarni vergul bilan ajratib kiriting:"
        )
        
        await message.answer(permissions_text, reply_markup=get_cancel_keyboard())
        
    except ValueError:
        await message.answer("❌ Noto'g'ri ID! Faqat raqam kiriting.")


@router.message(AdminStates.waiting_admin_permissions)
async def add_admin_permissions(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        from handlers.admin import admin_panel
        await admin_panel(message, state)
        return
    
    data = await state.get_data()
    admin_id = data['admin_id']
    
    permissions = parse_permissions(message.text)
    
    if not permissions:
        await message.answer(
            "❌ Noto'g'ri format!\n\n"
            "Iltimos, to'g'ri formatda kiriting (masalan: 1,2,3)"
        )
        return
    
    try:
        await db.add_admin(admin_id, permissions, message.from_user.id)
        await state.clear()
        
        perms_text = ", ".join(permissions) if 'all' not in permissions else "Barcha ruxsatlar"
        
        await message.answer(
            f"✅ <b>Admin qo'shildi!</b>\n\n"
            f"👤 ID: <code>{admin_id}</code>\n"
            f"🔑 Ruxsatlar: {perms_text}\n\n"
            f"Yangi admin /admin komandasi orqali admin paneliga kirishi mumkin.",
            reply_markup=get_admin_main_menu()
        )
        
        try:
            await message.bot.send_message(
                admin_id,
                f"🎉 Tabriklaymiz!\n\n"
                f"Siz {message.from_user.full_name} tomonidan admin qilindingiz!\n\n"
                f"🔑 Sizning ruxsatlaringiz: {perms_text}\n\n"
                f"Admin paneliga o'tish uchun /admin komandasi yuboring."
            )
        except:
            pass
        
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")


# ==================== ADMIN STATISTICS ====================

@router.message(F.text == "📋 Admin statistic")
async def admin_statistics(message: Message):
    if not await has_permission_check(message.from_user.id, "Admin statistic"):
        await message.answer("❌ Sizda bu amalni bajarish uchun ruxsat yo'q!")
        return
    
    admins = await db.get_all_admins()
    
    if not admins:
        await message.answer(
            "📋 Hozircha qo'shimcha adminlar yo'q!\n\n"
            f"👑 Faqat owner: <a href='tg://user?id={config.OWNER_ID}'>Owner</a>",
            reply_markup=get_admin_main_menu()
        )
        return
    
    text = "📋 <b>Adminlar ro'yxati:</b>\n\n"
    text += f"👑 <b>Owner:</b> <a href='tg://user?id={config.OWNER_ID}'>ID: {config.OWNER_ID}</a>\n\n"
    text += "👨‍💼 <b>Qo'shimcha adminlar:</b>\n\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    for idx, admin in enumerate(admins, 1):
        perms = admin['permissions']
        perms_text = "Barcha ruxsatlar" if 'all' in perms or '7' in perms else f"{len(perms)} ta ruxsat"
        
        text += f"{idx}. Admin ID: <code>{admin['user_id']}</code>\n"
        text += f"   🔑 {perms_text}\n"
        text += f"   📅 {admin['added_date'].strftime('%d.%m.%Y')}\n\n"
        
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"👤 Admin {idx}",
                url=f"tg://user?id={admin['user_id']}"
            )
        ])
    
    await message.answer(text, reply_markup=keyboard)


# ==================== ANNOUNCEMENT CHANNEL SETTINGS ====================

@router.message(Command("set_announcement_channel"))
async def set_announcement_channel(message: Message):
    """
    E'lon kanalini sozlash.
    Format: /set_announcement_channel -1001234567890 kino_vibe_films kino_vibe_bot
    
    Parametrlar:
      1) Kanal ID si (masalan: -1001234567890)  yoki @username
      2) Kanal username (@ belgisisiz, masalan: kino_vibe_films)
      3) Bot username (@ belgisisiz, masalan: kino_vibe_bot)
    """
    if message.from_user.id != config.OWNER_ID:
        return
    
    # Command argumentlarini olish: /set_announcement_channel ID USERNAME BOT
    args = message.text.split()[1:]  # komandadan keyingi qismlar

    if len(args) < 3:
        current_channel = await db.get_setting('announcement_channel') or "—"
        current_ch_username = await db.get_setting('announcement_channel_username') or "—"
        current_bot = await db.get_setting('bot_username') or "—"

        await message.answer(
            "📢 <b>E'lon kanali sozlamalari</b>\n\n"
            f"Hozirgi kanal ID: <code>{current_channel}</code>\n"
            f"Hozirgi kanal username: @{current_ch_username}\n"
            f"Hozirgi bot username: @{current_bot}\n\n"
            "<b>O'zgartirish uchun:</b>\n"
            "<code>/set_announcement_channel KANAL_ID KANAL_USERNAME BOT_USERNAME</code>\n\n"
            "Misol:\n"
            "<code>/set_announcement_channel -1001234567890 kino_vibe_films kino_vibe_bot</code>\n\n"
            "⚠️ Bot kanalga admin qilingan bo'lishi kerak!"
        )
        return

    channel_id = args[0].strip()
    channel_username = args[1].strip().lstrip('@')
    bot_username = args[2].strip().lstrip('@')

    # Kanalga ulanishni tekshirish
    try:
        chat = await message.bot.get_chat(channel_id)
        channel_title = chat.title
    except Exception as e:
        await message.answer(
            f"❌ Kanal topilmadi: {e}\n\n"
            "Bot kanalga admin qilinganligini tekshiring!"
        )
        return

    await db.set_setting('announcement_channel', channel_id)
    await db.set_setting('announcement_channel_username', channel_username)
    await db.set_setting('bot_username', bot_username)

    await message.answer(
        f"✅ <b>E'lon kanali sozlandi!</b>\n\n"
        f"📢 Kanal: {channel_title}\n"
        f"🆔 ID: <code>{channel_id}</code>\n"
        f"🌐 Kanal: @{channel_username}\n"
        f"🤖 Bot: @{bot_username}\n\n"
        f"Endi har yangi kino qo'shilganda shu kanalga avtomatik e'lon yuboriladi.",
        reply_markup=get_admin_main_menu()
    )


# ==================== CHANGE ADMIN CONTACT LINK ====================

@router.message(Command("set_admin_contact"))
async def set_admin_contact(message: Message):
    if message.from_user.id != config.OWNER_ID:
        return
    
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer(
            "📝 <b>Admin contact link ni o'zgartirish</b>\n\n"
            "Format: <code>/set_admin_contact https://t.me/username</code>\n\n"
            "Hozirgi link:\n"
            f"{await db.get_setting('admin_contact_link')}"
        )
        return
    
    new_link = args[1].strip()
    
    if not (new_link.startswith('http://') or new_link.startswith('https://')):
        await message.answer("❌ Link http:// yoki https:// bilan boshlanishi kerak!")
        return
    
    await db.set_setting('admin_contact_link', new_link)
    
    await message.answer(
        f"✅ <b>Admin contact link yangilandi!</b>\n\n"
        f"Yangi link: {new_link}",
        reply_markup=get_admin_main_menu()
    )


# ==================== DELETE ADMIN ====================

@router.message(Command("delete_admin"))
async def delete_admin(message: Message):
    if message.from_user.id != config.OWNER_ID:
        return
    
    args = message.text.split()
    
    if len(args) < 2:
        await message.answer(
            "🗑 <b>Adminni o'chirish</b>\n\n"
            "Format: <code>/delete_admin USER_ID</code>\n\n"
            "Misol: <code>/delete_admin 123456789</code>"
        )
        return
    
    try:
        admin_id = int(args[1])
        
        admin = await db.get_admin(admin_id)
        if not admin:
            await message.answer("❌ Bunday admin topilmadi!")
            return
        
        await db.delete_admin(admin_id)
        
        await message.answer(
            f"✅ <b>Admin o'chirildi!</b>\n\n"
            f"👤 ID: <code>{admin_id}</code>",
            reply_markup=get_admin_main_menu()
        )
        
        try:
            await message.bot.send_message(
                admin_id,
                "📢 Siz admin huquqlaridan mahrum qilindingiz!"
            )
        except:
            pass
            
    except ValueError:
        await message.answer("❌ Noto'g'ri ID format!")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")


# ==================== EXPORT FILMS TO DOCX ====================

@router.message(Command("export_films"))
async def export_films(message: Message):
    """
    Barcha kinolarni Word (.docx) faylga eksport qilish.
    Faqat adminlar uchun.
    """
    if not await is_admin_check(message.from_user.id):
        return

    status = await message.answer("⏳ Fayl tayyorlanmoqda...")

    try:
        import json
        import asyncio
        import os
        import tempfile
        from datetime import datetime

        # Barcha kinolarni olish
        films = await db.get_all_films()

        if not films:
            await status.edit_text("❌ Hozircha kinolar yo'q!")
            return

        # Har bir kino uchun qismlar sonini olish
        films_data = []
        for film in films:
            parts_count = await db.get_parts_count(film['code'])
            films_data.append({
                "name": film['name'],
                "code": film['code'],
                "parts_count": int(parts_count)
            })

        # JS script orqali docx yaratish
        films_json = json.dumps(films_data, ensure_ascii=False)
        tmp_output = tempfile.mktemp(suffix=".docx")

        # Script joylashuvi — bot bilan bir papkada bo'lishi kerak
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "create_films_doc.js")

        proc = await asyncio.create_subprocess_exec(
            "node", script_path, films_json, tmp_output,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            await status.edit_text(f"❌ Xatolik: {stderr.decode()}")
            return

        # Faylni botda yuborish
        today = datetime.now().strftime("%d.%m.%Y")
        filename = f"kinolar_{today}.docx"

        with open(tmp_output, "rb") as f:
            await message.answer_document(
                document=(filename, f.read()),
                caption=(
                    f"📄 <b>Kinolar ro'yxati</b>\n\n"
                    f"📅 Sana: {today}\n"
                    f"🎬 Jami kinolar: {len(films_data)} ta\n"
                    f"📹 Jami qismlar: {sum(f['parts_count'] for f in films_data)} ta"
                )
            )

        await status.delete()

        # Vaqtinchalik faylni o'chirish
        os.remove(tmp_output)

    except Exception as e:
        await status.edit_text(f"❌ Xatolik yuz berdi: {e}")
