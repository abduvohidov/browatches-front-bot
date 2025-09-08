#!/bin/bash

echo "🤖 Запуск телеграм бота для заказа часов"
echo "========================================"

# Остановка предыдущих процессов
echo "🛑 Остановка предыдущих процессов..."
pkill -f "python3 bot.py" 2>/dev/null
pkill -f "python3 web_server.py" 2>/dev/null
sleep 2

# Проверка зависимостей
echo "📦 Проверка зависимостей..."
python3 -c "import aiogram, aiohttp" 2>/dev/null || {
    echo "❌ Установка зависимостей..."
    pip3 install aiogram aiohttp python-dotenv
}

# Запуск веб-сервера
echo "🌐 Запуск веб-сервера..."
python3 web_server.py &
WEB_PID=$!
sleep 3

# Проверка веб-сервера
if curl -s http://localhost:8080/webapp/index.html > /dev/null; then
    echo "✅ Веб-сервер запущен на http://localhost:8080"
else
    echo "❌ Ошибка запуска веб-сервера"
    kill $WEB_PID 2>/dev/null
    exit 1
fi

# Запуск бота
echo "🤖 Запуск бота..."
python3 bot.py &
BOT_PID=$!

# Проверка бота
sleep 3
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Бот запущен успешно!"
    echo ""
    echo "📋 Инструкция по тестированию:"
    echo "1. Найдите бота @browatchesbot в Telegram"
    echo "2. Отправьте команду /start"
    echo "3. Нажмите кнопку 'Оформить заказ'"
    echo "4. Заполните форму и отправьте"
    echo "5. Отправьте локацию для завершения заказа"
    echo ""
    echo "⚠️  ВАЖНО: Mini App работает только в Telegram!"
    echo "🌐 Mini App: http://localhost:8080/webapp/index.html"
    echo ""
    echo "Для остановки нажмите Ctrl+C"
    
    # Ожидание сигнала остановки
    trap "echo ''; echo '🛑 Остановка...'; kill $BOT_PID $WEB_PID 2>/dev/null; exit 0" INT
    wait
else
    echo "❌ Ошибка запуска бота"
    kill $WEB_PID 2>/dev/null
    exit 1
fi
