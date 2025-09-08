#!/usr/bin/env python3
"""
Скрипт для запуска телеграм бота с Mini App
"""
import asyncio
import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Проверка установленных зависимостей"""
    try:
        import aiogram
        import aiohttp
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("Установите зависимости: pip install -r requirements.txt")
        return False

def install_requirements():
    """Установка зависимостей"""
    print("📦 Установка зависимостей...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка при установке зависимостей")
        return False

async def run_bot_and_server():
    """Запуск бота и веб-сервера одновременно"""
    print("🚀 Запуск телеграм бота и веб-сервера...")
    
    # Импортируем модули после установки зависимостей
    from bot import main as bot_main
    from web_server import start_web_server
    
    # Запускаем бота и веб-сервер параллельно
    await asyncio.gather(
        bot_main(),
        start_web_server()
    )

def main():
    """Главная функция"""
    print("🤖 Телеграм бот для заказа часов")
    print("=" * 40)
    
    # Проверяем зависимости
    if not check_requirements():
        if not install_requirements():
            return
    
    # Проверяем наличие файлов
    required_files = ['bot.py', 'webapp/index.html', 'config.py']
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Отсутствует файл: {file}")
            return
    
    print("✅ Все файлы на месте")
    print("\n📋 Инструкция по тестированию:")
    print("1. Найдите вашего бота в Telegram")
    print("2. Отправьте команду /start")
    print("3. Нажмите кнопку 'Оформить заказ'")
    print("4. Заполните форму и отправьте")
    print("5. Отправьте локацию для завершения заказа")
    print("\n⚠️  ВАЖНО: Mini App работает только в Telegram!")
    print("=" * 40)
    
    try:
        # Запускаем бота и сервер
        asyncio.run(run_bot_and_server())
    except KeyboardInterrupt:
        print("\n🛑 Остановка бота...")
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")

if __name__ == "__main__":
    main()
