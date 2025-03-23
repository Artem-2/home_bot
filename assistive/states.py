from aiogram.fsm.state import StatesGroup, State



class all(StatesGroup):
    shopping = State()
    console_state = State()
    plants_Q0 = State()
    plants_Q1 = State()
    plants_Q2 = State()
    plants_Q3 = State()
    plants_Q4 = State()
    plant_history_id = State()
    edit_plant_id = State()
    edit_plant_description = State()
    edit_plant_photo = State()
    end_plant = State()
    