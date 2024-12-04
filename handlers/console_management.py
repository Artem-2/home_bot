import asyncio
import subprocess
import shlex  # для корректного разделения строки на аргументы
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from assistive.states import all
import platform

router = Router()

@router.message(F.text, Command("console"))
async def console_manegement_start(message: types.Message, state: FSMContext):
    try:
        await state.set_state(state=all.console_state)
        await message.answer("Переход в режим управления консолью")
    except Exception as e:
        await message.answer(f"Произошла ошибка 1001: {str(e)}")
        await state.clear()

@router.message(F.text, all.console_state)
async def console_manegement(message: types.Message, state: FSMContext):
    await message.answer("Начало выполнения команды...")
    output = run_command(message.tex)
    await message.answer("Конец выполнения команды.")
    await message.answer(str(output), parse_mode=types.ParseMode.MARKDOWN)





def run_command(command):
    pass