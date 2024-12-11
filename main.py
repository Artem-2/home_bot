import asyncio
import logging 
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from assistive.db.DBhelp import BotDB
from assistive.config_read import config


from handlers import console_management
from handlers import shopping_cart_manegement

#строчка для тестов без нее нет возмождности проверить работу db
BotDB.get()




logger = logging.getLogger(__name__)




async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")

    storage = MemoryStorage()
    
    bot = Bot(token=config['TOKEN'], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.GLOBAL_USER)

    #добавление новых router
    dp.include_routers(console_management.router)
    dp.include_routers(shopping_cart_manegement.router)
    
    #отправка стартового сообщения администратору
    admins = config["ADMIN"].split(",")
    try:
        for c in admins:
            await bot.send_message(c,'Бот запущен')
    except:
        sys.exit("Неверный id админа \n")
        
    # Start
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        try:
            for c in admins:
                await bot.send_message(c,'Бот отключен')
        except:
            pass
        await dp.storage.close()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")