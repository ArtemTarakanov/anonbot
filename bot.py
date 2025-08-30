import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('8364318349:AAHh6UODoQHMKwgnUZha3ZVDsyiM5fZso-g')  # Токен вашего бота
ADMIN_ID = int(os.getenv('1492658199'))  # Ваш Telegram ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    if user.id == ADMIN_ID:
        await update.message.reply_text(
            "Привет, админ! 👋\n"
            "Бот готов к работе. Все сообщения от пользователей будут пересылаться вам."
        )
    else:
        await update.message.reply_text(
            "Добро пожаловать! 👋\n"
            "Отправьте мне любое сообщение, и оно будет передано администратору."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик всех сообщений"""
    user = update.effective_user
    message = update.message
    
    # Если сообщение от админа - игнорируем
    if user.id == ADMIN_ID:
        await message.reply_text("Вы администратор. Ваши сообщения не пересылаются.")
        return
    
    # Формируем информацию о пользователе
    user_info = f"👤 От: {user.first_name}"
    if user.last_name:
        user_info += f" {user.last_name}"
    if user.username:
        user_info += f" (@{user.username})"
    user_info += f"\n🆔 ID: {user.id}\n\n"
    
    try:
        # Пересылаем сообщение админу
        if message.text:
            # Текстовое сообщение
            full_message = user_info + f"📝 Сообщение:\n{message.text}"
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=full_message
            )
        elif message.photo:
            # Фото
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=message.photo[-1].file_id,
                caption=user_info + f"📷 Фото: {message.caption or ''}"
            )
        elif message.document:
            # Документ
            await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=message.document.file_id,
                caption=user_info + f"📄 Документ: {message.caption or ''}"
            )
        elif message.voice:
            # Голосовое сообщение
            await context.bot.send_voice(
                chat_id=ADMIN_ID,
                voice=message.voice.file_id,
                caption=user_info + "🎤 Голосовое сообщение"
            )
        elif message.video:
            # Видео
            await context.bot.send_video(
                chat_id=ADMIN_ID,
                video=message.video.file_id,
                caption=user_info + f"🎥 Видео: {message.caption or ''}"
            )
        elif message.sticker:
            # Стикер
            await context.bot.send_sticker(
                chat_id=ADMIN_ID,
                sticker=message.sticker.file_id
            )
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=user_info + "🎭 Стикер"
            )
        else:
            # Другие типы сообщений
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=user_info + "❓ Получен неподдерживаемый тип сообщения"
            )
        
        # Подтверждение пользователю
        await message.reply_text("✅ Ваше сообщение отправлено администратору!")
        
    except Exception as e:
        logger.error(f"Ошибка при пересылке сообщения: {e}")
        await message.reply_text("❌ Произошла ошибка при отправке сообщения.")

async def get_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для получения своего ID"""
    user_id = update.effective_user.id
    await update.message.reply_text(f"Ваш Telegram ID: {user_id}")

def main() -> None:
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("Не установлен BOT_TOKEN!")
        return
    
    if not ADMIN_ID:
        logger.error("Не установлен ADMIN_ID!")
        return
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("myid", get_my_id))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()