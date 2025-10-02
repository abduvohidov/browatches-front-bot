import asyncio
import json
import logging
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
    waiting_for_confirmation = State()
    waiting_for_admin_approval = State()



# Бренды часов
WATCH_BRANDS = ["Rolex"]

# Модели часов по брендам с детальной информацией
WATCH_MODELS_BY_BRAND = {
    "Rolex": [
        {
            "name": "Rolex DayDate",
            "color": "Белый",
            "price": "220.000 uzs",
            "mechanism": "Батарейный механизм",
            "description": "Классические элегантные часы с отображением даты",
            "photo": "https://www.lenkersdorfer.com/upload/rolex_v7/product/landscape/upright_m128239-0005.webp",
            "detailed_info": "Rolex DayDate - это классические элегантные часы, сочетающие в себе стиль и функциональность. Первая в мире автоматическая модель с отображением даты. Корпус из нержавеющей стали 904L, сапфировое стекло, механизм Rolex 3235 с запасом хода 70 часов.",
            "photos": ["https://www.lenkersdorfer.com/upload/rolex_v7/product/landscape/upright_m128239-0005.webp"  ],
            "brand": "Rolex",
            "category": "Классические",
            "material": "Нержавеющая сталь 904L",
            "water_resistance": "Незащищенный",
        },
        {
            "name": "Rolex Oyster Perpetual",
            "color": "Белый",
            "price": "220.000 uzs",
            "mechanism": "Батарейный механизм",
            "description": "Классические элегантные часы с отображением даты",
            "photo": "https://privilegia.uz/wp-content/uploads/2020/06/m114300-0004-e1593514972475.png",
            "detailed_info": "Rolex DayDate - это классические элегантные часы, сочетающие в себе стиль и функциональность. Первая в мире автоматическая модель с отображением даты. Корпус из нержавеющей стали 904L, сапфировое стекло, механизм Rolex 3235 с запасом хода 70 часов.",
            "photos": ["https://privilegia.uz/wp-content/uploads/2020/06/m114300-0004-e1593514972475.png"],
            "brand": "Rolex",
            "category": "Классические",
            "material": "Нержавеющая сталь 904L",
            "water_resistance": "Незащищенный",
        },
        {
            "name": "Rolex Oyster Perpetual",
            "color": "Цифиный",
            "price": "220.000 uzs",
            "mechanism": "Батарейный механизм",
            "description": "Классические элегантные часы с отображением даты",
            "photo": "https://content.thewosgroup.com/productimage/17304444/17304444_1.png",
            "detailed_info": "Rolex DayDate - это классические элегантные часы, сочетающие в себе стиль и функциональность. Первая в мире автоматическая модель с отображением даты. Корпус из нержавеющей стали 904L, сапфировое стекло, механизм Rolex 3235 с запасом хода 70 часов.",
            "photos": ["https://content.thewosgroup.com/productimage/17304444/17304444_1.png"],
            "brand": "Rolex",
            "category": "Классические",
            "material": "Нержавеющая сталь 904L",
            "water_resistance": "Незащищенный",
        }
    ]
}

# Способы оплаты
PAYMENT_METHODS = ["Перевод на карту", "Оплата наличными"]


# Глобальная корзина пользователей (в реальном проекте лучше использовать базу данных)
user_carts = {}


# Отслеживание последних сообщений для редактирования
user_last_messages = {}

# Отслеживание ID сообщений карточек товаров для редактирования
user_product_cards = {}

# Функции для работы с корзиной
def get_user_cart(user_id: int) -> dict:
    """Получить корзину пользователя"""
    if user_id not in user_carts:
        user_carts[user_id] = {
            "items": []
        }
    return user_carts[user_id]

def add_to_cart(user_id: int, brand: str, model_index: int, quantity: int = 1):
    """Добавить товар в корзину"""
    cart = get_user_cart(user_id)
    model = WATCH_MODELS_BY_BRAND[brand][model_index]
    
    # Проверяем, есть ли уже такой товар в корзине
    for item in cart["items"]:
        if item["brand"] == brand and item["model_index"] == model_index:
            item["quantity"] += quantity
            return
    
    # Добавляем новый товар
    cart["items"].append({
        "brand": brand,
        "model_index": model_index,
        "name": model["name"],
        "price": model["price"],
        "photo": model["photo"],
        "color": model["color"],
        "quantity": quantity
    })

def remove_from_cart(user_id: int, brand: str, model_index: int):
    """Удалить товар из корзины"""
    cart = get_user_cart(user_id)
    cart["items"] = [item for item in cart["items"] 
                     if not (item["brand"] == brand and item["model_index"] == model_index)]

def update_cart_quantity(user_id: int, brand: str, model_index: int, quantity: int):
    """Обновить количество товара в корзине"""
    cart = get_user_cart(user_id)
    for item in cart["items"]:
        if item["brand"] == brand and item["model_index"] == model_index:
            if quantity <= 0:
                remove_from_cart(user_id, brand, model_index)
            else:
                item["quantity"] = quantity
            break

def clear_cart(user_id: int):
    """Очистить корзину"""
    user_carts[user_id] = {
        "items": []
    }

def calculate_cart_total(user_id: int) -> dict:
    """Рассчитать итоговую сумму корзины"""
    cart = get_user_cart(user_id)
    subtotal = 0
    
    for item in cart["items"]:
        # Извлекаем числовое значение цены (убираем символы валюты и запятые)
        price_str = item["price"].replace("₽", "").replace("uzs", "").replace(",", "").replace(" ", "").replace(".", "")
        try:
            price = int(price_str)
            subtotal += price * item["quantity"]
        except ValueError:
            continue
    
    return {
        "subtotal": subtotal,
        "total": subtotal
    }



# Функции для редактирования сообщений
async def edit_message_safe(message: types.Message, text: str = None, photo: str = None, 
                           reply_markup: InlineKeyboardMarkup = None, parse_mode: str = "HTML"):
    """Безопасное редактирование сообщения с обработкой ошибок"""
    user_id = message.from_user.id
    
    try:
        if photo:
            # Если есть фото, редактируем медиа
            await bot.edit_message_media(
                chat_id=message.chat.id,
                message_id=message.message_id,
                media=types.InputMediaPhoto(media=photo, caption=text, parse_mode=parse_mode),
                reply_markup=reply_markup
            )
        else:
            # Если нет фото, редактируем только текст
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        
        # Сохраняем ID сообщения для дальнейшего редактирования
        user_last_messages[user_id] = message.message_id
        return True
        
    except Exception as e:
        logging.warning(f"Не удалось отредактировать сообщение для пользователя {user_id}: {e}")
        # Если редактирование не удалось, отправляем новое сообщение
        try:
            if photo:
                new_message = await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=photo,
                    caption=text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
            else:
                new_message = await bot.send_message(
                    chat_id=message.chat.id,
                    text=text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
            user_last_messages[user_id] = new_message.message_id
            return True
        except Exception as e2:
            logging.error(f"Не удалось отправить новое сообщение для пользователя {user_id}: {e2}")
            return False

async def send_or_edit_message(message: types.Message, text: str = None, photo: str = None,
                               reply_markup: InlineKeyboardMarkup = None, parse_mode: str = "HTML"):
    """Отправить новое сообщение или отредактировать существующее"""
    user_id = message.from_user.id
    
    # Если есть сохраненное сообщение, пытаемся его отредактировать
    if user_id in user_last_messages:
        try:
            # Получаем сообщение по ID
            chat_id = message.chat.id
            message_id = user_last_messages[user_id]
            
            # Создаем объект сообщения для редактирования
            message_to_edit = types.Message(
                message_id=message_id,
                chat=message.chat,
                from_user=message.from_user,
                date=message.date
            )
            
            success = await edit_message_safe(message_to_edit, text, photo, reply_markup, parse_mode)
            if success:
                return
        except Exception as e:
            logging.warning(f"Не удалось отредактировать сообщение {user_id}: {e}")
    
    # Если редактирование не удалось, отправляем новое сообщение
    try:
        if photo:
            # Проверяем URL фото перед отправкой
            if photo.startswith('http'):
                try:
                    new_message = await bot.send_photo(
                        chat_id=message.chat.id,
                        photo=photo,
                        caption=text,
                        parse_mode=parse_mode,
                        reply_markup=reply_markup
                    )
                except Exception as photo_error:
                    logging.warning(f"Не удалось отправить фото {photo}: {photo_error}")
                    # Отправляем только текст без фото
                    new_message = await bot.send_message(
                        chat_id=message.chat.id,
                        text=text,
                        parse_mode=parse_mode,
                        reply_markup=reply_markup
                    )
            else:
                # Если это не URL, отправляем как файл
                new_message = await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=types.FSInputFile(photo),
                    caption=text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
        else:
            new_message = await bot.send_message(
                chat_id=message.chat.id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        user_last_messages[user_id] = new_message.message_id
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение для пользователя {user_id}: {e}")
        # В крайнем случае отправляем только текст
        try:
            new_message = await bot.send_message(
                chat_id=message.chat.id,
                text=text or "Произошла ошибка при загрузке контента",
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
            user_last_messages[user_id] = new_message.message_id
        except Exception as e2:
            logging.error(f"Критическая ошибка отправки сообщения: {e2}")

# Функция поиска товаров
def search_products(query: str) -> list:
    """Поиск товаров по запросу"""
    query = query.lower().strip()
    results = []
    
    for brand, models in WATCH_MODELS_BY_BRAND.items():
        for i, model in enumerate(models):
            # Поиск по бренду
            if query in brand.lower():
                results.append((brand, i, model))
                continue
            
            # Поиск по названию модели
            if query in model["name"].lower():
                results.append((brand, i, model))
                continue
            
            # Поиск по описанию
            if query in model["description"].lower():
                results.append((brand, i, model))
                continue
    
    return results


async def show_cart(message: types.Message):
    """Отображение корзины пользователя"""
    user_id = message.from_user.id
    cart = get_user_cart(user_id)
    
    if not cart["items"]:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⌚ Каталог"), KeyboardButton(text="🛒 Корзина")]
            ],
            resize_keyboard=True,
            persistent=True
        )
        
        await send_or_edit_message(
            message,
            "🛒 <b>Ваша корзина пуста</b>\n\n"
            "Добавьте товары из каталога, чтобы оформить заказ.",
            reply_markup=keyboard
        )
        return
    
    # Формируем сообщение с товарами в корзине
    cart_text = "🛒 <b>Ваша корзина</b>\n\n"
    
    for i, item in enumerate(cart["items"]):
        cart_text += f"<b>{i+1}. {item['brand']} {item['name']}</b>\n"
        cart_text += f"🎨 <b>Цвет:</b> {item['color']}\n"
        cart_text += f"💰 Цена: {item['price']}\n"
        cart_text += f"📦 Количество: {item['quantity']}\n\n"
    
    # Рассчитываем итоговую сумму
    totals = calculate_cart_total(user_id)
    cart_text += f"💳 <b>К оплате: {totals['total']:,} uzs</b>\n"
    
    # Создаем клавиатуру для управления корзиной
    keyboard_buttons = []
    
    # Кнопки для каждого товара
    for i, item in enumerate(cart["items"]):
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"✏️ {item['name'][:15]}... (x{item['quantity']})", 
                callback_data=f"edit_item_{item['brand']}_{item['model_index']}"
            )
        ])
    
    # Основные кнопки управления корзиной
    keyboard_buttons.extend([
        [InlineKeyboardButton(text="💳 Оформить заказ", callback_data="checkout_cart")],
        [InlineKeyboardButton(text="🗑️ Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton(text="⌚ Назад в каталог", callback_data="back_to_catalog")]
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await send_or_edit_message(
        message,
        cart_text,
        reply_markup=keyboard
    )

# Функция для создания карточки товара
async def send_product_card(message: types.Message, brand: str, model_index: int, show_navigation: bool = True, edit_existing: bool = False):
    """Отправляет детальную карточку товара с несколькими фото и характеристиками"""
    model = WATCH_MODELS_BY_BRAND[brand][model_index]
    models = WATCH_MODELS_BY_BRAND[brand]
    
    # Создаем inline клавиатуру с кнопками действий
    keyboard_buttons = [
        [InlineKeyboardButton(text="🛒 Добавить в корзину", callback_data=f"add_to_cart_{brand}_{model_index}")]
    ]
    
    # Добавляем кнопки навигации только если товаров больше одного и включена навигация
    if show_navigation and len(models) > 1:
        keyboard_buttons.append([
            InlineKeyboardButton(text="⬅️", callback_data=f"prev_detail_{brand}_{model_index}"), 
            InlineKeyboardButton(text="➡️", callback_data=f"next_detail_{brand}_{model_index}")
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⌚ Назад в каталог", callback_data="back_to_catalog")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    # Формируем текст с характеристиками
    card_text = f"""
🕰️ <b>{model['brand']} {model['name']}</b>

💰 <b>Цена:</b> {model['price']}
🎨 <b>Цвет:</b> {model['color']}
⚙️ <b>Механизм:</b> {model['mechanism']}

📋 <b>Характеристики:</b>
🏷️ <b>Бренд:</b> {model['brand']}
🔧 <b>Материал:</b> {model['material']}
💧 <b>Водозащита:</b> {model['water_resistance']}

📝 <b>Описание:</b>
{model['detailed_info']}
    """
    
    # Если нужно редактировать существующее сообщение
    if edit_existing:
        try:
            # Пытаемся отредактировать существующее сообщение
            if model["photos"][0].startswith('http'):
                await bot.edit_message_media(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    media=types.InputMediaPhoto(media=model["photos"][0], caption=card_text, parse_mode="HTML"),
                    reply_markup=keyboard
                )
            else:
                await bot.edit_message_media(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    media=types.InputMediaPhoto(media=types.FSInputFile(model["photos"][0]), caption=card_text, parse_mode="HTML"),
                    reply_markup=keyboard
                )
            return
        except Exception as edit_error:
            logging.warning(f"Не удалось отредактировать сообщение: {edit_error}")
            # Если редактирование не удалось, отправляем новое сообщение
    
    # Отправляем новое сообщение с фото
    try:
        if model["photos"][0].startswith('http'):
            new_message = await bot.send_photo(
                chat_id=message.chat.id,
                photo=model["photos"][0],
                caption=card_text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        else:
            new_message = await bot.send_photo(
                chat_id=message.chat.id,
                photo=types.FSInputFile(model["photos"][0]),
                caption=card_text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        
        # Сохраняем ID сообщения для дальнейшего редактирования
        user_product_cards[message.from_user.id] = new_message.message_id
        
    except Exception as photo_error:
        logging.warning(f"Не удалось отправить фото {model['photos'][0]}: {photo_error}")
        # Если фото не отправилось, отправляем только текст
        new_message = await bot.send_message(
            chat_id=message.chat.id,
            text=card_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        # Сохраняем ID сообщения для дальнейшего редактирования
        user_product_cards[message.from_user.id] = new_message.message_id

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обработчик команды /start"""
    # Создаем reply keyboard с основными кнопками меню
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⌚ Каталог"), KeyboardButton(text="🛒 Корзина")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    # Красивое приветственное сообщение с логотипом
    welcome_text = """👋 Привет! Добро пожаловать в наш бот-магазин часов.

Здесь вы можете:
⌚ Посмотреть каталог часов
🛒 Оформить заказ прямо в боте
📞 Связаться с продавцом для вопросов
    """
    
    # Отправляем фото логотипа CSC
    try:
        await message.answer_photo(
            photo=types.FSInputFile("images/CSCLogo.jpg"),
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
@dp.message(lambda message: message.text == "⌚ Каталог")
async def catalog_menu(message: types.Message):
    """Обработчик кнопки Каталог"""
    # Создаем reply keyboard с брендами
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Rolex")],
            [KeyboardButton(text="🔙 Назад на главную")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await send_or_edit_message(
        message,
        "Выберите бренд для просмотра товаров:",
        reply_markup=keyboard
    )


@dp.message(lambda message: message.text == "🛒 Корзина")
async def cart_menu(message: types.Message):
    """Обработчик кнопки Корзина"""
    await show_cart(message)

# Обработчики выбора брендов
@dp.message(lambda message: message.text in ["Rolex"])
async def handle_brand_selection(message: types.Message):
    """Обработка выбора бренда"""
    brand = message.text
    models = WATCH_MODELS_BY_BRAND[brand]
    
    # Показываем первый товар бренда
    if models:
        model = models[0]
        # Создаем inline клавиатуру с кнопками навигации
        keyboard_buttons = [
            [InlineKeyboardButton(text="🛒 Добавить в корзину", callback_data=f"add_to_cart_{brand}_0")],
            [InlineKeyboardButton(text="📖 Подробнее", callback_data=f"product_detail_{brand}_0")]
        ]
        
        # Добавляем кнопки навигации только если товаров больше одного
        if len(models) > 1:
            keyboard_buttons.append([
                InlineKeyboardButton(text="⬅️", callback_data=f"prev_product_{brand}_0"), 
                InlineKeyboardButton(text="➡️", callback_data=f"next_product_{brand}_0")
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="⌚ Назад в каталог", callback_data="back_to_catalog")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
        # Формируем текст карточки
        card_text = f"""
🕰️ <b>{model['brand']} {model['name']}</b>

💰 <b>Цена:</b> {model['price']}
🎨 <b>Цвет:</b> {model['color']}
⚙️ <b>Механизм:</b> {model['mechanism']}
📝 <b>Описание:</b> {model['description']}

📄 <b>Товар 1 из {len(models)}</b>
        """
        
        # Отправляем или редактируем сообщение с фото
        await send_or_edit_message(
            message,
            text=card_text,
            photo=model["photo"],
        reply_markup=keyboard
    )

# Обработчик кнопки "Назад на главную"
@dp.message(lambda message: message.text == "🔙 Назад на главную")
async def back_to_main_menu(message: types.Message):
    """Возврат в главное меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⌚ Каталог"), KeyboardButton(text="🛒 Корзина")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await send_or_edit_message(
        message,
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите нужный раздел:",
        reply_markup=keyboard
    )







# Обработчик "Добавить в корзину"
@dp.callback_query(lambda c: c.data.startswith("add_to_cart_"))
async def handle_add_to_cart(callback_query: CallbackQuery):
    """Обработка добавления товара в корзину"""
    await callback_query.answer("✅ Товар добавлен в корзину!")
    
    parts = callback_query.data.split("_")
    brand = parts[3]
    model_index = int(parts[4])
    model = WATCH_MODELS_BY_BRAND[brand][model_index]
    
    # Добавляем товар в корзину
    add_to_cart(callback_query.from_user.id, brand, model_index, 1)
    
    # Обновляем кнопку, показывая что товар добавлен
    keyboard_buttons = [
        [InlineKeyboardButton(text="✅ Добавлено в корзину", callback_data="noop")],
        [InlineKeyboardButton(text="📖 Подробнее", callback_data=f"product_detail_{brand}_{model_index}")]
    ]
    
    # Добавляем кнопки навигации только если товаров больше одного
    models = WATCH_MODELS_BY_BRAND[brand]
    if len(models) > 1:
        keyboard_buttons.append([
            InlineKeyboardButton(text="⬅️", callback_data=f"prev_product_{brand}_{model_index}"), 
            InlineKeyboardButton(text="➡️", callback_data=f"next_product_{brand}_{model_index}")
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⌚ Назад в каталог", callback_data="back_to_catalog")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    # Обновляем сообщение
    try:
        await callback_query.message.edit_reply_markup(reply_markup=keyboard)
    except Exception as e:
        logging.warning(f"Не удалось обновить клавиатуру: {e}")


# Обработчик "Назад в каталог"
@dp.callback_query(lambda c: c.data == "back_to_catalog")
async def handle_back_to_catalog(callback_query: CallbackQuery):
    """Обработка возврата в каталог"""
    await callback_query.answer()
    
    # Создаем reply keyboard с брендами
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Rolex")],
            [KeyboardButton(text="🔙 Назад на главную")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    # Используем callback_query.message напрямую для редактирования
    try:
        await callback_query.message.edit_text(
            "Выберите бренд для просмотра товаров:",
            reply_markup=None
        )
        
        # Отправляем новое сообщение с клавиатурой
        await callback_query.message.answer(
            "Выберите бренд для просмотра товаров:",
            reply_markup=keyboard
        )
    except Exception as e:
        logging.warning(f"Не удалось отредактировать сообщение: {e}")
        # Если редактирование не удалось, отправляем новое сообщение
        await callback_query.message.answer(
            "Выберите бренд для просмотра товаров:",
            reply_markup=keyboard
        )

# Обработчик навигации по товарам
@dp.callback_query(lambda c: c.data.startswith("next_product_") or c.data.startswith("prev_product_"))
async def handle_product_navigation(callback_query: CallbackQuery):
    """Обработка навигации по товарам"""
    await callback_query.answer()
    
    parts = callback_query.data.split("_")
    direction = parts[0]  # "next" или "prev"
    brand = parts[2]
    current_index = int(parts[3])
    models = WATCH_MODELS_BY_BRAND[brand]
    
    # Вычисляем новый индекс
    if direction == "next":
        new_index = (current_index + 1) % len(models)
    else:  # prev
        new_index = (current_index - 1) % len(models)
    
    model = models[new_index]
    
    # Создаем клавиатуру для нового товара
    keyboard_buttons = [
        [InlineKeyboardButton(text="🛒 Добавить в корзину", callback_data=f"add_to_cart_{brand}_{new_index}")],
        [InlineKeyboardButton(text="📖 Подробнее", callback_data=f"product_detail_{brand}_{new_index}")]
    ]
    
    # Добавляем кнопки навигации только если товаров больше одного
    if len(models) > 1:
        keyboard_buttons.append([
            InlineKeyboardButton(text="⬅️", callback_data=f"prev_product_{brand}_{new_index}"), 
            InlineKeyboardButton(text="➡️", callback_data=f"next_product_{brand}_{new_index}")
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⌚ Назад в каталог", callback_data="back_to_catalog")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    # Формируем текст карточки
    card_text = f"""
🕰️ <b>{model['brand']} {model['name']}</b>

💰 <b>Цена:</b> {model['price']}
🎨 <b>Цвет:</b> {model['color']}
⚙️ <b>Механизм:</b> {model['mechanism']}
📝 <b>Описание:</b> {model['description']}

📄 <b>Товар {new_index + 1} из {len(models)}</b>
    """
    
    # Пытаемся отредактировать существующее сообщение
    try:
        if model["photo"].startswith('http'):
            await bot.edit_message_media(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                media=types.InputMediaPhoto(media=model["photo"], caption=card_text, parse_mode="HTML"),
                reply_markup=keyboard
            )
        else:
            await bot.edit_message_media(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                media=types.InputMediaPhoto(media=types.FSInputFile(model["photo"]), caption=card_text, parse_mode="HTML"),
                reply_markup=keyboard
            )
    except Exception as edit_error:
        logging.warning(f"Не удалось отредактировать сообщение: {edit_error}")
        # Если редактирование не удалось, отправляем новое сообщение
        try:
            if model["photo"].startswith('http'):
                new_message = await bot.send_photo(
                    chat_id=callback_query.message.chat.id,
                    photo=model["photo"],
                    caption=card_text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            else:
                new_message = await bot.send_photo(
                    chat_id=callback_query.message.chat.id,
                    photo=types.FSInputFile(model["photo"]),
                    caption=card_text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            
            # Сохраняем ID нового сообщения
            user_product_cards[callback_query.from_user.id] = new_message.message_id
            
        except Exception as photo_error:
            logging.warning(f"Не удалось отправить фото {model['photo']}: {photo_error}")
            # Если фото не отправилось, отправляем только текст
            new_message = await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text=card_text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            
            # Сохраняем ID нового сообщения
            user_product_cards[callback_query.from_user.id] = new_message.message_id

# Обработчик навигации в детальном просмотре товара
@dp.callback_query(lambda c: c.data.startswith("next_detail_") or c.data.startswith("prev_detail_"))
async def handle_detail_navigation(callback_query: CallbackQuery):
    """Обработка навигации в детальном просмотре товара"""
    await callback_query.answer()
    
    parts = callback_query.data.split("_")
    direction = parts[0]  # "next" или "prev"
    brand = parts[2]
    current_index = int(parts[3])
    models = WATCH_MODELS_BY_BRAND[brand]
    
    # Вычисляем новый индекс
    if direction == "next":
        new_index = (current_index + 1) % len(models)
    else:  # prev
        new_index = (current_index - 1) % len(models)
    
    # Создаем объект сообщения для редактирования существующей карточки
    message = types.Message(
        message_id=callback_query.message.message_id,
        chat=callback_query.message.chat,
        from_user=callback_query.from_user,
        date=callback_query.message.date
    )
    
    # Показываем детальную карточку нового товара (редактируем существующее сообщение)
    await send_product_card(message, brand, new_index, show_navigation=True, edit_existing=True)

# Обработчик детального просмотра товара
@dp.callback_query(lambda c: c.data.startswith("product_detail_"))
async def handle_product_detail(callback_query: CallbackQuery):
    """Обработка детального просмотра товара"""
    await callback_query.answer()
    
    parts = callback_query.data.split("_")
    brand = parts[2]
    model_index = int(parts[3])
    
    # Создаем объект сообщения для отправки новой карточки
    message = types.Message(
        message_id=callback_query.message.message_id,
        chat=callback_query.message.chat,
        from_user=callback_query.from_user,
        date=callback_query.message.date
    )
    
    # Показываем детальную карточку товара с навигацией (отправляем новое сообщение)
    await send_product_card(message, brand, model_index, show_navigation=True)




@dp.message(Command("admin"))
async def admin_command(message: types.Message):
    """Команда для админа - просмотр статистики"""
    if message.from_user.id == ADMIN_CHAT_ID:
        await message.answer("Админ панель:\n/orders - просмотр заказов")
    else:
        await message.answer("У вас нет прав доступа")

async def send_order_to_admin(user_id: int, order_data: dict):
    """Отправка заказа администратору"""
    try:
        # Логируем отправку заказа администратору
        logging.info(f"Отправка заказа администратору от пользователя {user_id}")
        
        # Формируем детальное сообщение для админа
        admin_message = f"🛒 <b>НОВЫЙ ЗАКАЗ ОТ КЛИЕНТА</b>\n\n"
        admin_message += f"📅 <b>Дата заказа:</b> {order_data.get('order_date', 'Не указано')}\n"
        admin_message += f"👤 <b>Клиент:</b> {order_data.get('name', 'Не указано')}\n"
        admin_message += f"📞 <b>Телефон:</b> {order_data.get('phone', 'Не указано')}\n"
        admin_message += f"📍 <b>Локация:</b> {order_data.get('location', 'Не указано')}\n"
        admin_message += f"🆔 <b>ID пользователя:</b> {user_id}\n"
        admin_message += f"👤 <b>Username:</b> @{order_data.get('username', 'Не указано')}\n\n"
        
        # Добавляем детальную информацию о товарах
        cart_items = order_data.get('cart_items', [])
        admin_message += f"📦 <b>Товары в заказе ({len(cart_items)} шт.):</b>\n"
        total_price = 0
        
        for i, item in enumerate(cart_items, 1):
            # Получаем полную информацию о товаре
            brand = item['brand']
            model_index = item['model_index']
            model = WATCH_MODELS_BY_BRAND[brand][model_index]
            
            admin_message += f"\n{i}. <b>{item['brand']} {item['name']}</b>\n"
            admin_message += f"   💰 Цена: {item['price']}\n"
            admin_message += f"   📦 Количество: {item['quantity']}\n"
            admin_message += f"   🎨 Цвет: {item['color']}\n"
            admin_message += f"   ⚙️ Механизм: {model['mechanism']}\n"
            admin_message += f"   🔧 Материал: {model['material']}\n"
            admin_message += f"   💧 Водозащита: {model['water_resistance']}\n"
            
            # Рассчитываем общую стоимость
            price_str = item['price'].replace("₽", "").replace("uzs", "").replace(",", "").replace(" ", "").replace(".", "")
            try:
                price = int(price_str)
                total_price += price * item['quantity']
            except ValueError:
                continue
        
        admin_message += f"\n💳 <b>Общая стоимость: {total_price:,} uzs</b>\n"
        admin_message += f"📊 <b>Статус:</b> Ожидает модерации\n\n"
        admin_message += f"⚠️ <b>Требуется действие:</b> Принять или отклонить заказ"
        
        # Создаем клавиатуру для админа
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять заказ", callback_data=f"accept_order_{user_id}"),
                InlineKeyboardButton(text="❌ Отклонить заказ", callback_data=f"reject_order_{user_id}")
            ],
            [InlineKeyboardButton(text="📞 Связаться с клиентом", callback_data=f"contact_client_{user_id}")]
        ])
        
        # Отправляем сообщение с фото первого товара (если есть)
        if cart_items:
            first_item = cart_items[0]
            brand = first_item['brand']
            model_index = first_item['model_index']
            model = WATCH_MODELS_BY_BRAND[brand][model_index] 
            
            try:
                await bot.send_photo(
                    ADMIN_CHAT_ID,
                    photo=model['photo'],
                    caption=admin_message,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logging.info(f"Заказ с фото отправлен администратору от пользователя {user_id}")
            except Exception as photo_error:
                logging.warning(f"Не удалось отправить фото: {photo_error}")
                # Если фото не отправилось, отправляем только текст
                await bot.send_message(
                    ADMIN_CHAT_ID,
                    admin_message,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                logging.info(f"Заказ без фото отправлен администратору от пользователя {user_id}")
        else:
            # Если нет товаров в корзине, отправляем только текст
            await bot.send_message(
                ADMIN_CHAT_ID,
                admin_message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            logging.info(f"Заказ без товаров отправлен администратору от пользователя {user_id}")

        logging.info(f"Заказ успешно отправлен администратору: {order_data}")
        
    except Exception as e:
        logging.error(f"Ошибка при отправке заказа администратору: {e}")
        raise e  # Пробрасываем ошибку для обработки в вызывающем коде

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
        
        # Получаем корзину пользователя
        cart = get_user_cart(message.from_user.id)
        cart_items = cart.get('items', [])
        
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
            'cart_items': cart_items,
            'watch_model': 'Не указано',
            'payment_method': 'Не указано'
        }
        
        # Отправляем локацию админу
        await bot.send_location(
            ADMIN_CHAT_ID,
            latitude=latitude,
            longitude=longitude
        )
        
        # Формируем детальное сообщение для админа
        admin_message = f"📍 <b>Получена геолокация от клиента!</b>\n\n"
        admin_message += f"👤 <b>Клиент:</b> {order_data['name']}\n"
        admin_message += f"🆔 <b>ID пользователя:</b> {message.from_user.id}\n"
        admin_message += f"📍 <b>Локация:</b> {latitude}, {longitude}\n\n"
        
        # Добавляем информацию о товарах в корзине
        if cart_items:
            admin_message += f"📦 <b>Товары в корзине:</b>\n"
            total_price = 0
            
            for i, item in enumerate(cart_items, 1):
                # Получаем полную информацию о товаре
                brand = item['brand']
                model_index = item['model_index']
                model = WATCH_MODELS_BY_BRAND[brand][model_index]
                
                admin_message += f"{i}. <b>{item['brand']} {item['name']}</b>\n"
                admin_message += f"   💰 Цена: {item['price']}\n"
                admin_message += f"   📦 Количество: {item['quantity']}\n"
                admin_message += f"   ⚙️ Механизм: {model['mechanism']}\n"
                admin_message += f"   🔧 Материал: {model['material']}\n"
                admin_message += f"   💧 Водозащита: {model['water_resistance']}\n"
                
                # Рассчитываем общую стоимость
                price_str = item['price'].replace("₽", "").replace("uzs", "").replace(",", "").replace(" ", "").replace(".", "")
                try:
                    price = int(price_str)
                    total_price += price * item['quantity']
                except ValueError:
                    continue
            
            admin_message += f"💳 <b>Общая стоимость: {total_price:,} uzs</b>\n\n"
        else:
            admin_message += f"📦 <b>Корзина пуста</b>\n\n"
        
        admin_message += f"Оформить заказ или отклонить?"
        
        # Уведомляем админа с кнопками принятия/отклонения
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Оформить заказ", callback_data=f"accept_order_{message.from_user.id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_order_{message.from_user.id}")
            ]
        ])
        
        # Отправляем сообщение с фото первого товара (если есть)
        if cart_items:
            first_item = cart_items[0]
            brand = first_item['brand']
            model_index = first_item['model_index']
            model = WATCH_MODELS_BY_BRAND[brand][model_index]
            
            try:
                await bot.send_photo(
                    ADMIN_CHAT_ID,
                    photo=model['photo'],
                    caption=admin_message,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            except Exception as photo_error:
                logging.warning(f"Не удалось отправить фото: {photo_error}")
                # Если фото не отправилось, отправляем только текст
                await bot.send_message(
                    ADMIN_CHAT_ID,
                    admin_message,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
        else:
            # Если нет товаров в корзине, отправляем только текст
            await bot.send_message(
                ADMIN_CHAT_ID,
                admin_message,
                parse_mode="HTML",
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
        # Логируем принятие заказа
        logging.info(f"Администратор принял заказ от пользователя {user_id}")
        
        # Уведомляем клиента о принятии заказа
        await bot.send_message(
            user_id,
            "✅ <b>Ваш заказ принят!</b>\n\n"
            "🎉 <b>Статус:</b> Заказ подтвержден администратором\n"
            "📞 <b>Что дальше:</b>\n"
            "• Мы свяжемся с вами в ближайшее время\n"
            "• Уточним детали доставки\n"
            "• Согласуем время доставки\n\n"
            "Спасибо за покупку! 🛒",
            parse_mode="HTML"
        )
        
        # Обновляем сообщение админа
        await callback_query.message.edit_text(
            callback_query.message.text + "\n\n✅ <b>ЗАКАЗ ПРИНЯТ АДМИНИСТРАТОРОМ</b>\n"
            f"📅 Время принятия: {callback_query.message.date}\n"
            f"👤 Принял: {callback_query.from_user.first_name}",
            parse_mode="HTML",
            reply_markup=None
        )
        
        await callback_query.answer("✅ Заказ принят и клиент уведомлен!")
        
        logging.info(f"Заказ от пользователя {user_id} успешно принят администратором")
        
    except Exception as e:
        logging.error(f"Ошибка при принятии заказа: {e}")
        await callback_query.answer("❌ Ошибка при принятии заказа")

@dp.callback_query(lambda c: c.data.startswith("reject_order_"))
async def handle_reject_order(callback_query: CallbackQuery):
    """Обработка отклонения заказа админом"""
    if callback_query.from_user.id != ADMIN_CHAT_ID:
        await callback_query.answer("У вас нет прав для этого действия")
        return
    
    user_id = int(callback_query.data.split("_")[2])
    
    try:
        # Логируем отклонение заказа
        logging.info(f"Администратор отклонил заказ от пользователя {user_id}")
        
        # Сбрасываем состояние пользователя
        from aiogram.fsm.context import FSMContext
        from aiogram.fsm.storage.base import StorageKey
        
        storage_key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
        state = FSMContext(storage=storage, key=storage_key)
        await state.clear()
        
        # Уведомляем клиента об отклонении заказа
        await bot.send_message(
            user_id,
            "❌ <b>Заказ отклонен</b>\n\n"
            "😔 К сожалению, ваш заказ не может быть оформлен в данный момент.\n\n"
            "📞 <b>Что можно сделать:</b>\n"
            "• Свяжитесь с нами для уточнения деталей\n"
            "• Попробуйте оформить заказ позже\n"
            "• Выберите другие товары из каталога\n\n"
            "Извините за неудобства! 🙏",
            parse_mode="HTML"
        )
        
        # Обновляем сообщение админа
        await callback_query.message.edit_text(
            callback_query.message.text + "\n\n❌ <b>ЗАКАЗ ОТКЛОНЕН АДМИНИСТРАТОРОМ</b>\n"
            f"📅 Время отклонения: {callback_query.message.date}\n"
            f"👤 Отклонил: {callback_query.from_user.first_name}",
            parse_mode="HTML",
            reply_markup=None
        )
        
        await callback_query.answer("❌ Заказ отклонен и клиент уведомлен!")
        
        logging.info(f"Заказ от пользователя {user_id} отклонен администратором")
        
    except Exception as e:
        logging.error(f"Ошибка при отклонении заказа: {e}")
        await callback_query.answer("❌ Ошибка при отклонении заказа")

@dp.callback_query(lambda c: c.data.startswith("contact_client_"))
async def handle_contact_client(callback_query: CallbackQuery):
    """Обработка кнопки 'Связаться с клиентом'"""
    if callback_query.from_user.id != ADMIN_CHAT_ID:
        await callback_query.answer("У вас нет прав для этого действия")
        return
    
    user_id = int(callback_query.data.split("_")[2])
    
    try:
        # Логируем попытку связаться с клиентом
        logging.info(f"Администратор запросил связь с клиентом {user_id}")
        
        # Отправляем администратору информацию для связи
        contact_info = f"📞 <b>Связь с клиентом</b>\n\n"
        contact_info += f"🆔 <b>ID пользователя:</b> {user_id}\n"
        contact_info += f"👤 <b>Username:</b> @{callback_query.message.from_user.username if callback_query.message.from_user.username else 'Не указан'}\n"
        contact_info += f"📱 <b>Для связи:</b> @{callback_query.message.from_user.username if callback_query.message.from_user.username else 'Используйте ID'}\n\n"
        contact_info += f"💬 <b>Рекомендации:</b>\n"
        contact_info += f"• Напишите клиенту напрямую\n"
        contact_info += f"• Уточните детали заказа\n"
        contact_info += f"• Согласуйте время доставки\n\n"
        contact_info += f"⚠️ <b>Важно:</b> После связи обновите статус заказа!"
        
        # Создаем клавиатуру для обновления статуса
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Заказ подтвержден", callback_data=f"accept_order_{user_id}"),
                InlineKeyboardButton(text="❌ Заказ отклонен", callback_data=f"reject_order_{user_id}")
            ]
        ])
        
        await callback_query.message.answer(
            contact_info,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        await callback_query.answer("📞 Информация для связи отправлена!")
        
        logging.info(f"Информация для связи с клиентом {user_id} отправлена администратору")
        
    except Exception as e:
        logging.error(f"Ошибка при получении информации для связи: {e}")
        await callback_query.answer("❌ Ошибка при получении информации для связи")


@dp.callback_query(lambda c: c.data.startswith("edit_item_"))
async def handle_edit_item(callback_query: CallbackQuery):
    """Редактирование товара в корзине"""
    await callback_query.answer()
    
    parts = callback_query.data.split("_")
    brand = parts[2]
    model_index = int(parts[3])
    
    # Получаем информацию о товаре
    model = WATCH_MODELS_BY_BRAND[brand][model_index]
    cart = get_user_cart(callback_query.from_user.id)
    
    # Находим товар в корзине
    item = None
    for cart_item in cart["items"]:
        if cart_item["brand"] == brand and cart_item["model_index"] == model_index:
            item = cart_item
            break
    
    if not item:
        # Создаем объект сообщения для редактирования
        message = types.Message(
            message_id=callback_query.message.message_id,
            chat=callback_query.message.chat,
            from_user=callback_query.from_user,
            date=callback_query.message.date
        )
        
        await send_or_edit_message(
            message,
            "❌ Товар не найден в корзине"
        )
        return
    
    # Создаем клавиатуру для редактирования
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➖", callback_data=f"decrease_{brand}_{model_index}"),
            InlineKeyboardButton(text=f"📦 {item['quantity']}", callback_data="noop"),
            InlineKeyboardButton(text="➕", callback_data=f"increase_{brand}_{model_index}")
        ],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"remove_item_{brand}_{model_index}")],
        [InlineKeyboardButton(text="🔙 Назад в корзину", callback_data="back_to_cart")]
    ])
    
    # Создаем объект сообщения для редактирования
    message = types.Message(
        message_id=callback_query.message.message_id,
        chat=callback_query.message.chat,
        from_user=callback_query.from_user,
        date=callback_query.message.date
    )
    
    await send_or_edit_message(
        message,
        f"✏️ <b>Редактирование товара</b>\n\n"
        f"⌚ {model['brand']} {model['name']}\n"
        f"💰 Цена: {model['price']}\n"
        f"📦 Количество: {item['quantity']}\n\n"
        f"Используйте кнопки для изменения количества:",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data.startswith("increase_"))
async def handle_increase_quantity(callback_query: CallbackQuery):
    """Увеличить количество товара"""
    await callback_query.answer("✅ Количество увеличено!")
    
    parts = callback_query.data.split("_")
    brand = parts[1]
    model_index = int(parts[2])
    
    cart = get_user_cart(callback_query.from_user.id)
    for item in cart["items"]:
        if item["brand"] == brand and item["model_index"] == model_index:
            item["quantity"] += 1
            break
    
    # Создаем объект сообщения для редактирования
    message = types.Message(
        message_id=callback_query.message.message_id,
        chat=callback_query.message.chat,
        from_user=callback_query.from_user,
        date=callback_query.message.date
    )
    
    await show_cart(message)

@dp.callback_query(lambda c: c.data.startswith("decrease_"))
async def handle_decrease_quantity(callback_query: CallbackQuery):
    """Уменьшить количество товара"""
    await callback_query.answer("✅ Количество уменьшено!")
    
    parts = callback_query.data.split("_")
    brand = parts[1]
    model_index = int(parts[2])
    
    update_cart_quantity(callback_query.from_user.id, brand, model_index, -1)
    
    # Создаем объект сообщения для редактирования
    message = types.Message(
        message_id=callback_query.message.message_id,
        chat=callback_query.message.chat,
        from_user=callback_query.from_user,
        date=callback_query.message.date
    )
    
    await show_cart(message)

@dp.callback_query(lambda c: c.data.startswith("remove_item_"))
async def handle_remove_item(callback_query: CallbackQuery):
    """Удаление товара из корзины"""
    await callback_query.answer("🗑️ Товар удален из корзины!")
    
    parts = callback_query.data.split("_")
    brand = parts[2]
    model_index = int(parts[3])
    
    # Удаляем товар из корзины
    remove_from_cart(callback_query.from_user.id, brand, model_index)
    
    # Создаем объект сообщения для редактирования
    message = types.Message(
        message_id=callback_query.message.message_id,
        chat=callback_query.message.chat,
        from_user=callback_query.from_user,
        date=callback_query.message.date
    )
    
    # Показываем обновленную корзину
    await show_cart(message)

@dp.callback_query(lambda c: c.data == "clear_cart")
async def handle_clear_cart(callback_query: CallbackQuery):
    """Очистка корзины"""
    await callback_query.answer("🗑️ Корзина очищена!")
    
    clear_cart(callback_query.from_user.id)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⌚ Каталог"), KeyboardButton(text="🛒 Корзина")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    # Создаем объект сообщения для редактирования
    message = types.Message(
        message_id=callback_query.message.message_id,
        chat=callback_query.message.chat,
        from_user=callback_query.from_user,
        date=callback_query.message.date
    )
    
    await send_or_edit_message(
        message,
        "🛒 <b>Корзина очищена</b>\n\n"
        "Добавьте товары из каталога, чтобы оформить заказ.",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "checkout_cart")
async def handle_checkout_cart(callback_query: CallbackQuery, state: FSMContext):
    """Оформление заказа из корзины"""
    await callback_query.answer()
    
    user_id = callback_query.from_user.id
    cart = get_user_cart(user_id)
    
    if not cart["items"]:
        await callback_query.message.answer("❌ Корзина пуста!")
        return
    
    # Сохраняем информацию о корзине в состоянии
    await state.update_data(cart_items=cart["items"])
    await state.set_state(OrderStates.waiting_for_name)
    
    # Показываем информацию о заказе
    totals = calculate_cart_total(user_id)
    
    order_text = "💳 <b>Оформление заказа</b>\n\n"
    order_text += f"📦 Товаров в корзине: {len(cart['items'])}\n"
    order_text += f"💰 К оплате: {totals['total']:,} uzs\n\n"
    order_text += "Для оформления заказа введите ваше имя:"
    
    await callback_query.message.answer(
        order_text,
        parse_mode="HTML"
    )

@dp.callback_query(lambda c: c.data == "back_to_cart")
async def handle_back_to_cart(callback_query: CallbackQuery):
    """Возврат в корзину"""
    await callback_query.answer()
    
    # Используем callback_query.message напрямую
    try:
        # Пытаемся отредактировать существующее сообщение
        await show_cart(callback_query.message)
    except Exception as e:
        logging.warning(f"Не удалось отредактировать сообщение: {e}")
        # Если редактирование не удалось, отправляем новое сообщение
        await callback_query.message.answer("Произошла ошибка при возврате в корзину")

# Обработчик для пустых callback-запросов
@dp.callback_query(lambda c: c.data == "noop")
async def handle_noop(callback_query: CallbackQuery):
    """Обработка пустых callback-запросов"""
    await callback_query.answer()

# Обработчики для оформления заказа
@dp.message(OrderStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Обработка ввода имени"""
    await state.update_data(name=message.text)
    await state.set_state(OrderStates.waiting_for_phone)
    
    await message.answer(
        f"✅ Имя сохранено: {message.text}\n\n"
        "Теперь введите ваш номер телефона:",
        parse_mode="HTML"
    )

@dp.message(OrderStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    """Обработка ввода телефона"""
    await state.update_data(phone=message.text)
    await state.set_state(OrderStates.waiting_for_location)
    
    # Создаем клавиатуру для отправки локации
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Отправить локацию", request_location=True)],
            [KeyboardButton(text="❌ Пропустить")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        f"✅ Телефон сохранен: {message.text}\n\n"
        "Теперь отправьте вашу локацию для доставки:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@dp.message(OrderStates.waiting_for_location)
async def process_location(message: types.Message, state: FSMContext):
    """Обработка ввода локации"""
    if message.text == "❌ Пропустить":
        await state.update_data(location="Не указано")
    else:
        await state.update_data(location=message.text)
    
    # Получаем все данные заказа
    order_data = await state.get_data()
    
    # Показываем сводку заказа и запрашиваем подтверждение
    await show_order_confirmation(message, state, order_data)

async def show_order_confirmation(message: types.Message, state: FSMContext, order_data: dict):
    """Показать сводку заказа и запросить подтверждение"""
    # Устанавливаем состояние ожидания подтверждения
    await state.set_state(OrderStates.waiting_for_confirmation)
    
    # Получаем данные корзины
    cart_items = order_data.get('cart_items', [])
    
    # Формируем сводку заказа
    confirmation_text = "🛒 <b>ПОДТВЕРЖДЕНИЕ ЗАКАЗА</b>\n\n"
    confirmation_text += "📋 <b>Ваши данные:</b>\n"
    confirmation_text += f"👤 <b>Имя:</b> {order_data.get('name', 'Не указано')}\n"
    confirmation_text += f"📞 <b>Телефон:</b> {order_data.get('phone', 'Не указано')}\n"
    confirmation_text += f"📍 <b>Локация:</b> {order_data.get('location', 'Не указано')}\n\n"
    
    confirmation_text += "⌚ <b>Товары в заказе:</b>\n"
    total_price = 0
    
    for i, item in enumerate(cart_items, 1):
        # Получаем полную информацию о товаре
        brand = item['brand']
        model_index = item['model_index']
        model = WATCH_MODELS_BY_BRAND[brand][model_index]
        
        confirmation_text += f"{i}. <b>{item['brand']} {item['name']}</b>\n"
        confirmation_text += f"   💰 Цена: {item['price']}\n"
        confirmation_text += f"   📦 Количество: {item['quantity']}\n"
        confirmation_text += f"   🎨 Цвет: {item['color']}\n"
        confirmation_text += f"   ⚙️ Механизм: {model['mechanism']}\n\n"
        
        # Рассчитываем общую стоимость
        price_str = item['price'].replace("₽", "").replace("uzs", "").replace(",", "").replace(" ", "").replace(".", "")
        try:
            price = int(price_str)
            total_price += price * item['quantity']
        except ValueError:
            continue
    
    confirmation_text += f"💳 <b>Общая стоимость: {total_price:,} uzs</b>\n\n"
    confirmation_text += "⚠️ <b>ВАЖНО:</b> После подтверждения заказ будет отправлен администратору для модерации.\n"
    confirmation_text += "❓ <b>Вы действительно хотите оформить заказ на часы?</b>\n\n"
    confirmation_text += "Нажмите 'Да, оформить заказ' для подтверждения или 'Отменить' для отмены."
    
    # Создаем клавиатуру с кнопками подтверждения
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, оформить заказ", callback_data="confirm_order"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_order")
        ]
    ])
    
    await message.answer(
        confirmation_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )

# Обработчики подтверждения заказа
@dp.callback_query(lambda c: c.data == "confirm_order")
async def handle_confirm_order(callback_query: CallbackQuery, state: FSMContext):
    """Обработка подтверждения заказа"""
    user_id = callback_query.from_user.id
    
    try:
        # Логируем начало процесса подтверждения
        logging.info(f"Пользователь {user_id} подтвердил заказ")
        
        # Получаем данные заказа
        order_data = await state.get_data()
        cart_items = order_data.get('cart_items', [])
        
        # Добавляем дату заказа
        from datetime import datetime
        order_data['order_date'] = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        # Дополнительная проверка данных заказа
        if not cart_items:
            await callback_query.answer("❌ Корзина пуста! Заказ не может быть оформлен.")
            logging.warning(f"Попытка оформить пустой заказ от пользователя {user_id}")
            return
        
        # Проверяем наличие обязательных данных
        if not order_data.get('name') or not order_data.get('phone'):
            await callback_query.answer("❌ Неполные данные! Пожалуйста, заполните все поля.")
            logging.warning(f"Неполные данные заказа от пользователя {user_id}: {order_data}")
            return
        
        # Логируем детали заказа
        logging.info(f"Детали заказа от пользователя {user_id}: {order_data}")
        
        await callback_query.answer("✅ Заказ подтвержден! Отправляем администратору...")
        
        # Отправляем заказ администратору
        await send_order_to_admin(user_id, order_data)
        
        # Очищаем корзину
        clear_cart(user_id)
        
        # Сбрасываем состояние
        await state.clear()
        
        # Возвращаем в главное меню
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⌚ Каталог"), KeyboardButton(text="🛒 Корзина")]
            ],
            resize_keyboard=True,
            persistent=True
        )
        
        await callback_query.message.answer(
            "✅ <b>Заказ успешно отправлен администратору!</b>\n\n"
            "📋 <b>Что дальше:</b>\n"
            "• Администратор рассмотрит ваш заказ\n"
            "• Вы получите уведомление о статусе заказа\n"
            "• Мы свяжемся с вами для уточнения деталей доставки\n\n"
            "Спасибо за покупку! 🛒",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        logging.info(f"Заказ от пользователя {user_id} успешно отправлен администратору")
        
    except Exception as e:
        logging.error(f"Ошибка при подтверждении заказа пользователя {user_id}: {e}")
        await callback_query.answer("❌ Произошла ошибка при оформлении заказа. Попробуйте позже.")
        
        # В случае ошибки возвращаем пользователя в главное меню
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⌚ Каталог"), KeyboardButton(text="🛒 Корзина")]
            ],
            resize_keyboard=True,
            persistent=True
        )
        
        await callback_query.message.answer(
            "❌ <b>Произошла ошибка при оформлении заказа</b>\n\n"
            "Пожалуйста, попробуйте позже или свяжитесь с нами для помощи.",
            parse_mode="HTML",
            reply_markup=keyboard
        )

@dp.callback_query(lambda c: c.data == "cancel_order")
async def handle_cancel_order(callback_query: CallbackQuery, state: FSMContext):
    """Обработка отмены заказа"""
    await callback_query.answer("❌ Заказ отменен")
    
    # Сбрасываем состояние
    await state.clear()
    
    # Возвращаем в главное меню
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⌚ Каталог"), KeyboardButton(text="🛒 Корзина")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await callback_query.message.answer(
        "❌ <b>Заказ отменен</b>\n\n"
        "Вы можете продолжить покупки в каталоге.",
        parse_mode="HTML",
        reply_markup=keyboard
    )

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
