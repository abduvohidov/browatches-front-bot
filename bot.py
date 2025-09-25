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
    waiting_for_admin_approval = State()

# Состояния для корзины
class CartStates(StatesGroup):
    viewing_cart = State()
    editing_quantity = State()
    applying_promo = State()



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
            "detailed_info": "Rolex Submariner - это культовые дайверские часы, которые стали символом надежности и престижа. Корпус из нержавеющей стали 904L, сапфировое стекло, водонепроницаемость до 300 метров. Механизм Rolex 3235 с запасом хода 70 часов.",
            "photos": [
                "https://images.unsplash.com/photo-1523170335258-f5b6c6e8e4c4?w=500&h=500&fit=crop",
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&h=500&fit=crop",
                "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=500&h=500&fit=crop"
            ],
            "brand": "Rolex",
            "category": "Спортивные",
            "material": "Нержавеющая сталь 904L",
            "water_resistance": "300 метров",
            "warranty": "5 лет официальной гарантии"
        },
        {
            "name": "GMT-Master II",
            "price": "₽2,800,000",
            "mechanism": "Автоматический механизм Rolex 3285",
            "description": "Часы для путешественников с функцией GMT",
            "photo": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&h=500&fit=crop",
            "detailed_info": "Rolex GMT-Master II - идеальные часы для путешественников. Позволяют отслеживать время в двух часовых поясах одновременно. Корпус из нержавеющей стали, керамический безель, водонепроницаемость до 100 метров.",
            "photos": [
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&h=500&fit=crop",
                "https://images.unsplash.com/photo-1523170335258-f5b6c6e8e4c4?w=500&h=500&fit=crop",
                "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=500&h=500&fit=crop"
            ],
            "brand": "Rolex",
            "category": "Мужские",
            "material": "Нержавеющая сталь + керамический безель",
            "water_resistance": "100 метров",
            "warranty": "5 лет официальной гарантии"
        }
    ],
    "Patek Philippe": [
        {
            "name": "Calatrava",
            "price": "₽3,500,000",
            "mechanism": "Ручной завод механизм 324 S C",
            "description": "Элегантные классические часы из белого золота",
            "photo": "https://images.unsplash.com/photo-1594534475808-b18fc33b045e?w=500&h=500&fit=crop",
            "detailed_info": "Patek Philippe Calatrava - воплощение классической элегантности. Корпус из белого золота 18к, сапфировое стекло с антибликовым покрытием. Механизм ручного завода с запасом хода 45 часов. Символ престижа и изысканного вкуса.",
            "photos": [
                "https://images.unsplash.com/photo-1594534475808-b18fc33b045e?w=500&h=500&fit=crop",
                "https://images.unsplash.com/photo-1523170335258-f5b6c6e8e4c4?w=500&h=500&fit=crop",
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&h=500&fit=crop"
            ],
            "brand": "Patek Philippe",
            "category": "Унисекс",
            "material": "Белое золото 18к",
            "water_resistance": "30 метров",
            "warranty": "Пожизненная гарантия"
        },
        {
            "name": "Nautilus",
            "price": "₽4,200,000",
            "mechanism": "Автоматический механизм 26-330 S C",
            "description": "Спортивные часы в стальном корпусе",
            "photo": "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=500&h=500&fit=crop",
            "detailed_info": "Patek Philippe Nautilus - спортивные часы с характерным дизайном в виде иллюминатора. Корпус из нержавеющей стали, водонепроницаемость до 120 метров. Автоматический механизм с запасом хода 45 часов.",
            "photos": [
                "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=500&h=500&fit=crop",
                "https://images.unsplash.com/photo-1523170335258-f5b6c6e8e4c4?w=500&h=500&fit=crop",
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&h=500&fit=crop"
            ],
            "brand": "Patek Philippe",
            "category": "Спортивные",
            "material": "Нержавеющая сталь",
            "water_resistance": "120 метров",
            "warranty": "Пожизненная гарантия"
        }
    ],
    "Tissot": [
        {
            "name": "Le Locle",
            "price": "₽45,000",
            "mechanism": "Автоматический механизм ETA 2824-2",
            "description": "Классические швейцарские часы с автоподзаводом",
            "photo": "https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?w=500&h=500&fit=crop",
            "detailed_info": "Tissot Le Locle - классические швейцарские часы с элегантным дизайном. Корпус из нержавеющей стали, сапфировое стекло, водонепроницаемость до 30 метров. Автоматический механизм ETA 2824-2 с запасом хода 38 часов.",
            "photos": [
                "https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?w=500&h=500&fit=crop",
                "https://images.unsplash.com/photo-1523170335258-f5b6c6e8e4c4?w=500&h=500&fit=crop",
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&h=500&fit=crop"
            ],
            "brand": "Tissot",
            "category": "Мужские",
            "material": "Нержавеющая сталь",
            "water_resistance": "30 метров",
            "warranty": "2 года официальной гарантии"
        },
        {
            "name": "PRX",
            "price": "₽35,000",
            "mechanism": "Автоматический механизм Powermatic 80",
            "description": "Современные спортивные часы в стиле 70-х",
            "photo": "https://images.unsplash.com/photo-1523170335258-f5b6c6e8e4c4?w=500&h=500&fit=crop",
            "detailed_info": "Tissot PRX - современная интерпретация классических спортивных часов 70-х годов. Корпус из нержавеющей стали, интегрированный браслет, водонепроницаемость до 100 метров. Механизм Powermatic 80 с запасом хода 80 часов.",
            "photos": [
                "https://images.unsplash.com/photo-1523170335258-f5b6c6e8e4c4?w=500&h=500&fit=crop",
                "https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?w=500&h=500&fit=crop",
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&h=500&fit=crop"
            ],
            "brand": "Tissot",
            "category": "Спортивные",
            "material": "Нержавеющая сталь",
            "water_resistance": "100 метров",
            "warranty": "2 года официальной гарантии"
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

# Промокоды и скидки
PROMO_CODES = {
    "WELCOME10": {"discount": 10, "description": "Скидка 10% для новых клиентов"},
    "VIP15": {"discount": 15, "description": "Скидка 15% для VIP клиентов"},
    "SUMMER20": {"discount": 20, "description": "Летняя скидка 20%"},
    "FREESHIP": {"discount": 0, "free_shipping": True, "description": "Бесплатная доставка"}
}

# Глобальная корзина пользователей (в реальном проекте лучше использовать базу данных)
user_carts = {}

# Глобальное избранное пользователей
user_favorites = {}

# Функции для работы с корзиной
def get_user_cart(user_id: int) -> dict:
    """Получить корзину пользователя"""
    if user_id not in user_carts:
        user_carts[user_id] = {
            "items": [],
            "promo_code": None,
            "discount": 0,
            "free_shipping": False
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
        "items": [],
        "promo_code": None,
        "discount": 0,
        "free_shipping": False
    }

def calculate_cart_total(user_id: int) -> dict:
    """Рассчитать итоговую сумму корзины"""
    cart = get_user_cart(user_id)
    subtotal = 0
    
    for item in cart["items"]:
        # Извлекаем числовое значение цены (убираем символы валюты и запятые)
        price_str = item["price"].replace("₽", "").replace(",", "").replace(" ", "")
        try:
            price = int(price_str)
            subtotal += price * item["quantity"]
        except ValueError:
            continue
    
    # Применяем скидку
    discount_amount = 0
    if cart["promo_code"] and cart["promo_code"] in PROMO_CODES:
        promo = PROMO_CODES[cart["promo_code"]]
        if "discount" in promo:
            discount_amount = int(subtotal * promo["discount"] / 100)
    
    total = subtotal - discount_amount
    
    return {
        "subtotal": subtotal,
        "discount": discount_amount,
        "total": total,
        "free_shipping": cart.get("free_shipping", False)
    }

def apply_promo_code(user_id: int, promo_code: str) -> bool:
    """Применить промокод"""
    cart = get_user_cart(user_id)
    
    if promo_code.upper() in PROMO_CODES:
        promo = PROMO_CODES[promo_code.upper()]
        cart["promo_code"] = promo_code.upper()
        cart["discount"] = promo.get("discount", 0)
        cart["free_shipping"] = promo.get("free_shipping", False)
        return True
    return False

# Функции для работы с избранным
def get_user_favorites(user_id: int) -> list:
    """Получить избранное пользователя"""
    if user_id not in user_favorites:
        user_favorites[user_id] = []
    return user_favorites[user_id]

def add_to_favorites(user_id: int, brand: str, model_index: int):
    """Добавить товар в избранное"""
    favorites = get_user_favorites(user_id)
    item_key = f"{brand}_{model_index}"
    
    if item_key not in favorites:
        favorites.append(item_key)

def remove_from_favorites(user_id: int, brand: str, model_index: int):
    """Удалить товар из избранного"""
    favorites = get_user_favorites(user_id)
    item_key = f"{brand}_{model_index}"
    
    if item_key in favorites:
        favorites.remove(item_key)

def is_in_favorites(user_id: int, brand: str, model_index: int) -> bool:
    """Проверить, есть ли товар в избранном"""
    favorites = get_user_favorites(user_id)
    item_key = f"{brand}_{model_index}"
    return item_key in favorites

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
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 Перейти в каталог", callback_data="back_to_catalog")]
        ])
        
        await message.answer(
            "🛍️ <b>Ваша корзина пуста</b>\n\n"
            "Добавьте товары из каталога, чтобы оформить заказ.",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return
    
    # Формируем сообщение с товарами в корзине
    cart_text = "🛍️ <b>Ваша корзина</b>\n\n"
    
    for i, item in enumerate(cart["items"]):
        cart_text += f"<b>{i+1}. {item['brand']} {item['name']}</b>\n"
        cart_text += f"💰 Цена: {item['price']}\n"
        cart_text += f"📦 Количество: {item['quantity']}\n\n"
    
    # Рассчитываем итоговую сумму
    totals = calculate_cart_total(user_id)
    
    cart_text += f"📊 <b>Итого:</b>\n"
    cart_text += f"💰 Сумма: ₽{totals['subtotal']:,}\n"
    
    if totals['discount'] > 0:
        cart_text += f"🎯 Скидка: -₽{totals['discount']:,}\n"
    
    if cart.get("promo_code"):
        promo_info = PROMO_CODES[cart["promo_code"]]
        cart_text += f"🎫 Промокод: {cart['promo_code']} ({promo_info['description']})\n"
    
    cart_text += f"💳 <b>К оплате: ₽{totals['total']:,}</b>\n"
    
    if totals['free_shipping']:
        cart_text += f"🚚 <b>Бесплатная доставка!</b>\n"
    
    # Создаем клавиатуру для управления корзиной
    keyboard_buttons = []
    
    # Кнопки для каждого товара
    for i, item in enumerate(cart["items"]):
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"✏️ {item['name'][:20]}...", 
                callback_data=f"edit_item_{item['brand']}_{item['model_index']}"
            )
        ])
    
    # Кнопки управления корзиной
    keyboard_buttons.extend([
        [InlineKeyboardButton(text="🎫 Применить промокод", callback_data="apply_promo")],
        [InlineKeyboardButton(text="🗑️ Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton(text="💳 Оформить заказ", callback_data="checkout_cart")],
        [InlineKeyboardButton(text="📚 Назад в каталог", callback_data="back_to_catalog")]
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(
        cart_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )

# Функция для создания карточки товара
async def send_product_card(message: types.Message, brand: str, model_index: int):
    """Отправляет детальную карточку товара с несколькими фото и характеристиками"""
    model = WATCH_MODELS_BY_BRAND[brand][model_index]
    
    # Создаем inline клавиатуру с кнопками действий
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Добавить в корзину", callback_data=f"add_to_cart_{brand}_{model_index}")],
        [InlineKeyboardButton(text="⭐ В избранное", callback_data=f"toggle_favorite_{brand}_{model_index}")],
        [InlineKeyboardButton(text="📚 Назад в каталог", callback_data="back_to_catalog")]
    ])
    
    # Формируем текст с характеристиками
    card_text = f"""
🕰️ <b>{model['brand']} {model['name']}</b>

💰 <b>Цена:</b> {model['price']}
⚙️ <b>Механизм:</b> {model['mechanism']}

📋 <b>Характеристики:</b>
🏷️ <b>Бренд:</b> {model['brand']}
🔧 <b>Материал:</b> {model['material']}
💧 <b>Водозащита:</b> {model['water_resistance']}
🛡️ <b>Гарантия:</b> {model['warranty']}

📝 <b>Описание:</b>
{model['detailed_info']}
    """
    
    # Отправляем первое фото с полной информацией
    try:
        await message.answer_photo(
            photo=model["photos"][0],
            caption=card_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception as e:
        logging.warning(f"Не удалось загрузить главное фото для {brand} {model['name']}: {e}")
        await message.answer(
            card_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    
    # Отправляем дополнительные фото (360° или разные ракурсы)
    for i, photo_url in enumerate(model["photos"][1:], 1):
        try:
            await asyncio.sleep(0.3)  # Небольшая пауза между фото
            await message.answer_photo(
                photo=photo_url,
                caption=f"📸 <b>Ракурс {i+1}</b> - {model['brand']} {model['name']}",
                parse_mode="HTML"
            )
        except Exception as e:
            logging.warning(f"Не удалось загрузить дополнительное фото {i+1} для {brand} {model['name']}: {e}")
            continue

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обработчик команды /start"""
    # Создаем reply keyboard с основными кнопками меню
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Каталог"), KeyboardButton(text="⭐ Избранное")],
            [KeyboardButton(text="🛍️ Корзина"), KeyboardButton(text="🔍 Поиск")],
            [KeyboardButton(text="🎯 Акции"), KeyboardButton(text="📞 Контакты")],
            [KeyboardButton(text="❓ Помощь")]
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

🛍️ <b>Как сделать заказ:</b>
1. Выберите "Каталог" для просмотра товаров
2. Добавьте понравившиеся часы в корзину
3. Перейдите в "Корзина" для оформления заказа

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
    
    # Создаем inline клавиатуру с брендами для выбора
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏷️ Rolex", callback_data="catalog_brand_Rolex")],
        [InlineKeyboardButton(text="🏷️ Patek Philippe", callback_data="catalog_brand_Patek Philippe")],
        [InlineKeyboardButton(text="🏷️ Tissot", callback_data="catalog_brand_Tissot")]
    ])
    
    await message.answer(
        "📚 <b>Каталог часов</b>\n\n"
        "Выберите бренд для просмотра детальных карточек товаров:",
        parse_mode="HTML",
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
        "Для оформления заказа перейдите в каталог и добавьте товары в корзину 👇",
        parse_mode="HTML"
    )
    
    # Добавляем reply кнопку для возврата в меню
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
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
    
    # Добавляем reply кнопку для возврата в меню
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await message.answer(
        "Для оформления заказа перейдите в каталог и добавьте товары в корзину:",
        reply_markup=keyboard
    )

@dp.message(lambda message: message.text == "🛍️ Корзина")
async def cart_menu(message: types.Message):
    """Обработчик кнопки Корзина"""
    await show_cart(message)

@dp.message(lambda message: message.text == "⭐ Избранное")
async def favorites_menu(message: types.Message):
    """Обработчик кнопки Избранное"""
    user_id = message.from_user.id
    favorites = get_user_favorites(user_id)
    
    if not favorites:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 Перейти в каталог", callback_data="back_to_catalog")]
        ])
        
        await message.answer(
            "⭐ <b>Ваше избранное пусто</b>\n\n"
            "Добавьте товары в избранное, нажав на звездочку в каталоге.",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return
    
    # Формируем сообщение с избранными товарами
    favorites_text = "⭐ <b>Ваше избранное</b>\n\n"
    
    for i, item_key in enumerate(favorites, 1):
        brand, model_index = item_key.split("_")
        model_index = int(model_index)
        model = WATCH_MODELS_BY_BRAND[brand][model_index]
        
        favorites_text += f"<b>{i}. {model['brand']} {model['name']}</b>\n"
        favorites_text += f"💰 Цена: {model['price']}\n"
        favorites_text += f"📝 {model['description']}\n\n"
    
    # Создаем клавиатуру для управления избранным
    keyboard_buttons = []
    
    # Кнопки для каждого товара
    for item_key in favorites:
        brand, model_index = item_key.split("_")
        model_index = int(model_index)
        model = WATCH_MODELS_BY_BRAND[brand][model_index]
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"👁️ {model['name'][:20]}...", 
                callback_data=f"view_product_{brand}_{model_index}"
            )
        ])
    
    # Кнопки управления
    keyboard_buttons.extend([
        [InlineKeyboardButton(text="🗑️ Очистить избранное", callback_data="clear_favorites")],
        [InlineKeyboardButton(text="📚 Назад в каталог", callback_data="back_to_catalog")]
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(
        favorites_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )

@dp.message(lambda message: message.text == "🔍 Поиск")
async def search_menu(message: types.Message):
    """Обработчик кнопки Поиск"""
    await message.answer(
        "🔍 <b>Поиск часов</b>\n\n"
        "Введите название часов или бренд для поиска:\n\n"
        "💡 <b>Примеры поиска:</b>\n"
        "• Rolex\n"
        "• Submariner\n"
        "• Tissot\n"
        "• Patek Philippe\n\n"
        "Просто введите текст для поиска:",
        parse_mode="HTML"
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
        "2️⃣ Выберите понравившиеся часы\n"
        "3️⃣ Добавьте товары в корзину\n"
        "4️⃣ Перейдите в корзину\n"
        "5️⃣ Оформите заказ из корзины\n"
        "6️⃣ Ожидайте подтверждения\n\n"
        "💡 <b>Совет:</b> Вы можете добавить несколько товаров в корзину!",
        parse_mode="HTML"
    )
    
    # Добавляем reply кнопку для возврата в меню
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await callback_query.message.answer(
        "Выберите действие:",
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
    
    # Добавляем reply кнопку для возврата в меню
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await callback_query.message.answer(
        "Выберите действие:",
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
    
    # Добавляем reply кнопку для возврата в меню
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await callback_query.message.answer(
        "Выберите действие:",
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
    
    # Добавляем reply кнопку для возврата в меню
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await callback_query.message.answer(
        "Выберите действие:",
        reply_markup=keyboard
    )

# Команда для возврата в главное меню
@dp.message(Command("menu"))
async def menu_command(message: types.Message):
    """Команда для возврата в главное меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Каталог"), KeyboardButton(text="⭐ Избранное")],
            [KeyboardButton(text="🛍️ Корзина"), KeyboardButton(text="🎯 Акции")],
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


# Обработчик для возврата в меню
@dp.message(lambda message: message.text in ["🏠 Главное меню", "Назад", "Меню"])
async def back_to_menu(message: types.Message):
    """Возврат в главное меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Каталог"), KeyboardButton(text="⭐ Избранное")],
            [KeyboardButton(text="🛍️ Корзина"), KeyboardButton(text="🎯 Акции")],
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
    
    await callback_query.message.answer("✅ Каталог загружен! Добавьте понравившиеся товары в корзину для оформления заказа.")



# Обработчик выбора бренда в каталоге
@dp.callback_query(lambda c: c.data.startswith("catalog_brand_"))
async def handle_catalog_brand_selection(callback_query: CallbackQuery):
    """Обработка выбора бренда в каталоге"""
    await callback_query.answer()
    
    brand = callback_query.data.split("_")[2]
    models = WATCH_MODELS_BY_BRAND[brand]
    
    # Создаем inline клавиатуру с моделями выбранного бренда
    keyboard_buttons = []
    for i, model in enumerate(models):
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"⌚ {model['name']} - {model['price']}", 
                callback_data=f"view_product_{brand}_{i}"
            )
        ])
    
    # Добавляем кнопку "Назад к брендам"
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад к брендам", callback_data="back_to_brands")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback_query.message.edit_text(
        f"🏷️ <b>{brand}</b>\n\n"
        f"Выберите модель для просмотра детальной карточки:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

# Обработчик просмотра карточки товара
@dp.callback_query(lambda c: c.data.startswith("view_product_"))
async def handle_view_product(callback_query: CallbackQuery):
    """Обработка просмотра карточки товара"""
    await callback_query.answer()
    
    parts = callback_query.data.split("_")
    brand = parts[2]
    model_index = int(parts[3])
    
    # Отправляем детальную карточку товара
    await send_product_card(callback_query.message, brand, model_index)

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
    
    # Получаем информацию о корзине
    cart = get_user_cart(callback_query.from_user.id)
    total_items = sum(item["quantity"] for item in cart["items"])
    
    await callback_query.message.answer(
        f"🛒 <b>Товар добавлен в корзину!</b>\n\n"
        f"⌚ {model['brand']} {model['name']}\n"
        f"💰 Цена: {model['price']}\n\n"
        f"📦 В корзине: {total_items} товар(ов)\n\n"
        f"Для просмотра корзины нажмите кнопку '🛍️ Корзина' в главном меню.",
        parse_mode="HTML"
    )


# Обработчик "Назад в каталог"
@dp.callback_query(lambda c: c.data == "back_to_catalog")
async def handle_back_to_catalog(callback_query: CallbackQuery):
    """Обработка возврата в каталог"""
    await callback_query.answer()
    
    # Создаем inline клавиатуру с брендами для выбора
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏷️ Rolex", callback_data="catalog_brand_Rolex")],
        [InlineKeyboardButton(text="🏷️ Patek Philippe", callback_data="catalog_brand_Patek Philippe")],
        [InlineKeyboardButton(text="🏷️ Tissot", callback_data="catalog_brand_Tissot")]
    ])
    
    await callback_query.message.edit_text(
        "📚 <b>Каталог часов</b>\n\n"
        "Выберите бренд для просмотра детальных карточек товаров:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

# Обработчик "Назад к брендам"
@dp.callback_query(lambda c: c.data == "back_to_brands")
async def handle_back_to_brands(callback_query: CallbackQuery):
    """Обработка возврата к выбору брендов"""
    await callback_query.answer()
    
    # Создаем inline клавиатуру с брендами для выбора
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏷️ Rolex", callback_data="catalog_brand_Rolex")],
        [InlineKeyboardButton(text="🏷️ Patek Philippe", callback_data="catalog_brand_Patek Philippe")],
        [InlineKeyboardButton(text="🏷️ Tissot", callback_data="catalog_brand_Tissot")]
    ])
    
    await callback_query.message.edit_text(
        "📚 <b>Каталог часов</b>\n\n"
        "Выберите бренд для просмотра детальных карточек товаров:",
        parse_mode="HTML",
        reply_markup=keyboard
    )



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
    
    await message.answer("✅ Каталог загружен! Добавьте понравившиеся товары в корзину для оформления заказа.")

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

# Обработчики для корзины
@dp.callback_query(lambda c: c.data.startswith("edit_item_"))
async def handle_edit_item(callback_query: CallbackQuery):
    """Обработка редактирования товара в корзине"""
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
        await callback_query.message.answer("❌ Товар не найден в корзине")
        return
    
    # Создаем клавиатуру для редактирования
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➖", callback_data=f"decrease_{brand}_{model_index}"),
            InlineKeyboardButton(text=f"📦 {item['quantity']}", callback_data="noop"),
            InlineKeyboardButton(text="➕", callback_data=f"increase_{brand}_{model_index}")
        ],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"remove_{brand}_{model_index}")],
        [InlineKeyboardButton(text="🔙 Назад в корзину", callback_data="back_to_cart")]
    ])
    
    await callback_query.message.answer(
        f"✏️ <b>Редактирование товара</b>\n\n"
        f"⌚ {model['brand']} {model['name']}\n"
        f"💰 Цена: {model['price']}\n"
        f"📦 Количество: {item['quantity']}\n\n"
        f"Используйте кнопки для изменения количества:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data.startswith("increase_"))
async def handle_increase_quantity(callback_query: CallbackQuery):
    """Увеличить количество товара"""
    await callback_query.answer()
    
    parts = callback_query.data.split("_")
    brand = parts[1]
    model_index = int(parts[2])
    
    cart = get_user_cart(callback_query.from_user.id)
    for item in cart["items"]:
        if item["brand"] == brand and item["model_index"] == model_index:
            item["quantity"] += 1
            break
    
    await callback_query.message.answer("✅ Количество увеличено!")
    await show_cart(callback_query.message)

@dp.callback_query(lambda c: c.data.startswith("decrease_"))
async def handle_decrease_quantity(callback_query: CallbackQuery):
    """Уменьшить количество товара"""
    await callback_query.answer()
    
    parts = callback_query.data.split("_")
    brand = parts[1]
    model_index = int(parts[2])
    
    update_cart_quantity(callback_query.from_user.id, brand, model_index, -1)
    
    await callback_query.message.answer("✅ Количество уменьшено!")
    await show_cart(callback_query.message)

@dp.callback_query(lambda c: c.data.startswith("remove_"))
async def handle_remove_item(callback_query: CallbackQuery):
    """Удалить товар из корзины"""
    await callback_query.answer("🗑️ Товар удален из корзины!")
    
    parts = callback_query.data.split("_")
    brand = parts[1]
    model_index = int(parts[2])
    
    remove_from_cart(callback_query.from_user.id, brand, model_index)
    await show_cart(callback_query.message)

@dp.callback_query(lambda c: c.data == "apply_promo")
async def handle_apply_promo(callback_query: CallbackQuery, state: FSMContext):
    """Обработка применения промокода"""
    await callback_query.answer()
    await state.set_state(CartStates.applying_promo)
    
    await callback_query.message.answer(
        "🎫 <b>Применение промокода</b>\n\n"
        "Введите промокод для получения скидки:\n\n"
        "💡 <b>Доступные промокоды:</b>\n"
        "• WELCOME10 - скидка 10% для новых клиентов\n"
        "• VIP15 - скидка 15% для VIP клиентов\n"
        "• SUMMER20 - летняя скидка 20%\n"
        "• FREESHIP - бесплатная доставка",
        parse_mode="HTML"
    )

@dp.message(CartStates.applying_promo)
async def process_promo_code(message: types.Message, state: FSMContext):
    """Обработка введенного промокода"""
    promo_code = message.text.strip().upper()
    
    if apply_promo_code(message.from_user.id, promo_code):
        promo_info = PROMO_CODES[promo_code]
        await message.answer(
            f"✅ <b>Промокод применен!</b>\n\n"
            f"🎫 Код: {promo_code}\n"
            f"📝 Описание: {promo_info['description']}\n\n"
            f"Скидка учтена в корзине.",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ <b>Неверный промокод</b>\n\n"
            "Проверьте правильность введенного кода и попробуйте снова.",
            parse_mode="HTML"
        )
    
    await state.clear()
    await show_cart(message)

@dp.callback_query(lambda c: c.data == "clear_cart")
async def handle_clear_cart(callback_query: CallbackQuery):
    """Очистка корзины"""
    await callback_query.answer("🗑️ Корзина очищена!")
    
    clear_cart(callback_query.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Перейти в каталог", callback_data="back_to_catalog")]
    ])
    
    await callback_query.message.answer(
        "🛍️ <b>Корзина очищена</b>\n\n"
        "Добавьте товары из каталога, чтобы оформить заказ.",
        parse_mode="HTML",
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
    await state.update_data(promo_code=cart.get("promo_code"))
    await state.set_state(OrderStates.waiting_for_admin_approval)
    
    # Показываем информацию о заказе
    totals = calculate_cart_total(user_id)
    
    order_text = "💳 <b>Оформление заказа</b>\n\n"
    order_text += f"📦 Товаров в корзине: {len(cart['items'])}\n"
    order_text += f"💰 К оплате: ₽{totals['total']:,}\n\n"
    
    if cart.get("promo_code"):
        promo_info = PROMO_CODES[cart["promo_code"]]
        order_text += f"🎫 Промокод: {cart['promo_code']} ({promo_info['description']})\n\n"
    
    order_text += "Для оформления заказа введите ваше имя:"
    
    await callback_query.message.answer(
        order_text,
        parse_mode="HTML"
    )

@dp.callback_query(lambda c: c.data == "back_to_cart")
async def handle_back_to_cart(callback_query: CallbackQuery):
    """Возврат в корзину"""
    await callback_query.answer()
    await show_cart(callback_query.message)

# Обработчики для избранного
@dp.callback_query(lambda c: c.data.startswith("toggle_favorite_"))
async def handle_toggle_favorite(callback_query: CallbackQuery):
    """Переключение товара в избранном"""
    await callback_query.answer()
    
    parts = callback_query.data.split("_")
    brand = parts[2]
    model_index = int(parts[3])
    
    user_id = callback_query.from_user.id
    
    if is_in_favorites(user_id, brand, model_index):
        remove_from_favorites(user_id, brand, model_index)
        await callback_query.message.answer("❌ Товар удален из избранного")
    else:
        add_to_favorites(user_id, brand, model_index)
        await callback_query.message.answer("⭐ Товар добавлен в избранное")

@dp.callback_query(lambda c: c.data == "clear_favorites")
async def handle_clear_favorites(callback_query: CallbackQuery):
    """Очистка избранного"""
    await callback_query.answer("🗑️ Избранное очищено!")
    
    user_id = callback_query.from_user.id
    user_favorites[user_id] = []
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Перейти в каталог", callback_data="back_to_catalog")]
    ])
    
    await callback_query.message.answer(
        "⭐ <b>Избранное очищено</b>\n\n"
        "Добавьте товары в избранное, нажав на звездочку в каталоге.",
        parse_mode="HTML",
        reply_markup=keyboard
    )

# Обработчик текстовых сообщений для поиска
@dp.message()
async def handle_text_message(message: types.Message):
    """Обработчик текстовых сообщений для поиска"""
    # Игнорируем команды и кнопки меню
    if message.text in ["📚 Каталог", "⭐ Избранное", "🛍️ Корзина", "🔍 Поиск", 
                       "🎯 Акции", "📞 Контакты", "❓ Помощь", "🏠 Главное меню", 
                       "Назад", "Меню"]:
        return
    
    # Выполняем поиск
    results = search_products(message.text)
    
    if not results:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 Перейти в каталог", callback_data="back_to_catalog")]
        ])
        
        await message.answer(
            f"🔍 <b>Поиск: '{message.text}'</b>\n\n"
            "❌ Ничего не найдено\n\n"
            "Попробуйте изменить запрос или перейдите в каталог для просмотра всех товаров.",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return
    
    # Показываем результаты поиска
    search_text = f"🔍 <b>Результаты поиска: '{message.text}'</b>\n\n"
    search_text += f"Найдено товаров: {len(results)}\n\n"
    
    # Создаем клавиатуру с результатами
    keyboard_buttons = []
    
    for brand, model_index, model in results[:10]:  # Ограничиваем до 10 результатов
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"⌚ {model['name']} - {model['price']}", 
                callback_data=f"view_product_{brand}_{model_index}"
            )
        ])
    
    # Добавляем кнопку "Назад в каталог"
    keyboard_buttons.append([
        InlineKeyboardButton(text="📚 Назад в каталог", callback_data="back_to_catalog")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(
        search_text,
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
