import asyncio
import logging
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

import config
from database.db import db
from handlers import user, admin, admin_stats, admin_management

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot va Dispatcher yaratish
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


async def on_startup():
    """Bot ishga tushganda"""
    logger.info("Bot ishga tushmoqda...")

    # Database ulanish
    await db.connect()
    logger.info("Database ga ulanish muvaffaqiyatli!")

    # Jadvallarni yaratish
    await db.create_tables()
    logger.info("Database jadvallari tekshirildi/yaratildi")

    # Webhook o'rnatish — chat_join_request eventini qo'shish MUHIM!
    webhook_url = f"{config.WEBHOOK_URL}{config.WEBHOOK_PATH}"
    await bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True,
        allowed_updates=[
            "message",
            "callback_query",
            "chat_join_request",   # ← yopiq kanal so'rovlari uchun SHART
            "my_chat_member",
            "chat_member",
        ]
    )
    logger.info(f"Webhook o'rnatildi: {webhook_url}")

    bot_info = await bot.get_me()
    logger.info(f"Bot ishga tushdi: @{bot_info.username}")


async def on_shutdown():
    """Bot to'xtaganda"""
    logger.info("Bot to'xtatilmoqda...")

    await bot.delete_webhook(drop_pending_updates=True)
    await db.disconnect()
    await bot.session.close()

    logger.info("Bot to'xtatildi")


async def main():
    """Asosiy funksiya"""
    # Routerlarni ro'yxatdan o'tkazish
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(admin_stats.router)
    dp.include_router(admin_management.router)

    # Startup va shutdown handlerlar
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Web application yaratish
    app = web.Application()

    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    webhook_handler.register(app, path=config.WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    async def root(request):
        return web.Response(text="Bot is running ✅")

    app.router.add_get('/', root)
    app.router.add_get('/health', root)

    logger.info(f"Server ishga tushmoqda: 0.0.0.0:{config.PORT}")
    return app


if __name__ == '__main__':
    try:
        web.run_app(asyncio.run(main()), host='0.0.0.0', port=config.PORT)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi (KeyboardInterrupt)")
