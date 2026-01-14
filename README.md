# 🎬 Kino Bot - Telegram Bot

Professional Telegram kino bot - webhook rejimida ishlaydigan, PostgreSQL database bilan to'liq funksional bot.

## 📋 Xususiyatlar

### Foydalanuvchi funksiyalari:
- 🎬 Kino qidirish (kod orqali)
- 📊 Kinolar statistikasi (Top 20)
- 📞 Adminga murojat
- 📢 Majburiy kanal obunasi tekshiruvi

### Admin funksiyalari:
- ➕ **Add film** - Yangi kino qo'shish
- 📹 **Add parts** - Kino qismlarini qo'shish
- 🗑 **Delete film** - Kino yoki qismni o'chirish
- 📢 **Channels** - Majburiy kanallar boshqaruvi
- 👥 **User Statistic** - Foydalanuvchilar statistikasi
- 🎞 **Film Statistic** - Kinolar ro'yxati (30 tadan sahifalangan)
- ✍️ **All write** - Barcha foydalanuvchilarga xabar yuborish
- 👨‍💼 **Add admin** - Yangi admin qo'shish (faqat owner)
- 📋 **Admin statistic** - Adminlar ro'yxati
- 🏠 **Main menu** - Admin menyusiga qaytish

## 🚀 O'rnatish

### 1. Repozitoriyani klonlash
```bash
git clone <repository-url>
cd kino_bot
```

### 2. Virtual muhit yaratish
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows
```

### 3. Kerakli paketlarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. PostgreSQL database yaratish

#### Render.com da (tavsiya etiladi):
1. Render.com ga kiring
2. "New +" -> "PostgreSQL" ni tanlang
3. Database nomini kiriting
4. "Create Database" tugmasini bosing
5. Database ma'lumotlarini (CONNECTION STRING) nusxalang

#### Local PostgreSQL:
```bash
# PostgreSQL o'rnatilganligini tekshiring
psql --version

# Database yaratish
createdb kino_bot

# Database URL:
# postgresql://username:password@localhost:5432/kino_bot
```

### 5. .env fayli yaratish
`.env.example` faylidan `.env` yarating va quyidagi ma'lumotlarni kiriting:

```env
BOT_TOKEN=your_bot_token_from_botfather
OWNER_ID=your_telegram_id
DATABASE_URL=postgresql://user:password@host:port/dbname
WEBHOOK_URL=https://your-domain.com
WEBHOOK_PATH=/webhook
PORT=8000
```

**Ma'lumotlarni qayerdan olish:**
- `BOT_TOKEN`: [@BotFather](https://t.me/BotFather) dan yangi bot yarating
- `OWNER_ID`: [@userinfobot](https://t.me/userinfobot) ga `/start` yuboring
- `DATABASE_URL`: Render.com yoki local PostgreSQL dan
- `WEBHOOK_URL`: Render.com yoki boshqa hosting URL manzili
- `PORT`: 8000 (yoki hostingda belgilangan port)

### 6. Render.com da deploy qilish

#### A. Render.com da Web Service yaratish:
1. [Render.com](https://render.com) ga kiring
2. "New +" -> "Web Service" ni tanlang
3. GitHub repozitoriyangizni ulang
4. Sozlamalar:
   - **Name**: kino-bot (yoki istalgan nom)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: Free

#### B. Environment Variables qo'shish:
Settings -> Environment bo'limida quyidagilarni qo'shing:
- `BOT_TOKEN`
- `OWNER_ID`
- `DATABASE_URL` (PostgreSQL dan)
- `WEBHOOK_URL` (Render service URL, masalan: https://kino-bot.onrender.com)
- `WEBHOOK_PATH` = /webhook
- `PORT` = 8000

#### C. Deploy
"Create Web Service" tugmasini bosing va deploy jarayonini kuting.

### 7. Local ishga tushirish (test uchun)

⚠️ **Diqqat**: Local ishlatish uchun ngrok yoki boshqa tunnel service kerak!

```bash
# ngrok o'rnatish
# https://ngrok.com/download

# ngrok ishga tushirish
ngrok http 8000

# .env faylidagi WEBHOOK_URL ni ngrok URL ga o'zgartiring
# Masalan: https://abc123.ngrok.io

# Botni ishga tushirish
python main.py
```

## 📖 Foydalanish

### Foydalanuvchi:
1. Botni ishga tushirish: `/start`
2. Kino qidirish: "🎬 Kino qidirish" -> kod kiriting
3. Statistika: "📊 Kinolar statistikasi"
4. Murojat: "📞 Adminga murojat"

### Admin:
1. Admin paneliga kirish: `/admin`
2. Kino qo'shish:
   - "➕ Add film" -> kod -> nom -> izoh -> rasm
   - "📹 Add parts" -> kod -> videolar
3. Kanal qo'shish:
   - "📢 Channels" -> "➕ Kanal qo'shish" -> kanal ID/username
4. Adminlar:
   - "👨‍💼 Add admin" -> ID -> ruxsatlar (1,2,3 yoki 7)
   - Ruxsatlar: 1-Add film, 2-Add parts, 3-Delete, 4-Channels, 5-User Stats, 6-Film Stats, 7-Barchasi, 8-Broadcast, 9-Add admin, 10-Admin stats

### Owner maxsus komandalar:
- `/set_admin_contact https://t.me/username` - Admin contact linkni o'zgartirish
- `/delete_admin USER_ID` - Adminni o'chirish

## 🗄️ Database strukturasi

### Jadvallar:
- **users** - Foydalanuvchilar
- **films** - Kinolar (kod, nom, izoh, rasm)
- **film_parts** - Kino qismlari
- **film_views** - Ko'rishlar statistikasi
- **channels** - Majburiy kanallar
- **admins** - Adminlar va ruxsatlar
- **settings** - Bot sozlamalari

## 🔧 Texnik xususiyatlar

- **Framework**: aiogram 3.15.0
- **Database**: PostgreSQL (asyncpg)
- **Mode**: Webhook (production uchun)
- **Architecture**: Modular (handlers, database, utils)
- **State Management**: FSM (Finite State Machine)
- **Keyboard Type**: ReplyKeyboard (zamonaviy dizayn)

## 📝 Fayl strukturasi

```
kino_bot/
├── main.py                 # Asosiy bot fayli
├── config.py              # Konfiguratsiya
├── requirements.txt       # Kerakli paketlar
├── .env                   # Environment variables
├── database/
│   ├── __init__.py
│   └── db.py             # Database modellari
├── handlers/
│   ├── __init__.py
│   ├── user.py           # Foydalanuvchi handlerlari
│   ├── admin.py          # Admin handlerlari (film)
│   ├── admin_stats.py    # Admin statistika
│   └── admin_management.py # Admin boshqaruvi
├── utils/
│   ├── __init__.py
│   ├── keyboards.py      # Klaviaturalar
│   └── helpers.py        # Yordamchi funksiyalar
└── middlewares/          # Kelajakda middleware'lar
```

## 🛠️ Muammolarni hal qilish

### Bot ishlamayapti:
1. Webhook to'g'ri sozlanganligini tekshiring
2. Database ulanishini tekshiring
3. Bot tokenni tekshiring
4. Loglarni ko'ring: `heroku logs --tail` yoki Render logs

### Kanal obuna ishlamayapti:
1. Bot kanal adminlari orasida bo'lishi kerak
2. Kanal ID to'g'ri kiritilganligini tekshiring
3. Yopiq kanallar uchun bot admin bo'lishi shart

### Admin panel ochilmayapti:
1. OWNER_ID to'g'ri sozlanganligini tekshiring
2. `/admin` komandasi yuborilganligini tekshiring
3. Database admins jadvalini tekshiring

## 📞 Yordam

Muammolar yoki savollar uchun:
- GitHub Issues
- Telegram: [@forever_projects](https://t.me/forever_projects)

## 📄 Litsenziya

MIT License

---

**Ishlab chiqildi**: Professional Telegram Bot
**Versiya**: 1.0.0
**Sana**: 2026
