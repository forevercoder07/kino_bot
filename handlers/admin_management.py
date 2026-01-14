from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
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
    """Admin qo'shishni boshlash"""
    # Faqat owner qo'sha oladi
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
    """Admin ID ni qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        from handlers.admin import admin_panel
        await admin_panel(message, state)
        return
    
    try:
        admin_id = int(message.text.strip())
        
        # Owner ID ni tekshirish
        if admin_id == config.OWNER_ID:
            await message.answer("❌ Bu sizning ID ingiz! Siz allaqachon ownersiz.")
            return
        
        # Allaqachon admin emasligini tekshirish
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
            "• <code>7</code> - barcha ruxsatlar\n"
            "• <code>1,2,4,5,6</code> - bir nechta ruxsatlar\n\n"
            "Ruxsatlarni vergul bilan ajratib kiriting:"
        )
        
        await message.answer(permissions_text, reply_markup=get_cancel_keyboard())
        
    except ValueError:
        await message.answer("❌ Noto'g'ri ID! Faqat raqam kiriting.")


@router.message(AdminStates.waiting_admin_permissions)
async def add_admin_permissions(message: Message, state: FSMContext):
    """Admin ruxsatlarini qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        from handlers.admin import admin_panel
        await admin_panel(message, state)
        return
    
    data = await state.get_data()
    admin_id = data['admin_id']
    
    # Ruxsatlarni parse qilish
    permissions = parse_permissions(message.text)
    
    if not permissions:
        await message.answer(
            "❌ Noto'g'ri format!\n\n"
            "Iltimos, to'g'ri formatda kiriting (masalan: 1,2,3)"
        )
        return
    
    try:
        # Adminni qo'shish
        await db.add_admin(admin_id, permissions, message.from_user.id)
        
        await state.clear()
        
        # Ruxsatlarni chiroyli ko'rsatish
        perms_text = ", ".join(permissions) if 'all' not in permissions else "Barcha ruxsatlar"
        
        await message.answer(
            f"✅ <b>Admin qo'shildi!</b>\n\n"
            f"👤 ID: <code>{admin_id}</code>\n"
            f"🔑 Ruxsatlar: {perms_text}\n\n"
            f"Yangi admin /admin komandasi orqali admin paneliga kirishi mumkin.",
            reply_markup=get_admin_main_menu()
        )
        
        # Yangi adminga xabar yuborish
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
    """Adminlar statistikasi"""
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
    
    # Inline keyboard yaratish
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    for idx, admin in enumerate(admins, 1):
        perms = admin['permissions']
        perms_text = "Barcha ruxsatlar" if 'all' in perms or '7' in perms else f"{len(perms)} ta ruxsat"
        
        text += f"{idx}. Admin ID: <code>{admin['user_id']}</code>\n"
        text += f"   🔑 {perms_text}\n"
        text += f"   📅 {admin['added_date'].strftime('%d.%m.%Y')}\n\n"
        
        # Har bir admin uchun profil tugmasi
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"👤 Admin {idx}",
                url=f"tg://user?id={admin['user_id']}"
            )
        ])
    
    await message.answer(text, reply_markup=keyboard)


# ==================== CHANGE ADMIN CONTACT LINK ====================

@router.message(F.text.startswith("/set_admin_contact"))
async def set_admin_contact(message: Message):
    """Admin contact link ni o'zgartirish"""
    # Faqat owner
    if message.from_user.id != config.OWNER_ID:
        return
    
    # Komanda formatini tekshirish
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer(
            "📝 <b>Admin contact link ni o'zgartirish</b>\n\n"
            "Format: <code>/set_admin_contact https://t.me/username</code>\n\n"
            "Hozirgi link:\n"
            f"{await db.get_setting('admin_contact_link')}"
        )
        return
    
    new_link = parts[1].strip()
    
    # Link formatini tekshirish
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

@router.message(F.text.startswith("/delete_admin"))
async def delete_admin(message: Message):
    """Adminni o'chirish"""
    # Faqat owner
    if message.from_user.id != config.OWNER_ID:
        return
    
    parts = message.text.split()
    
    if len(parts) < 2:
        await message.answer(
            "🗑 <b>Adminni o'chirish</b>\n\n"
            "Format: <code>/delete_admin USER_ID</code>\n\n"
            "Misol: <code>/delete_admin 123456789</code>"
        )
        return
    
    try:
        admin_id = int(parts[1])
        
        # Tekshirish
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
        
        # Adminga xabar yuborish
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
