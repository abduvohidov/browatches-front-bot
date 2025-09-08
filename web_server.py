import asyncio
from aiohttp import web
import os

async def serve_webapp(request):
    """Сервис для отдачи Mini App"""
    webapp_path = os.path.join(os.path.dirname(__file__), 'webapp', 'index.html')
    
    try:
        with open(webapp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return web.Response(
            text=content,
            content_type='text/html',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
    except FileNotFoundError:
        return web.Response(text="Mini App не найден", status=404)

async def init_app():
    """Инициализация веб-приложения"""
    app = web.Application()
    
    # Маршрут для Mini App
    app.router.add_get('/webapp/index.html', serve_webapp)
    app.router.add_get('/webapp/', serve_webapp)
    
    return app

async def start_web_server():
    """Запуск веб-сервера"""
    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    
    print("🌐 Веб-сервер запущен на http://localhost:8080")
    print("📱 Mini App доступен по адресу: http://localhost:8080/webapp/index.html")
    
    # Держим сервер запущенным
    try:
        await asyncio.Future()  # Бесконечный цикл
    except KeyboardInterrupt:
        print("\n🛑 Остановка веб-сервера...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(start_web_server())
