import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, ADMIN_CHAT_ID
# from google_sheets import GoogleSheetsManager

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Менеджер Google Sheets (временно отключен)
# sheets_manager = GoogleSheetsManager()

# Состояния для FSM
class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_watch_model = State()
    waiting_for_payment = State()
    waiting_for_admin_approval = State()
    waiting_for_location = State()

# Список моделей часов
WATCH_MODELS = [
    "Rolex Submariner",
    "Omega Seamaster", 
    "Tag Heuer Carrera",
    "Breitling Navitimer",
    "Patek Philippe Calatrava"
]

# Способы оплаты
PAYMENT_METHODS = [
    "Наличные",
    "Банковская карта",
    "Перевод на карту",
    "Криптовалюта"
]

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обработчик команды /start"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Оформить заказ", callback_data="start_order")]
    ])
    
    await message.answer(
        "👋 Добро пожаловать в магазин часов!\n\n"
        "Нажмите кнопку ниже, чтобы оформить заказ:",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "start_order")
async def start_order_callback(callback_query: CallbackQuery, state: FSMContext):
    """Начало оформления заказа"""
    await callback_query.answer()
    await state.set_state(OrderStates.waiting_for_name)
    await callback_query.message.answer(
        "📝 Оформление заказа\n\n"
        "Введите ваше имя:"
    )

@dp.message(OrderStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Обработка имени"""
    await state.update_data(name=message.text)
    await state.set_state(OrderStates.waiting_for_phone)
    await message.answer("📞 Введите ваш номер телефона:")

@dp.message(OrderStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    """Обработка телефона"""
    await state.update_data(phone=message.text)
    await state.set_state(OrderStates.waiting_for_address)
    await message.answer("📍 Введите адрес доставки:")

@dp.message(OrderStates.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    """Обработка адреса"""
    await state.update_data(address=message.text)
    await state.set_state(OrderStates.waiting_for_watch_model)
    
    # Создаем клавиатуру с моделями часов
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=model, callback_data=f"model_{i}")] 
        for i, model in enumerate(WATCH_MODELS)
    ])
    
    await message.answer("⌚ Выберите модель часов:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("model_"))
async def process_watch_model(callback_query: CallbackQuery, state: FSMContext):
    """Обработка выбора модели часов"""
    await callback_query.answer()
    model_index = int(callback_query.data.split("_")[1])
    selected_model = WATCH_MODELS[model_index]
    
    await state.update_data(watch_model=selected_model)
    await state.set_state(OrderStates.waiting_for_payment)
    
    # Создаем клавиатуру со способами оплаты
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=method, callback_data=f"payment_{i}")] 
        for i, method in enumerate(PAYMENT_METHODS)
    ])
    
    await callback_query.message.answer(
        f"✅ Выбрана модель: {selected_model}\n\n"
        "💳 Выберите способ оплаты:",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data.startswith("payment_"))
async def process_payment_method(callback_query: CallbackQuery, state: FSMContext):
    """Обработка выбора способа оплаты"""
    await callback_query.answer()
    payment_index = int(callback_query.data.split("_")[1])
    selected_payment = PAYMENT_METHODS[payment_index]
    
    # Получаем все данные заказа
    order_data = await state.get_data()
    order_data['payment_method'] = selected_payment
    order_data['user_id'] = callback_query.from_user.id
    order_data['username'] = callback_query.from_user.username
    
    # Обрабатываем заказ
    await process_order_data(callback_query.from_user.id, order_data)
    await state.clear()

@dp.message(Command("admin"))
async def admin_command(message: types.Message):
    """Команда для админа - просмотр статистики"""
    if message.from_user.id == ADMIN_CHAT_ID:
        await message.answer("Админ панель:\n/orders - просмотр заказов")
    else:
        await message.answer("У вас нет прав доступа")

async def process_order_data(user_id: int, order_data: dict):
    """Обработка данных заказа"""
    try:
        # Сохраняем данные в Google Sheets (временно отключено)
        # await sheets_manager.add_order(order_data)
        logging.info(f"Заказ получен: {order_data}")
        
        # Отправляем подтверждение пользователю
        await bot.send_message(
            user_id,
            "✅ Спасибо! Ваш заказ отправлен на рассмотрение.\n\n"
            "Ожидайте подтверждения от администратора. Вы получите уведомление, когда заказ будет принят."
        )
        
        # Устанавливаем состояние ожидания подтверждения админа
        from aiogram.fsm.context import FSMContext
        from aiogram.fsm.storage.base import StorageKey
        
        storage_key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
        state = FSMContext(storage=storage, key=storage_key)
        await state.set_state(OrderStates.waiting_for_admin_approval)
        
        # Уведомляем админа с кнопками
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять заказ", callback_data=f"accept_order_{user_id}"),
                InlineKeyboardButton(text="❌ Отклонить заказ", callback_data=f"reject_order_{user_id}")
            ]
        ])
        
        await bot.send_message(
            ADMIN_CHAT_ID,
            f"🆕 Новый заказ!\n\n"
            f"👤 Клиент: {order_data.get('name', 'Не указано')}\n"
            f"📞 Телефон: {order_data.get('phone', 'Не указано')}\n"
            f"📍 Адрес: {order_data.get('address', 'Не указано')}\n"
            f"⌚ Модель: {order_data.get('watch_model', 'Не указано')}\n"
            f"💳 Оплата: {order_data.get('payment_method', 'Не указано')}\n"
            f"🆔 ID пользователя: {user_id}",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logging.error(f"Ошибка при обработке заказа: {e}")
        await bot.send_message(user_id, "❌ Произошла ошибка при обработке заказа")

@dp.message(lambda message: message.web_app_data is not None)
async def handle_web_app_data(message: types.Message, state: FSMContext):
    """Обработка данных из Mini App"""
    try:
        # Парсим данные из Mini App
        order_data = json.loads(message.web_app_data.data)
        
        # Добавляем информацию о пользователе
        order_data['user_id'] = message.from_user.id
        order_data['username'] = message.from_user.username
        
        # Обрабатываем заказ
        await process_order_data(message.from_user.id, order_data)
        
    except json.JSONDecodeError:
        await message.answer("❌ Ошибка при обработке данных заказа")
    except Exception as e:
        logging.error(f"Ошибка при обработке данных из Mini App: {e}")
        await message.answer("❌ Произошла ошибка при обработке заказа")

@dp.message(lambda message: message.location is not None)
async def handle_location(message: types.Message, state: FSMContext):
    """Обработка отправленной локации"""
    try:
        # Получаем координаты
        latitude = message.location.latitude
        longitude = message.location.longitude
        
        # Создаем данные заказа с геолокацией
        order_data = {
            'user_id': message.from_user.id,
            'username': message.from_user.username,
            'name': message.from_user.first_name or 'Не указано',
            'phone': 'Не указано',
            'address': 'Не указано',
            'watch_model': 'Не указано',
            'payment_method': 'Не указано',
            'location': {
                'latitude': latitude,
                'longitude': longitude
            }
        }
        
        # Отправляем локацию админу
        await bot.send_location(
            ADMIN_CHAT_ID,
            latitude=latitude,
            longitude=longitude
        )
        
        # Уведомляем админа с кнопками принятия/отклонения
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Оформить заказ", callback_data=f"accept_order_{message.from_user.id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_order_{message.from_user.id}")
            ]
        ])
        
        await bot.send_message(
            ADMIN_CHAT_ID,
            f"📍 Получена геолокация от клиента!\n\n"
            f"👤 Клиент: {order_data['name']}\n"
            f"🆔 ID пользователя: {message.from_user.id}\n"
            f"📍 Локация: {latitude}, {longitude}\n\n"
            f"Оформить заказ или отклонить?",
            reply_markup=keyboard
        )
        
        # Устанавливаем состояние ожидания подтверждения админа
        from aiogram.fsm.context import FSMContext
        from aiogram.fsm.storage.base import StorageKey
        
        storage_key = StorageKey(bot_id=bot.id, chat_id=message.from_user.id, user_id=message.from_user.id)
        state = FSMContext(storage=storage, key=storage_key)
        await state.set_state(OrderStates.waiting_for_admin_approval)
        
        # Уведомляем пользователя
        await message.answer(
            "📍 Геолокация получена! Отправлена администратору для рассмотрения.\n\n"
            "Ожидайте подтверждения - мы свяжемся с вами в ближайшее время.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        
    except Exception as e:
        logging.error(f"Ошибка при обработке локации: {e}")
        await message.answer("❌ Произошла ошибка при обработке локации")

@dp.callback_query(lambda c: c.data.startswith("accept_order_"))
async def handle_accept_order(callback_query: CallbackQuery):
    """Обработка принятия заказа админом"""
    if callback_query.from_user.id != ADMIN_CHAT_ID:
        await callback_query.answer("У вас нет прав для этого действия")
        return
    
    user_id = int(callback_query.data.split("_")[2])
    
    try:
        # Уведомляем клиента о принятии заказа
        await bot.send_message(
            user_id,
            "✅ Заказ оформлен!\n\n"
            "Мы свяжемся с вами в ближайшее время для уточнения деталей доставки."
        )
        
        # Обновляем сообщение админа
        await callback_query.message.edit_text(
            callback_query.message.text + "\n\n✅ Заказ оформлен админом",
            reply_markup=None
        )
        
        await callback_query.answer("Заказ оформлен!")
        
    except Exception as e:
        logging.error(f"Ошибка при принятии заказа: {e}")
        await callback_query.answer("Ошибка при принятии заказа")

@dp.callback_query(lambda c: c.data.startswith("reject_order_"))
async def handle_reject_order(callback_query: CallbackQuery):
    """Обработка отклонения заказа админом"""
    if callback_query.from_user.id != ADMIN_CHAT_ID:
        await callback_query.answer("У вас нет прав для этого действия")
        return
    
    user_id = int(callback_query.data.split("_")[2])
    
    try:
        # Сбрасываем состояние пользователя
        from aiogram.fsm.context import FSMContext
        from aiogram.fsm.storage.base import StorageKey
        
        storage_key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
        state = FSMContext(storage=storage, key=storage_key)
        await state.clear()
        
        # Уведомляем клиента об отклонении заказа
        await bot.send_message(
            user_id,
            "❌ К сожалению, заказ не может быть оформлен.\n\n"
            "Попробуйте позже или свяжитесь с нами для уточнения деталей."
        )
        
        # Обновляем сообщение админа
        await callback_query.message.edit_text(
            callback_query.message.text + "\n\n❌ Заказ отклонен админом",
            reply_markup=None
        )
        
        await callback_query.answer("Заказ отклонен!")
        
    except Exception as e:
        logging.error(f"Ошибка при отклонении заказа: {e}")
        await callback_query.answer("Ошибка при отклонении заказа")

async def main():
    """Главная функция запуска бота"""
    try:
        # Удаляем webhook если он был установлен
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Запускаем polling
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    asyncio.run(main())
