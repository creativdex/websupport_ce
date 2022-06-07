import logging, ssl
from aiohttp import web
from aiogram import Bot, types, Dispatcher
from aiogram.dispatcher.webhook import get_new_configured_app
from bot_create import dp, bot, cfg
from handlers import other, alert, registration, admin

WH_TG = f"{cfg['SRV']['wh_host']}{cfg['BOT']['wh_in']}"

logging.basicConfig(level=logging.INFO)

routes = web.RouteTableDef()

#Получаем обновления от телеграма
@routes.post(cfg['BOT']['wh_in'])
async def tg_update(req: web.Request):
    upds = [types.Update(**(await req.json()))]
    Bot.set_current(bot)
    Dispatcher.set_current(dp)
    await dp.process_updates(upds)
    return web.Response(text="OK")

#Проверка правильности вебхука телеграма
@routes.post(cfg['BX']['wh_in'])
async def bx_update(req: web.Request):
    await other.status_send(req.query['id'], req.query['status'])
    return web.Response(text="OK")

#Проверка правильности вебхука телеграма
@routes.get('/webhook')
async def webhook(request):
    webhook_info = await bot.get_webhook_info()
    return web.Response(text=f"Webhook = {webhook_info.url}")

#Скрипт для получения сертификата SSL от центра сертификации
@routes.get('/.well-known/pki-validation/1F8DB317A7D8D9B32BF74412C71B303D.txt')
async def sslcert(request):
    return web.FileResponse('./Web/1F8DB317A7D8D9B32BF74412C71B303D.txt')

async def on_startup(app):
    logging.warning('Hi!')
    other.other_hendlers_registration(dp)
    admin.admin_hendlers_registration(dp)
    alert.alert_hendlers_registration(dp)
    registration.register_hendlers_registration(dp)

    webhook = await bot.get_webhook_info()
    if webhook.url != WH_TG:
        if not webhook.url:
            await bot.delete_webhook()
        await bot.set_webhook(WH_TG)
   
async def on_shutdown(app):

    await bot.delete_webhook()
    logging.warning('Bye!')

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_verify_locations(cfg['SRV']['ssl_bundle'])
context.load_cert_chain(certfile=cfg['SRV']['ssl_cert'], keyfile=cfg['SRV']['ssl_key'])

app = web.Application()
app = get_new_configured_app(dispatcher=dp, path=cfg['BOT']['wh_in'])
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)
app.add_routes(routes)

web.run_app(app, port=cfg['SRV']['port'], ssl_context=context)






