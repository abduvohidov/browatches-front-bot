# 🤖 Телеграм бот для заказа часов

Telegram Mini App бот для оформления заказов часов с интеграцией в Google Sheets.

## 🚀 Быстрый запуск

### Автоматический запуск:
```bash
./start.sh
```

### Ручной запуск:
1. **Установите зависимости:**
   ```bash
   pip3 install aiogram aiohttp python-dotenv
   ```

2. **Запустите веб-сервер:**
   ```bash
   python3 web_server.py &
   ```

3. **Запустите бота:**
   ```bash
   python3 bot.py
   ```

4. **Найдите бота @browatchesbot в Telegram и отправьте `/start`**

## 📱 Функциональность

### Для клиентов:
- **Mini App форма** с полями:
  - Имя
  - Телефон  
  - Адрес
  - Выбор модели часов
  - Способ оплаты
- **Отправка локации** для завершения заказа
- **Подтверждение заказа** в чате

### Для админа:
- **Уведомления** о новых заказах
- **Получение локации** клиента
- **Данные заказов** в Google Sheets

## 🛠 Технические детали

### Структура проекта:
```
browatches-front-bot/
├── bot.py              # Основной файл бота
├── web_server.py       # Веб-сервер для Mini App
├── webapp/
│   └── index.html      # Mini App форма
├── config.py           # Конфигурация
├── google_sheets.py    # Интеграция с Google Sheets
├── run.py              # Скрипт запуска
└── requirements.txt    # Зависимости
```

### Используемые технологии:
- **aiogram 3.2.0** - Telegram Bot API
- **aiohttp** - Веб-сервер для Mini App
- **gspread** - Google Sheets API
- **Telegram Web App** - Mini App интерфейс

## ⚙️ Настройка

### Токен бота:
Токен уже настроен в `config.py`:
```python
BOT_TOKEN = "8251895501:AAGoJ3E8jnOtSL_triH1sWDeH6Wdx--8xU4"
```

### Admin Chat ID:
```python
ADMIN_CHAT_ID = 1247573660
```

### Google Sheets:
URL таблицы настроен в `config.py`. Для полной интеграции потребуется:
1. Создать Service Account в Google Cloud Console
2. Скачать JSON ключ
3. Обновить `google_sheets.py`

## 🧪 Тестирование

1. Запустите бота: `python run.py`
2. Найдите бота в Telegram
3. Отправьте `/start`
4. Нажмите "Оформить заказ"
5. Заполните форму
6. Отправьте локацию

## 📋 Модели часов

- Rolex Submariner
- Omega Seamaster
- Tag Heuer Carrera
- Breitling Navitimer
- Patek Philippe Calatrava

## 💳 Способы оплаты

- Наличные
- Банковская карта
- Перевод на карту
- Криптовалюта

## 🔧 Разработка

### Добавление новых моделей:
Отредактируйте массив `WATCH_MODELS` в `bot.py` и `webapp/index.html`

### Изменение способов оплаты:
Отредактируйте массив `PAYMENT_METHODS` в `bot.py` и `webapp/index.html`

### Настройка Google Sheets:
1. Создайте проект в Google Cloud Console
2. Включите Google Sheets API
3. Создайте Service Account
4. Скачайте JSON ключ
5. Обновите `google_sheets.py`

## 🐛 Устранение неполадок

### Бот не отвечает:
- Проверьте токен бота
- Убедитесь что бот запущен
- Проверьте логи в консоли

### Mini App не открывается:
- Убедитесь что веб-сервер запущен на порту 8080
- Проверьте URL в `bot.py`
- Mini App работает только в Telegram

### Ошибки с Google Sheets:
- Проверьте права доступа к таблице
- Убедитесь что Service Account настроен
- Проверьте ID таблицы в `config.py`

## 📞 Поддержка

При возникновении проблем проверьте:
1. Логи в консоли
2. Настройки в `config.py`
3. Права доступа к файлам
4. Сетевое подключение
