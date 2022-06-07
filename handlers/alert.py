from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types.message import ContentTypes
import aiogram.utils.markdown as fmt
from bot_create import fsm_alert, bot, cfg
from bot_bx import bx_create_smart
from bot_sql import sql_get_division, sql_get_user, sql_get_cashbox, sql_create_smart
from handlers.other import other_user_check, other_image_convert

async def contacting_start(message: types.Message):
    """ Начало обращения инцидент, запрашиваем подразделение """
    await fsm_alert.start.set()
    mark_menu_main = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = ["Инцидент", "ОРП", "Консультация"]
    mark_menu_main.add(*buttons)
    await message.answer(f"Выберите тип обращения", reply_markup=mark_menu_main)

async def contacting_get_type(message: types.Message, state: FSMContext):
    """ Начало обращения инцидент, запрашиваем подразделение """
    if message.text == "Инцидент" or message.text == "Консультация" or message.text == "ОРП":
        await fsm_alert.division.set()
        await state.update_data(type=message.text)
        if message.text == "Инцидент":
            await state.update_data(id_type='160')
        elif message.text == "Консультация":
            await state.update_data(id_type='178')
        elif message.text == "ОРП":
            await state.update_data(id_type='170')
        division = sql_get_division(message.from_user.id)
        await state.update_data(division_select=division)
        mark_division = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        mark_division.add(*division)
        await message.answer("Выберите подразделение", reply_markup=mark_division)
    else:
        await message.answer("Выберите из предложеного списка")

async def contacting_get_division(message: types.Message, state: FSMContext):
    """ Запрашиваем краткое описание инцидент"""
    fsm_data_user = await state.get_data()
    if message.text in fsm_data_user['division_select']:
        await fsm_alert.confirm.set()
        await state.update_data(division=message.text)
        if fsm_data_user['type'] == 'ОРП':        
            cashbox = sql_get_cashbox(message.text)
            await state.update_data(cashbox_select=cashbox)
            mark_cashbox = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            mark_cashbox.add(*cashbox)
            await message.answer("Выберите кассу", reply_markup=mark_cashbox)
        else:
            await message.answer("Кратко опишите суть проблемы", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("Выберите из предложеного списка")
        
async def contacting_confirm(message: types.Message, state: FSMContext):
    """ Проверяем введенные данные """
    await state.update_data(image_name='')
    await state.update_data(image='')
    await state.update_data(description=message.text)
    fsm_data_user = await state.get_data()
    mark_confirm = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = ["Подтвердить", "Отменить"]
    mark_confirm.add(*buttons)
    text_confirm = fmt.text(fmt.text(f"<b>Тип обращения: </b>{fsm_data_user['type']}"),
                   fmt.text(f"<b>Подразделение: </b>{fsm_data_user['division']}"),
                   fmt.text(f"<b>Описание: </b>{fsm_data_user['description']}"), sep='\n')
    if fsm_data_user['type'] == 'ОРП':
        if message.text in fsm_data_user['cashbox_select']:
            await fsm_alert.create.set()
            await message.answer(text_confirm, reply_markup=mark_confirm)
        else:
            await message.answer("Выберите из предложеного списка")
    elif message.content_type == 'photo' or message.content_type == 'document':
        image = await other_image_convert(message)
        await state.update_data(image_name=image[0].pop(0))
        await state.update_data(image=image[1].pop())
        await state.update_data(description=message.caption)
        await fsm_alert.create.set()
        await message.answer(fmt.text(fmt.text(f"<b>Тип обращения: </b>{fsm_data_user['type']}"),
                             fmt.text(f"<b>Подразделение: </b>{fsm_data_user['division']}"),
                             fmt.text(f"<b>Описание: </b>Скриншот\n{message.caption}"), sep='\n'), reply_markup=mark_confirm)
    else:  
        await fsm_alert.create.set()
        await message.answer(text_confirm, reply_markup=mark_confirm)

""" Регистрируем обрашение инцидент в BX и отпраляем сообшение об успехе в чат """
async def contacting_create(message: types.Message, state: FSMContext):    
    if message.text == "Подтвердить":    
        fsm_data_user = await state.get_data()
        sql_data_user = sql_get_user(message.from_user.id)
        bx_param = f"{fsm_data_user['division']}\n{sql_data_user[0]}\n{sql_data_user[1]}\n{fsm_data_user['type']}\n{fsm_data_user['description']}"
        result = await bx_create_smart(fsm_data_user['division'], bx_param, sql_data_user[0], fsm_data_user['id_type'], fsm_data_user['image_name'], fsm_data_user['image'])
        bx_markup = types.InlineKeyboardMarkup(row_width=2)
        bx_url = types.InlineKeyboardButton('Обращение в битриксе', 
        f"https://cenalom.bitrix24.ru/page/tekh_podderzhka_/tekhnicheskaya_podderzhka/type/184/details/{result['item']['id']}/")
        bx_markup.add(bx_url)  
        if fsm_data_user['type'] == 'ОРП':
            await message.answer(f"Зарегистрировано обращение от\n{fsm_data_user['division']}, проблема с ОРП\n{fsm_data_user['description']}\nОжидайте, техническая поддержка с вами свяжется", reply_markup=bx_markup)
            msg = await bot.send_message(cfg['BOT']['chatsend'],f"Зарегистрировано обращение от\n{fsm_data_user['division']}, проблема с ОРП\n{fsm_data_user['description']}\nОжидайте, техническая поддержка с вами свяжется", reply_markup=bx_markup)
            sql_create_smart(result['item']['id'], msg.message_id)
        else:
            await message.answer(f"Зарегистрировано обращение от\n{fsm_data_user['division']}\nОжидайте, техническая поддержка с вами свяжется", reply_markup=bx_markup)
            msg = await bot.send_message(cfg['BOT']['chatsend'],f"Зарегистрировано обращение от\n{fsm_data_user['division']}\nОжидайте, техническая поддержка с вами свяжется", reply_markup=bx_markup)
            sql_create_smart(result['item']['id'], msg.message_id)
        await state.finish()
        await other_user_check(message, state)
    elif message.text == "Отменить":
        await state.finish()
        await other_user_check(message, state)
    
async def get_chat_id(message: types.Message):
    await bot.send_message('912702931',f"Чат ID группы <code>{message.chat.id}</code>")

    


def alert_hendlers_registration(dp: Dispatcher):
    dp.register_message_handler(contacting_get_type, state=fsm_alert.start)
    dp.register_message_handler(contacting_get_division, state=fsm_alert.division)
    dp.register_message_handler(contacting_confirm, content_types=ContentTypes.PHOTO | ContentTypes.DOCUMENT | ContentTypes.TEXT, state=fsm_alert.confirm)
    dp.register_message_handler(contacting_create, state=fsm_alert.create)
    #dp.register_message_handler(get_chat_id, commands="chat")    
    
    
