import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ВСТАВЬТЕ ВАШИ ДАННЫЕ
API_TOKEN = '9094086525:AAHjInXsw-7E_w8mm9PT99wZjDbUGZhHXaQ'
ADMIN_ID = 8313826963 # Ваш ID (узнать у @userinfobot)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Состояния для сбора заявки
class Booking(StatesGroup):
    waiting_contact = State()

# Главное меню
def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🚲 Забронировать Minako Monster Pro", callback_data="book_bike")
    builder.button(text="💰 Тарифы", callback_data="prices")
    builder.button(text="📍 Адрес и время работы", callback_data="address")
    builder.adjust(1)
    return builder.as_markup()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.reply(
        f"Привет, {message.from_user.first_name}! ⚡️\n"
        f"Добро пожаловать в прокат электровелосипедов в Красноярске.\n"
        f"У нас доступна модель Minako Monster Pro. Выберите действие:", 
        reply_markup=get_main_menu()
    )

# Тарифы
@dp.callback_query(F.data == "prices")
async def show_prices(callback: types.CallbackQuery):
    await callback.message.answer(
        "💰 Наши тарифы на Minako Monster Pro:\n\n"
        "📅 Неделя (7 дней) — 2700 руб.\n"
        "📅 Месяц (30 дней) — 9500 руб.\n\n"
        "✅ Без залога!\n"
        "Для аренды нужен только паспорт."
    )
    await callback.answer()

# Адрес
@dp.callback_query(F.data == "address")
async def show_address(callback: types.CallbackQuery):
    await callback.message.answer(
        "📍 Наш адрес:\n"
        "г. Красноярск, ул. Березина, 90\n\n"
        "🕒 Режим работы:\n"
        "Ежедневно с 10:00 до 19:00"
    )
    await callback.answer()

# Начало бронирования (сразу переходим к сбору номера)
@dp.callback_query(F.data == "book_bike")
async def start_booking(callback: types.CallbackQuery, state: FSMContext):
    # Создаем кнопку "Поделиться контактом"
    kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="📱 Отправить мой номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await callback.message.answer(
        "Вы хотите забронировать Minako Monster Pro.\n\n"
        "Пожалуйста, нажмите кнопку ниже, чтобы отправить свой номер телефона. "
        "Мы свяжемся с вами, чтобы подтвердить время и ответить на вопросы.",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await state.set_state(Booking.waiting_contact)
    await callback.answer()

# Получаем контакт и отправляем уведомление Админу
@dp.message(Booking.waiting_contact, F.contact)
async def process_contact(message: types.Message, state: FSMContext):
    user = message.from_user
    phone = message.contact.phone_number

    # Убираем клавиатуру
    remove_kb = types.ReplyKeyboardRemove()
    
    # 1. Сообщение клиенту
    await message.answer(
        "✅ Спасибо! Ваша заявка на бронирование Minako Monster Pro принята.\n"
        "Мы свяжемся с вами в ближайшее время (в рабочее время с 10:00 до 19:00).",
        reply_markup=remove_kb
    )

    # 2. Уведомление ВАМ (Админу)
    admin_text = (
        f"🚨 НОВАЯ БРОНЬ (Minako Monster Pro)!\n\n"
        f"Клиент: {user.first_name}\n"
        f"Юзернейм: @{user.username if user.username else 'Нет'}\n"
        f"Телефон: {phone}\n\n"
        f"Свяжитесь с клиентом!"
    )
    await bot.send_message(ADMIN_ID, admin_text)
    await state.clear()

async def main():
    print("Бот проката Minako Monster Pro запущен!")
    await dp.start_polling(bot)

if name == 'main':
    asyncio.run(main())
