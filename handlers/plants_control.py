
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from assistive.states import all
import datetime
import uuid
from assistive.db.DBhelp import BotDB

router = Router()




@router.message(F.text, Command("plants"))
async def shopping_cart_manegement_start(message: types.Message, state: FSMContext):
    try:
        await state.set_state(state=all.plants_Q0)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Добавить", callback_data="add_plant")],
                [InlineKeyboardButton(text="Посмотреть", callback_data="view_plants")],
                [InlineKeyboardButton(text="Изменить", callback_data="edit_plant")],
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
    await message.bot.download_file(file_path, f"image/{plant_id}_{message.date}.jpg")

    new_plant_id = user_data.get("new_plant_id")
    # Сохранение данных растения в БД
    BotDB.plant_history_add(new_plant_id, ("Стартовое фото"), str(plant_id) + "_" + str(message.date))

    await message.answer("Растение добавлено!")
    await state.clear()


@router.callback_query(F.data == "view_plants")
async def view_plants(callback: types.CallbackQuery, state: FSMContext):
    # Здесь запрос в БД и вывод информации о всех растениях
    # ...  Получение данных растений из БД ...
    await callback.message.answer("Информация о растениях:\n"
                                 # ... Вывод информации из БД ...
                                  )


@router.callback_query(F.data == "edit_plant")
async def edit_plant(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите номер растения для редактирования:")
    await state.set_state(all.edit_plant_id)


@router.message(all.edit_plant_id)
async def process_edit_plant_id(message: types.Message, state: FSMContext):
    plant_number = message.text
    # Здесь запрос в БД по номеру растения
    # ... Получение данных о растении по plant_number из БД ...

    #Если растение найдено
    #if plant_data: # plant_data - данные растения из БД
        #await state.update_data(plant_number=plant_number, plant_data=plant_data)
        #await message.answer("Введите новое описание:")
        #await state.set_state(all.edit_plant_description)
    #else:
        #await message.answer("Растение не найдено.")
        #await state.clear()


@router.message(all.edit_plant_description)
async def process_edit_plant_description(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    new_description = message.text

    # Здесь обновление данных растения в БД
    # ... Обновление поля описания в БД ...

    await message.answer("Описание обновлено. Отправьте новые фото (можно ничего не отправлять):")
    await state.set_state(all.edit_plant_photo)


@router.message(all.edit_plant_photo, F.photo)
async def process_edit_plant_photos(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    plant_number = user_data['plant_number']
    photo_id = message.photo[-1].file_id

    # Здесь сохранение новых фото в хранилище и обновление в БД
    # ... Добавить логику сохранения фото и обновления БД ...

    await message.answer("Фотографии обновлены!")
    await state.clear()

@router.message(all.edit_plant_photo) #обработка отсутствия фото
async def process_edit_plant_photo_skip(message: types.Message, state: FSMContext):
    await message.answer("Фотографии не обновлены!")
    await state.clear()
