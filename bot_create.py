import configparser, os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

cfg = configparser.ConfigParser()
cfg.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini'))

tokenTG = cfg['BOT']['token']
bot = Bot(tokenTG, parse_mode='html')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class fsm_registration(StatesGroup):
    name_first = State()
    name_last = State()
    tel = State()
    city = State()
    confirm = State()

class fsm_alert(StatesGroup):
    start = State()
    division = State()
    confirm = State()
    create = State()

class fsm_admin(StatesGroup):
    menu = State()
    blacklist_cb = State()
    load_file = State()

class fsm_other(StatesGroup):
    blocked = State()
