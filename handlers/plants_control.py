
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from assistive.states import all
import datetime
import uuid
from assistive.db.DBhelp import BotDB
from aiogram.types import InputFile
from aiogram.types import FSInputFile
import os

router = Router()




@router.message(F.text, Command("plants"))
async def shopping_cart_manegement_start(message: types.Message, state: FSMContext):
    try:
        await state.set_state(state=all.plants_Q0)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Добавить", callback_data="add_plant")],
                [InlineKeyboardButton(text="Список растений", callback_data="plants_list")],
                [InlineKeyboardButton(text="Добавить запись", callback_data="edit_plant")],
                [InlineKeyboardButton(text="Смерть", callback_data="end_plant")],
            ]
        )
        await message.answer("Менеджмент растений:", reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Произошла ошибка 3001: {str(e)}")
        await state.clear()


@router.callback_query(all.plants_Q0, F.data == "add_plant")
async def add_plant(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(all.plants_Q1)
    await callback.message.answer("Введите название растения:")


@router.message(all.plants_Q1)
async def process_plant_name(message: types.Message, state: FSMContext):
    await state.update_data(plant_name=message.text)
    await state.set_state(all.plants_Q2)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Текущая дата", callback_data="current_date")]
        ]
    )
    await message.answer("Введите дату рождения растения (ГГГГ-ММ-ДД):", reply_markup=keyboard)

@router.callback_query(all.plants_Q2, F.data == "current_date")
async def process_plant_birthdate(callback: types.CallbackQuery, state: FSMContext):
    try:
        birthdate = datetime.date.today()
        birthdate_str = birthdate.strftime("%Y-%m-%d")
        await state.update_data(plant_birthdate=birthdate_str)
        await state.set_state(all.plants_Q3)
        await callback.message.answer("Введите описание растения:")
    except ValueError:
        await callback.message.answer("Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД.")


@router.message(all.plants_Q2)
async def process_plant_birthdate2(message: types.Message, state: FSMContext):
    try:
        birthdate = datetime.datetime.strptime(message.text, "%Y-%m-%d").date()
        await state.update_data(plant_birthdate=birthdate)
        await state.set_state(all.plants_Q3)
        await message.answer("Введите описание растения:")
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД.")


@router.message(all.plants_Q3)
async def process_plant_description(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    plant_name = user_data.get("plant_name")
    plant_birthdate = user_data.get("plant_birthdate")
    plant_description = message.text

    new_plant_id = BotDB.plant_add(name=plant_name, birthdate=plant_birthdate, basic_description=plant_description, user_id=message.from_user.id)
    await state.update_data(new_plant_id=new_plant_id)

    await message.answer("Растение добавлено с номером: "+str(new_plant_id))
    await message.answer("Отправьте фото растения:")
    await state.set_state(all.plants_Q4) # Переход в состояние ожидания фото


@router.message(all.plants_Q4, F.photo)
async def process_plant_photo(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    plant_id = str(uuid.uuid4())
    photo_id = message.photo[-1].file_id  # Берем ID последнего фото, если несколько

    # Скачивание фото в папку image
    file_info = await message.bot.get_file(photo_id)
    file_path = file_info.file_path
    file_name = f"{plant_id}_{message.date.strftime('%Y%m%d%H%M%S')}.jpg"
    file_directory = os.path.join("image", file_name)
    await message.bot.download_file(file_path, file_directory)

    new_plant_id = user_data.get("new_plant_id")
    # Сохранение данных растения в БД
    BotDB.plant_history_add(new_plant_id, ("Стартовое фото"), str(plant_id) + "_" + str(message.date.strftime('%Y%m%d%H%M%S')) + ".jpg")

    await message.answer("Растение добавлено!")
    await state.clear()

#выводит список расстений
@router.callback_query(all.plants_Q0, F.data == "plants_list")
async def view_plants(callback: types.CallbackQuery, state: FSMContext):
    plants_list = BotDB.get_plants_list(callback.from_user.id)
    button = []
    for plant in plants_list:
        button.append([InlineKeyboardButton(text=str(plant[0]) + " - " + str(plant[1]), callback_data=str(plant[0]))])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard = button
    )
    await callback.message.answer("Список расстений:", reply_markup=keyboard)
    await state.set_state(all.plant_history_id)


@router.callback_query(all.plant_history_id)
async def view_plant_history_end(callback: types.CallbackQuery, state: FSMContext):  
    plants_history_list = BotDB.plant_history_get(callback.from_user.id, callback.data)
    if plants_history_list != []:
        for i in plants_history_list:
            file_directory = os.path.join("image", i[2])
            await callback.message.answer_photo(photo=FSInputFile(file_directory), caption=str(i[0])+": " + str(i[1]))
    else:
        await callback.message.answer("Такого растения нет")
        await state.clear()

@router.callback_query(F.data == "edit_plant")
async def edit_plant(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите номер растения для редактирования:")
    plants_list = BotDB.get_plants_list(callback.from_user.id)
    button = []
    for plant in plants_list:
        button.append([InlineKeyboardButton(text=str(plant[0]) + " - " + str(plant[1]), callback_data=str(plant[0]))])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard = button
    )
    await callback.message.answer("Список расстений:", reply_markup=keyboard)
    await state.set_state(all.edit_plant_id)


@router.callback_query(all.edit_plant_id)
async def process_edit_plant_id(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(plant_id=callback.data)
    plants_history_list = BotDB.plant_history_get(callback.from_user.id, callback.data)
    if plants_history_list != []:
        await callback.message.answer("Введите описание")
        await state.set_state(all.edit_plant_description)
    else:
        await callback.message.answer("Такого растения нет")
        await state.clear()


@router.message(all.edit_plant_description)
async def process_edit_plant_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)

    await message.answer("Отправьте новое фото:")
    await state.set_state(all.edit_plant_photo)


@router.message(all.edit_plant_photo, F.photo)
async def process_edit_plant_photos(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    plant_id = user_data.get("plant_id")
    description = user_data.get("description")
    user_data = await state.get_data()
    photo_id = message.photo[-1].file_id

    file_info = await message.bot.get_file(photo_id)
    file_path = file_info.file_path
    file_name = f"{plant_id}_{message.date.strftime('%Y%m%d%H%M%S')}.jpg"
    file_directory = os.path.join("image", file_name)
    await message.bot.download_file(file_path, file_directory)

    new_plant_id = user_data.get("new_plant_id")
    # Сохранение данных растения в БД
    BotDB.plant_history_add(plant_id, description, str(plant_id) + "_" + str(message.date.strftime('%Y%m%d%H%M%S')) + ".jpg")

    await message.answer("Запись добавлена")
    await state.clear()
