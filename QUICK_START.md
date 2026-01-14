# 🚀 Tezkor Ishga Tushirish

## 1. Render.com da PostgreSQL yaratish

1. [Render.com](https://render.com) ga kiring
2. "New +" → "PostgreSQL"
3. Name: `kino-bot-db`
4. "Create Database"
5. **Internal Database URL** ni nusxalang (masalan: `postgresql://...`)

## 2. Render.com da Web Service yaratish

1. GitHub'ga loyihani yuklang
2. Render.com da "New +" → "Web Service"
3. GitHub repo'ni ulang
4. Sozlamalar:
   ```
   Name: kino-bot
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python main.py
   ```

## 3. Environment Variables

Settings → Environment da qo'shing:

```env
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
OWNER_ID=123456789
DATABASE_URL=postgresql://kino_bot_user:password@dpg-xxx.oregon-postgres.render.com/kino_bot_db
WEBHOOK_URL=https://kino-bot.onrender.com
WEBHOOK_PATH=/webhook
PORT=8000
```

**Qayerdan olish:**
- BOT_TOKEN: [@BotFather](https://t.me/BotFather) - /newbot
- OWNER_ID: [@userinfobot](https://t.me/userinfobot) - /start
- DATABASE_URL: Render PostgreSQL Internal URL
- WEBHOOK_URL: Render web service URL (https://yourapp.onrender.com)

## 4. Deploy

"Create Web Service" → Deploy jarayonini kuting (2-3 daqiqa)

## 5. Botni tekshirish

Telegram'da botingizni oching:
1. `/start` - Ishga tushirish
2. `/admin` - Admin panel (siz owner bo'lganingiz uchun)

## ✅ Tayyor!

Bot ishga tushdi va ishlashga tayyor!

---

## 🔧 Keyingi qadamlar

### Kanal qo'shish:
1. `/admin` → "📢 Channels"
2. "➕ Kanal qo'shish"
3. Kanal ID yoki @username kiriting
4. Bot kanalga admin qilinganligini tekshiring!

### Kino qo'shish:
1. `/admin` → "➕ Add film"
2. Kod kiriting (masalan: 101)
3. Kino nomini kiriting
4. Izoh kiriting
5. Rasm yuboring
6. "📹 Add parts" orqali videolarni qo'shing

### Admin qo'shish:
1. `/admin` → "👨‍💼 Add admin"
2. Admin ID sini kiriting
3. Ruxsatlar kiriting (7 - barchasi)

---

## 📱 Test qilish

Kino qidirish:
1. Foydalanuvchi sifatida: "🎬 Kino qidirish"
2. Kod kiriting (masalan: 101)
3. Qismni tanlang (agar bir nechta bo'lsa)

---

## ⚠️ Muhim eslatmalar

1. **Bot kanal adminlari orasida bo'lishi kerak** - majburiy obuna ishlashi uchun
2. **Webhook ishlatiladi** - polling emas
3. **Render Free plan** - 15 daqiqa faoliyatsizlikdan keyin uxlaydi
4. **Database backup** - Render da 7 kun backup mavjud

---

## 🆘 Yordam

Muammo bo'lsa:
- Render Logs ni tekshiring
- Environment variables to'g'riligini tekshiring
- Bot token va Database URL ni qayta tekshiring

**Telegram**: [@forever_projects](https://t.me/forever_projects)
