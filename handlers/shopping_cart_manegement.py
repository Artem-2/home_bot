from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from assistive.states import all

router = Router()

@router.message(F.text, Command("shopping"))
async def shopping_cart_manegement_start(message: types.Message, state: FSMContext):
    try:
        await state.set_state(state=all.shopping)
        await message.answer("Переход в режим управления консолью")
    except Exception as e:
        await message.answer(f"Произошла ошибка 2001: {str(e)}")
        await state.clear()
        