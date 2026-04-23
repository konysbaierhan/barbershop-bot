import asyncio
import logging
import sqlite3
import os
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# ============================================================
#  ⚙️  НАСТРОЙКИ — берутся из переменных окружения Railway
# ============================================================

BOT_TOKEN = os.getenv(8513130101:AAE0MoCgDpVhZS3KQaicTLJ4-PcmkOvLWzs)
ADMIN_ID = int(os.getenv(829018731))

# 🔗 Вставьте сюда прямую ссылку на вашу страницу записи в DIKIDI
DIKIDI_URL = "https://dikidi.net/2055441"

# 📍 Контактные данные барбершопа
BARBERSHOP_ADDRESS = "ул. Калдаякова, 4, Астана"
BARBERSHOP_PHONE = "+7 (777) 000-00-00"

DB_FILE = "users.db"

# ============================================================
#  ЛОГИРОВАНИЕ
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ============================================================
#  БАЗА ДАННЫХ
# ============================================================

def init_db() -> None:
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    logger.info("База данных инициализирована.")


def save_user(user_id: int) -> None:
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,),
        )
        conn.commit()


def get_all_user_ids() -> list[int]:
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute("SELECT user_id FROM users").fetchall()
    return [row[0] for row in rows]

# ============================================================
#  КЛАВИАТУРЫ
# ============================================================

def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✂️ Записаться онлайн", url=DIKIDI_URL)],
            [InlineKeyboardButton(text="💈 Услуги и прайс", callback_data="services")],
            [InlineKeyboardButton(text="📍 Контакты", callback_data="contacts")],
        ]
    )

# ============================================================
#  БОТ И ДИСПЕТЧЕР
# ============================================================

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ============================================================
#  ХЭНДЛЕРЫ
# ============================================================

@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    save_user(message.from_user.id)
    welcome_text = (
        "<b>Добро пожаловать в территорию мужского стиля.</b>\n\n"
        "Выберите действие ниже 👇"
    )
    await message.answer(welcome_text, reply_markup=main_keyboard())


@dp.message(Command("broadcast"))
async def cmd_broadcast(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔️ У вас нет прав на использование этой команды.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer(
            "⚠️ Укажите текст рассылки.\n"
            "Пример: <code>/broadcast Парни, сегодня скидка 20%!</code>"
        )
        return

    broadcast_text = parts[1].strip()
    user_ids = get_all_user_ids()

    if not user_ids:
        await message.answer("📭 В базе нет пользователей.")
        return

    success_count = 0
    fail_count = 0

    await message.answer(f"📤 Начинаю рассылку для {len(user_ids)} пользователей...")

    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=broadcast_text)
            success_count += 1
        except Exception as e:
            logger.warning(f"Не удалось отправить {user_id}: {e}")
            fail_count += 1
        await asyncio.sleep(0.05)

    await message.answer(
        f"✅ Готово!\n"
        f"Доставлено: <b>{success_count}</b>\n"
        f"Не доставлено: <b>{fail_count}</b>"
    )


@dp.callback_query(F.data == "services")
async def callback_services(callback: CallbackQuery) -> None:
    services_text = (
        "💈 <b>Услуги и прайс</b>\n\n"
        "✂️ Стрижка — <b>6 000 ₸</b>\n"
        "🪒 Борода — <b>3 000 ₸</b>\n\n"
        "Для записи нажмите <b>✂️ Записаться онлайн</b>"
    )
    await callback.message.answer(services_text)
    await callback.answer()


@dp.callback_query(F.data == "contacts")
async def callback_contacts(callback: CallbackQuery) -> None:
    contacts_text = (
        "📍 <b>Наш адрес:</b>\n"
        f"{Калдаякова 4}\n\n"
        "📞 <b>Телефон:</b>\n"
        f"{87754709410}"
    )
    await callback.message.answer(contacts_text)
    await callback.answer()

# ============================================================
#  ЗАПУСК
# ============================================================

async def main() -> None:
    init_db()
    logger.info("Бот запускается...")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
