from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command

from aiogram.utils.keyboard import InlineKeyboardBuilder
#Ошибки 1000
    

router = Router()



@router.message(F.text, Command("console"))
async def activete(message: types.Message, state: FSMContext):
    try:
        await message.answer("Переход в режим управления консолью")
    except:
        await message.answer("Произошла ошибка 1001")
        await state.clear()