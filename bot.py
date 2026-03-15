import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
print(f"Токен: {BOT_TOKEN}")

class TestStates(StatesGroup):
    question_1 = State()
    question_2 = State()
    question_3 = State()
    question_4 = State()

def get_answers_for_question(question_num):
    if question_num == 1:
        buttons = [
            [InlineKeyboardButton(text="А) Охотиться в лесу", callback_data="q1_a")],
            [InlineKeyboardButton(text="Б) Путешествовать по мирам", callback_data="q1_b")],
            [InlineKeyboardButton(text="В) Курагу", callback_data="q1_c")],
            [InlineKeyboardButton(text="Г) Пугать Петю", callback_data="q1_d")],
        ]
    elif question_num == 2:
        buttons = [
            [InlineKeyboardButton(text="А) Играть в футбол", callback_data="q2_a")],
            [InlineKeyboardButton(text="Б) Разбираться в технике и гаджетах", callback_data="q2_b")],
            [InlineKeyboardButton(text="В) Читать сказки", callback_data="q2_c")],
            [InlineKeyboardButton(text="Г) Дрессировать меня", callback_data="q2_d")],
        ]
    elif question_num == 3:
        buttons = [
            [InlineKeyboardButton(text="А) Случайно открыли не тот шкаф", callback_data="q3_a")],
            [InlineKeyboardButton(text="Б) Искали курагу", callback_data="q3_b")],
            [InlineKeyboardButton(text="В) У тебя же сегодня день рождения!", callback_data="q3_c")],
            [InlineKeyboardButton(text="Г) Петя хотел посмотреть, как ты живёшь", callback_data="q3_d")],
        ]
    elif question_num == 4:
        buttons = [
            [InlineKeyboardButton(text="А) На кухне (там вкусно, но нас нет)", callback_data="q4_a")],
            [InlineKeyboardButton(text="Б) В шкафу (портал, всё дела)", callback_data="q4_b")],
            [InlineKeyboardButton(text="В) Под кроватью (пыльно, мы не ходим)", callback_data="q4_c")],
            [InlineKeyboardButton(text="Г) В стиралке (я там чуть не утонул, больше не сунусь)", callback_data="q4_d")],
        ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

questions_data = {
    1: {"text": "Что я люблю больше всего на свете?", "correct": "c"},
    2: {"text": "Чем Петя любит заниматься в свободное время?", "correct": "b"},
    3: {"text": "Зачем мы с Петей вообще здесь появились? Ну, в твоей квартире", "correct": "c"},
    4: {"text": "Мы спрятали твой подарок там, где мы с Петей обычно появляемся, когда приходим в гости. Где это?", "correct": "b"}
}

async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    # Отправляем картинку отдельно
    try:
        photo = FSInputFile("welcome.jpg")
        await message.answer_photo(photo=photo)
    except Exception as e:
        print(f"Ошибка картинки: {e}")
    
    # Отправляем первый текст
    await message.answer("Ну привет. Петя сказал быть вежливым. Так что здравствуй.")
    
    # Небольшая пауза для надежности
    await asyncio.sleep(0.5)
    
    # Кнопка с текстом
    start_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🚀 Поехали!", callback_data="start_test")]]
    )
    await message.answer("Подарок мы нашли. Но просто так отдать? Скучно.\nОтвечаешь на 4 вопроса — получаешь финальную подсказку.\nОшибёшься — дам вторую попытку, я добрый сегодня", reply_markup=start_kb)

async def start_test(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(TestStates.question_1)
    
    try:
        photo = FSInputFile("q1.jpg")
        await callback.message.answer_photo(photo=photo, caption="Вопрос №1")
    except:
        pass
    
    await callback.message.answer(
        questions_data[1]["text"], 
        reply_markup=get_answers_for_question(1)
    )
    await callback.answer()

async def send_question(message: types.Message, question_num: int):
    try:
        photo = FSInputFile(f"q{question_num}.jpg")
        await message.answer_photo(photo=photo, caption=f"Вопрос №{question_num}")
    except:
        pass
    
    await message.answer(
        questions_data[question_num]["text"],
        reply_markup=get_answers_for_question(question_num)
    )

async def handle_answer(callback: types.CallbackQuery, state: FSMContext):
    question_num = int(callback.data[1])
    user_answer = callback.data[3]
    correct = questions_data[question_num]["correct"]
    
    if user_answer == correct:
        if question_num < 4:
            await callback.message.answer("✅ Верно!")
    else:
        if question_num == 1:
            hint = "Подсказка: это то, что сушат и очень любят"
        elif question_num == 2:
            hint = "Его хобби связано с проводами и кнопками"
        elif question_num == 3:
            hint = "Мы надеялись попробовать твой торт"
        elif question_num == 4:
            hint = "В портале между мирами"
        
        await callback.message.answer(f"❌ Не угадал. Но я добрый, попробуй еще раз.\n{hint}")
        await callback.answer()
        return
    
    if question_num < 4:
        next_q = question_num + 1
        await state.set_state(getattr(TestStates, f"question_{next_q}"))
        await asyncio.sleep(1)
        await send_question(callback.message, next_q)
    else:
        await state.clear()
        try:
            photo = FSInputFile("final.jpg")
            await callback.message.answer_photo(photo=photo)
        except:
            pass
        
        final_text = ("Ну всё, экзамен сдан. Петя гордится.\n\n"
                     "Иди в шкаф. Подарков там два.\n"
                     "Один — тот, который ты ждёшь.\n"
                     "Второй — мы с Петей. Мы всегда тут. За дверцей.\n"
                     "Даже когда молчим — мы рядом.\n\n"
                     "С днюхой.\n\n"
                     "P.S. Курага в кармане куртки. Это тебе. Но если съешь, я обижусь.")
        await callback.message.answer(final_text)
    
    await callback.answer()

async def main():
    bot = Bot(token=BOT_TOKEN)  # ИСПРАВЛЕНО!
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.message.register(cmd_start, Command("start"))
    dp.callback_query.register(start_test, F.data == "start_test")
    dp.callback_query.register(handle_answer, F.data.startswith("q"))
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())