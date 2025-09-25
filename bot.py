import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
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
    waiting_for_location = State()
    waiting_for_brand = State()
    waiting_for_watch_model = State()
    waiting_for_payment = State()
    waiting_for_admin_approval = State()

# Бренды часов
WATCH_BRANDS = ["Rolex", "Patek Philippe", "Tissot"]

# Модели часов по брендам с детальной информацией
WATCH_MODELS_BY_BRAND = {
    "Rolex": [
        {
            "name": "Submariner",
            "price": "₽2,500,000",
            "mechanism": "Автоматический механизм Rolex 3235",
            "description": "Легендарные дайверские часы с водонепроницаемостью до 300м",
            "photo": "https://images.unsplash.com/photo-1523170335258-f5b6c6e8e4c4?w=500&h=500&fit=crop",
            "detailed_info": "Rolex Submariner - это культовые дайверские часы, которые стали символом надежности и престижа. Корпус из нержавеющей стали 904L, сапфировое стекло, водонепроницаемость до 300 метров. Механизм Rolex 3235 с запасом хода 70 часов."
        },
        {
            "name": "GMT-Master II",
            "price": "₽2,800,000",
            "mechanism": "Автоматический механизм Rolex 3285",
            "description": "Часы для путешественников с функцией GMT",
            "photo": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&h=500&fit=crop",
            "detailed_info": "Rolex GMT-Master II - идеальные часы для путешественников. Позволяют отслеживать время в двух часовых поясах одновременно. Корпус из нержавеющей стали, керамический безель, водонепроницаемость до 100 метров."
        }
    ],
    "Patek Philippe": [
        {
            "name": "Calatrava",
            "price": "₽3,500,000",
            "mechanism": "Ручной завод механизм 324 S C",
            "description": "Элегантные классические часы из белого золота",
            "photo": "https://images.unsplash.com/photo-1594534475808-b18fc33b045e?w=500&h=500&fit=crop",
            "detailed_info": "Patek Philippe Calatrava - воплощение классической элегантности. Корпус из белого золота 18к, сапфировое стекло с антибликовым покрытием. Механизм ручного завода с запасом хода 45 часов. Символ престижа и изысканного вкуса."
        },
        {
            "name": "Nautilus",
            "price": "₽4,200,000",
            "mechanism": "Автоматический механизм 26-330 S C",
            "description": "Спортивные часы в стальном корпусе",
            "photo": "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=500&h=500&fit=crop",
            "detailed_info": "Patek Philippe Nautilus - спортивные часы с характерным дизайном в виде иллюминатора. Корпус из нержавеющей стали, водонепроницаемость до 120 метров. Автоматический механизм с запасом хода 45 часов."
        }
    ],
    "Tissot": [
        {
            "name": "Le Locle",
            "price": "₽45,000",
            "mechanism": "Автоматический механизм ETA 2824-2",
            "description": "Классические швейцарские часы с автоподзаводом",
            "photo": "https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?w=500&h=500&fit=crop",
            "detailed_info": "Tissot Le Locle - классические швейцарские часы с элегантным дизайном. Корпус из нержавеющей стали, сапфировое стекло, водонепроницаемость до 30 метров. Автоматический механизм ETA 2824-2 с запасом хода 38 часов."
        },
        {
            "name": "PRX",
            "price": "₽35,000",
            "mechanism": "Автоматический механизм Powermatic 80",
            "description": "Современные спортивные часы в стиле 70-х",
            "photo": "https://images.unsplash.com/photo-1523170335258-f5b6c6e8e4c4?w=500&h=500&fit=crop",
            "detailed_info": "Tissot PRX - современная интерпретация классических спортивных часов 70-х годов. Корпус из нержавеющей стали, интегрированный браслет, водонепроницаемость до 100 метров. Механизм Powermatic 80 с запасом хода 80 часов."
        }
    ]
}

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
    # Создаем reply keyboard с основными кнопками меню
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Оформить заказ")],
            [KeyboardButton(text="📚 Каталог"), KeyboardButton(text="🎯 Акции")],
            [KeyboardButton(text="📞 Контакты"), KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    # Красивое приветственное сообщение с логотипом
    welcome_text = """
🕰️ <b>BRO WATCHES</b> 🕰️

✨ <b>Добро пожаловать в мир премиальных часов!</b> ✨

Мы предлагаем эксклюзивную коллекцию швейцарских часов от ведущих брендов. Каждые часы - это произведение искусства, сочетающее в себе безупречное качество, элегантный дизайн и надежность.

🏆 <b>Наши преимущества:</b>
• Оригинальные швейцарские часы
• Гарантия подлинности
• Индивидуальный подход к каждому клиенту
• Быстрая доставка по всей России

Выберите раздел в меню ниже 👇
    """
    
    # Отправляем фото логотипа (используем красивое изображение часов)
    logo_url = "https://images.unsplash.com/photo-1523170335258-f5b6c6e8e4c4?w=500&h=500&fit=crop&crop=center"
    
    try:
        await message.answer_photo(
            photo=logo_url,
            caption=welcome_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception as e:
        # Если фото не загрузилось, отправляем только текст
        logging.warning(f"Не удалось загрузить логотип: {e}")
        await message.answer(
            welcome_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

# Обработчики для кнопок главного меню
@dp.message(lambda message: message.text == "📚 Каталог")
async def catalog_menu(message: types.Message):
    """Обработчик кнопки Каталог"""
    await message.answer("📚 Загружаю каталог часов...")
    
    # Отправляем все часы по брендам
    for brand, models in WATCH_MODELS_BY_BRAND.items():
        await message.answer(f"🏷️ **{brand}**", parse_mode="Markdown")
        
        for i, model in enumerate(models, 1):
            try:
                await message.answer_photo(
                    photo=model["photo"],
                    caption=f"**{i}. {brand} {model['name']}**\n\n"
                           f"💰 Цена: {model['price']}\n"
                           f"⚙️ Механизм: {model['mechanism']}\n"
                           f"📝 Описание: {model['description']}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                # Если фото не загрузилось, отправляем только текст
                logging.warning(f"Не удалось загрузить фото для {brand} {model['name']}: {e}")
                await message.answer(
                    f"**{i}. {brand} {model['name']}**\n\n"
                    f"💰 Цена: {model['price']}\n"
                    f"⚙️ Механизм: {model['mechanism']}\n"
                    f"📝 Описание: {model['description']}",
                    parse_mode="Markdown"
                )
        
        # Небольшая пауза между брендами
        await asyncio.sleep(0.5)
    
    # Добавляем reply кнопки для оформления заказа
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Оформить заказ")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await message.answer(
        "✅ Каталог загружен!\n\n"
        "Для оформления заказа нажмите кнопку ниже:",
        reply_markup=keyboard
    )

@dp.message(lambda message: message.text == "🎯 Акции")
async def promotions_menu(message: types.Message):
    """Обработчик кнопки Акции"""
    await message.answer(
        "🎯 <b>Акции и специальные предложения</b>\n\n"
        "🔥 <b>Скидка 15% на все модели Tissot</b>\n"
        "⏰ Действует до конца месяца\n\n"
        "💎 <b>Бесплатная доставка</b>\n"
        "🚚 При заказе от 100,000₽\n\n"
        "🎁 <b>Подарочная упаковка</b>\n"
        "🎀 При покупке любых часов\n\n"
        "Для оформления заказа используйте кнопку ниже 👇",
        parse_mode="HTML"
    )
    
    # Добавляем reply кнопку для оформления заказа
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Оформить заказ")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await message.answer(
        "Выберите действие:",
        reply_markup=keyboard
    )

@dp.message(lambda message: message.text == "📞 Контакты")
async def contacts_menu(message: types.Message):
    """Обработчик кнопки Контакты"""
    await message.answer(
        "📞 <b>Наши контакты</b>\n\n"
        "🕰️ <b>BRO WATCHES</b>\n\n"
        "📱 <b>Телефон:</b> +7 (999) 123-45-67\n"
        "📧 <b>Email:</b> info@browatches.ru\n"
        "🌐 <b>Сайт:</b> www.browatches.ru\n\n"
        "📍 <b>Адрес:</b>\n"
        "Москва, ул. Тверская, 15\n"
        "м. Тверская, выход 3\n\n"
        "🕒 <b>Режим работы:</b>\n"
        "Пн-Пт: 10:00 - 20:00\n"
        "Сб-Вс: 11:00 - 19:00\n\n"
        "💬 <b>Telegram:</b> @browatches_support",
        parse_mode="HTML"
    )
    
    # Добавляем reply кнопку для оформления заказа
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Оформить заказ")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await message.answer(
        "Готовы оформить заказ?",
        reply_markup=keyboard
    )

@dp.message(lambda message: message.text == "❓ Помощь")
async def help_menu(message: types.Message):
    """Обработчик кнопки Помощь"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Как оформить заказ", callback_data="help_order")],
        [InlineKeyboardButton(text="💳 Способы оплаты", callback_data="help_payment")],
        [InlineKeyboardButton(text="🚚 Доставка", callback_data="help_delivery")],
        [InlineKeyboardButton(text="🔒 Гарантии", callback_data="help_warranty")]
    ])
    
    await message.answer(
        "❓ <b>Помощь и поддержка</b>\n\n"
        "Выберите интересующий вас раздел:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "help_order")
async def help_order_callback(callback_query: CallbackQuery):
    """Помощь по оформлению заказа"""
    await callback_query.answer()
    await callback_query.message.answer(
        "📚 <b>Как оформить заказ</b>\n\n"
        "1️⃣ Нажмите кнопку 'Каталог'\n"
        "2️⃣ Выберите 'Оформить заказ'\n"
        "3️⃣ Укажите ваши данные\n"
        "4️⃣ Выберите модель часов\n"
        "5️⃣ Выберите способ оплаты\n"
        "6️⃣ Ожидайте подтверждения\n\n"
        "💡 <b>Совет:</b> Для быстрого заказа отправьте геолокацию!",
        parse_mode="HTML"
    )
    
    # Добавляем reply кнопку для оформления заказа
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Оформить заказ")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await callback_query.message.answer(
        "Готовы оформить заказ?",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "help_payment")
async def help_payment_callback(callback_query: CallbackQuery):
    """Помощь по способам оплаты"""
    await callback_query.answer()
    await callback_query.message.answer(
        "💳 <b>Способы оплаты</b>\n\n"
        "💰 <b>Наличные</b> - при получении\n"
        "💳 <b>Банковская карта</b> - онлайн\n"
        "🏦 <b>Перевод на карту</b> - СБП\n"
        "₿ <b>Криптовалюта</b> - Bitcoin, Ethereum\n\n"
        "🔒 Все платежи защищены и безопасны",
        parse_mode="HTML"
    )
    
    # Добавляем reply кнопку для оформления заказа
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Оформить заказ")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await callback_query.message.answer(
        "Готовы оформить заказ?",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "help_delivery")
async def help_delivery_callback(callback_query: CallbackQuery):
    """Помощь по доставке"""
    await callback_query.answer()
    await callback_query.message.answer(
        "🚚 <b>Доставка</b>\n\n"
        "📍 <b>По Москве:</b> 1-2 дня (бесплатно от 100,000₽)\n"
        "🇷🇺 <b>По России:</b> 3-7 дней (от 500₽)\n"
        "🌍 <b>Международная:</b> 7-14 дней (от 2,000₽)\n\n"
        "📦 <b>Упаковка:</b> Подарочная упаковка включена\n"
        "🔒 <b>Страховка:</b> Полная страховка груза\n"
        "📱 <b>Отслеживание:</b> SMS-уведомления",
        parse_mode="HTML"
    )
    
    # Добавляем reply кнопку для оформления заказа
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Оформить заказ")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await callback_query.message.answer(
        "Готовы оформить заказ?",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "help_warranty")
async def help_warranty_callback(callback_query: CallbackQuery):
    """Помощь по гарантиям"""
    await callback_query.answer()
    await callback_query.message.answer(
        "🔒 <b>Гарантии и сертификаты</b>\n\n"
        "✅ <b>Гарантия подлинности</b> - все часы оригинальные\n"
        "📜 <b>Сертификаты</b> - полный пакет документов\n"
        "🛡️ <b>Гарантия производителя</b> - от 2 лет\n"
        "🔧 <b>Сервисное обслуживание</b> - авторизованные центры\n\n"
        "💎 <b>Возврат и обмен:</b> 14 дней с момента покупки",
        parse_mode="HTML"
    )
    
    # Добавляем reply кнопку для оформления заказа
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Оформить заказ")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await callback_query.message.answer(
        "Готовы оформить заказ?",
        reply_markup=keyboard
    )

# Команда для возврата в главное меню
@dp.message(Command("menu"))
async def menu_command(message: types.Message):
    """Команда для возврата в главное меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Оформить заказ")],
            [KeyboardButton(text="📚 Каталог"), KeyboardButton(text="🎯 Акции")],
            [KeyboardButton(text="📞 Контакты"), KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await message.answer(
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите нужный раздел:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

# Обработчик для кнопки "Оформить заказ"
@dp.message(lambda message: message.text == "🛒 Оформить заказ")
async def start_order_from_button(message: types.Message, state: FSMContext):
    """Обработчик кнопки Оформить заказ"""
    await state.set_state(OrderStates.waiting_for_name)
    await message.answer(
        "🛒 <b>Оформление заказа</b>\n\n"
        "Введите ваше имя:",
        parse_mode="HTML"
    )

# Обработчик для возврата в меню
@dp.message(lambda message: message.text in ["🏠 Главное меню", "Назад", "Меню"])
async def back_to_menu(message: types.Message):
    """Возврат в главное меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Оформить заказ")],
            [KeyboardButton(text="📚 Каталог"), KeyboardButton(text="🎯 Акции")],
            [KeyboardButton(text="📞 Контакты"), KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await message.answer(
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите нужный раздел:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "view_catalog")
async def view_catalog_callback(callback_query: CallbackQuery):
    """Обработчик кнопки просмотра каталога"""
    await callback_query.answer()
    await callback_query.message.answer("📚 Загружаю каталог часов...")
    
    # Отправляем все часы по брендам
    for brand, models in WATCH_MODELS_BY_BRAND.items():
        await callback_query.message.answer(f"🏷️ **{brand}**", parse_mode="Markdown")
        
        for i, model in enumerate(models, 1):
            try:
                await callback_query.message.answer_photo(
                    photo=model["photo"],
                    caption=f"**{i}. {brand} {model['name']}**\n\n"
                           f"💰 Цена: {model['price']}\n"
                           f"⚙️ Механизм: {model['mechanism']}\n"
                           f"📝 Описание: {model['description']}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                # Если фото не загрузилось, отправляем только текст
                logging.warning(f"Не удалось загрузить фото для {brand} {model['name']}: {e}")
                await callback_query.message.answer(
                    f"**{i}. {brand} {model['name']}**\n\n"
                    f"💰 Цена: {model['price']}\n"
                    f"⚙️ Механизм: {model['mechanism']}\n"
                    f"📝 Описание: {model['description']}",
                    parse_mode="Markdown"
                )
        
        # Небольшая пауза между брендами
        await asyncio.sleep(0.5)
    
    await callback_query.message.answer("✅ Каталог загружен! Для заказа используйте команду /start")

@dp.callback_query(lambda c: c.data == "start_order")
async def start_order_callback(callback_query: CallbackQuery, state: FSMContext):
    """Начало оформления заказа"""
    await callback_query.answer()
    await state.set_state(OrderStates.waiting_for_name)
    await callback_query.message.answer(
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
    await state.set_state(OrderStates.waiting_for_location)
    
    # Создаем клавиатуру с кнопкой геолокации
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Отправить геолокацию", request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer("📍 Отправьте вашу геолокацию для доставки:", reply_markup=keyboard)

@dp.message(OrderStates.waiting_for_location)
async def process_location(message: types.Message, state: FSMContext):
    """Обработка геолокации"""
    if message.location:
        # Сохраняем координаты
        location_data = {
            'latitude': message.location.latitude,
            'longitude': message.location.longitude
        }
        await state.update_data(location=location_data)
        await state.set_state(OrderStates.waiting_for_brand)
        
        # Убираем клавиатуру
        await message.answer("✅ Геолокация получена!", reply_markup=types.ReplyKeyboardRemove())
        
        # Создаем reply клавиатуру с брендами часов
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Rolex")],
                [KeyboardButton(text="Patek Philippe")],
                [KeyboardButton(text="Tissot")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        
        await message.answer("Выберите бренд часов:", reply_markup=keyboard)
    else:
        await message.answer("❌ Пожалуйста, отправьте геолокацию, нажав на кнопку ниже.")

@dp.message(OrderStates.waiting_for_brand)
async def process_brand_selection(message: types.Message, state: FSMContext):
    """Обработка выбора бренда часов"""
    brand = message.text
    
    # Проверяем, что выбранный бренд существует
    if brand not in WATCH_BRANDS:
        await message.answer("❌ Пожалуйста, выберите бренд из предложенных вариантов.")
        return
    
    # Сохраняем выбранный бренд
    await state.update_data(selected_brand=brand)
    await state.set_state(OrderStates.waiting_for_watch_model)
    
    # Убираем клавиатуру
    await message.answer("✅ Бренд выбран!", reply_markup=types.ReplyKeyboardRemove())
    
    # Получаем модели выбранного бренда
    models = WATCH_MODELS_BY_BRAND[brand]
    
    # Отправляем каждую модель с фото и кнопкой выбора
    for i, model in enumerate(models):
        try:
            # Создаем клавиатуру с кнопкой "Выбрать"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Выбрать", callback_data=f"select_model_{brand}_{i}")]
            ])
            
            await message.answer_photo(
                photo=model["photo"],
                caption=f"⌚ {brand} {model['name']}\n\n"
                       f"💰 Цена: {model['price']}\n"
                       f"⚙️ Механизм: {model['mechanism']}\n"
                       f"📝 Описание: {model['description']}",
                reply_markup=keyboard
            )
        except Exception as e:
            # Если фото не загрузилось, отправляем только текст
            logging.warning(f"Не удалось загрузить фото для {brand} {model['name']}: {e}")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Выбрать", callback_data=f"select_model_{brand}_{i}")]
            ])
            
            await message.answer(
                f"⌚ {brand} {model['name']}\n\n"
                f"💰 Цена: {model['price']}\n"
                f"⚙️ Механизм: {model['mechanism']}\n"
                f"📝 Описание: {model['description']}",
                reply_markup=keyboard
            )

@dp.callback_query(lambda c: c.data.startswith("select_model_"))
async def process_model_selection(callback_query: CallbackQuery, state: FSMContext):
    """Обработка выбора конкретной модели часов"""
    await callback_query.answer()
    
    # Парсим данные из callback_data
    parts = callback_query.data.split("_")
    brand = parts[2]
    model_index = int(parts[3])
    
    # Получаем информацию о выбранной модели
    model = WATCH_MODELS_BY_BRAND[brand][model_index]
    full_model_name = f"{brand} {model['name']}"
    
    # Сохраняем выбранную модель
    await state.update_data(watch_model=full_model_name)
    await state.set_state(OrderStates.waiting_for_payment)
    
    # Отправляем детальную информацию о выбранной модели
    try:
        await callback_query.message.answer_photo(
            photo=model["photo"],
            caption=f"✅ Выбрана модель: {full_model_name}\n\n"
                   f"💰 Цена: {model['price']}\n"
                   f"⚙️ Механизм: {model['mechanism']}\n"
                   f"📝 Подробное описание: {model['detailed_info']}"
        )
    except Exception as e:
        logging.warning(f"Не удалось загрузить фото для {full_model_name}: {e}")
        await callback_query.message.answer(
            f"✅ Выбрана модель: {full_model_name}\n\n"
            f"💰 Цена: {model['price']}\n"
            f"⚙️ Механизм: {model['mechanism']}\n"
            f"📝 Подробное описание: {model['detailed_info']}"
        )
    
    # Создаем клавиатуру со способами оплаты
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=method, callback_data=f"payment_{i}")] 
        for i, method in enumerate(PAYMENT_METHODS)
    ])
    
    await callback_query.message.answer(
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

@dp.message(Command("catalog"))
async def catalog_command(message: types.Message):
    """Команда для просмотра каталога часов"""
    await message.answer("📚 Загружаю каталог часов...")
    
    # Отправляем все часы по брендам
    for brand, models in WATCH_MODELS_BY_BRAND.items():
        await message.answer(f"🏷️ **{brand}**", parse_mode="Markdown")
        
        for i, model in enumerate(models, 1):
            try:
                await message.answer_photo(
                    photo=model["photo"],
                    caption=f"**{i}. {brand} {model['name']}**\n\n"
                           f"💰 Цена: {model['price']}\n"
                           f"⚙️ Механизм: {model['mechanism']}\n"
                           f"📝 Описание: {model['description']}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                # Если фото не загрузилось, отправляем только текст
                logging.warning(f"Не удалось загрузить фото для {brand} {model['name']}: {e}")
                await message.answer(
                    f"**{i}. {brand} {model['name']}**\n\n"
                    f"💰 Цена: {model['price']}\n"
                    f"⚙️ Механизм: {model['mechanism']}\n"
                    f"📝 Описание: {model['description']}",
                    parse_mode="Markdown"
                )
        
        # Небольшая пауза между брендами
        await asyncio.sleep(0.5)
    
    await message.answer("✅ Каталог загружен! Для заказа используйте команду /start")

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
        
        # Формируем сообщение для админа
        admin_message = f"�� Новый заказ!\n\n"
        admin_message += f"👤 Клиент: {order_data.get('name', 'Не указано')}\n"
        admin_message += f"📞 Телефон: {order_data.get('phone', 'Не указано')}\n"
        
        # Добавляем информацию о геолокации
        if 'location' in order_data:
            location = order_data['location']
            admin_message += f"📍 Геолокация: {location['latitude']}, {location['longitude']}\n"
        else:
            admin_message += f"📍 Адрес: {order_data.get('address', 'Не указано')}\n"
            
        admin_message += f"⌚ Модель: {order_data.get('watch_model', 'Не указано')}\n"
        admin_message += f"💳 Оплата: {order_data.get('payment_method', 'Не указано')}\n"
        admin_message += f"🆔 ID пользователя: {user_id}"
        
        await bot.send_message(
            ADMIN_CHAT_ID,
            admin_message,
            reply_markup=keyboard
        )
        
        # Если есть геолокация, отправляем её админу
        if 'location' in order_data:
            location = order_data['location']
            await bot.send_location(
                ADMIN_CHAT_ID,
                latitude=location['latitude'],
                longitude=location['longitude']
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
            'location': {
                'latitude': latitude,
                'longitude': longitude
            },
            'watch_model': 'Не указано',
            'payment_method': 'Не указано'
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
