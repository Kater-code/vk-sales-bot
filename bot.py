import os
import asyncio
from dotenv import load_dotenv
from vkbottle import Keyboard, KeyboardButtonColor, Text, BaseStateGroup, StatePeer
from vkbottle.bot import Bot, Message
from mistralai.client import Mistral

load_dotenv()

TOKEN = os.getenv("VK_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
MISTRAL_KEY = os.getenv("MISTRAL_API_KEY")

bot = Bot(token=TOKEN)
mistral = Mistral(api_key=MISTRAL_KEY)

# ==========================================
# СИСТЕМНЫЙ ПРОМПТ
# ==========================================
SYSTEM_PROMPT = """Ты — AI-ассистент сообщества "AI-автоматизация для бизнеса".
Тебя зовут Кaтерина. Ты помогаешь потенциальным клиентам.

О нас:
- Делаем AI-ботов для ВКонтакте на базе Mistral AI
- Автоматизируем процессы на n8n
- Интегрируем с CRM, Google Sheets, Telegram
- Создаем лендинги под ключ
- Стек: Python, FastAPI, n8n, Mistral AI, VK API

Цены:
- Простой бот с воронкой: от 30 000 руб
- AI-бот с Mistral + CRM: от 60 000 руб
- Автоматизация процессов на n8n: от 40 000 руб
- Лендинг под ключ: от 20 000 руб
- Поддержка и доработки: от 8 000 руб/мес

Правила общения:
- Отвечай кратко, по делу, дружелюбно
- Не придумывай то чего нет в описании
- Если вопрос сложный — предложи оставить заявку на бесплатную консультацию
- Пиши на русском языке
- Не используй сложные технические термины без объяснения
"""

# ==========================================
# КЛАВИАТУРЫ
# ==========================================
menu_keyboard = (
    Keyboard(one_time=False, inline=False)
    .add(Text("📝 Оставить заявку"), color=KeyboardButtonColor.POSITIVE)
    .row()
    .add(Text("❓ Задать вопрос"), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text("💰 Цены"), color=KeyboardButtonColor.SECONDARY)
    .get_json()
)

cancel_keyboard = (
    Keyboard(one_time=False, inline=False)
    .add(Text("❌ Отмена"), color=KeyboardButtonColor.NEGATIVE)
    .get_json()
)

# ==========================================
# FSM
# ==========================================
class OrderState(BaseStateGroup):
    WAITING_FOR_NAME = "name"
    WAITING_FOR_PHONE = "phone"
    WAITING_FOR_PROBLEM = "problem"

# ==========================================
# ИСТОРИЯ ДИАЛОГОВ (в памяти)
# ==========================================
user_histories: dict[int, list] = {}

def get_history(user_id: int) -> list:
    if user_id not in user_histories:
        user_histories[user_id] = []
    return user_histories[user_id]

async def ask_mistral(user_id: int, user_message: str) -> str:
    history = get_history(user_id)
    history.append({"role": "user", "content": user_message})

    if len(history) > 10:
        history = history[-10:]
        user_histories[user_id] = history

    response = await asyncio.to_thread(
        mistral.chat.complete,
        model="mistral-small-latest",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
    )

    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    return reply

# ==========================================
# ОБРАБОТЧИКИ
# ==========================================

@bot.on.message(text=["Привет", "Начать", "Start", "start", "привет", "начать"])
async def start_handler(message: Message):
    await message.answer(
        "Привет! Я Катерина — AI-ассистент этого сообщества 🤖\n\n"
        "Помогу рассказать об услугах, ответить на вопросы "
        "или принять заявку на бесплатную консультацию.\n\n"
        "Выбери что тебя интересует 👇",
        keyboard=menu_keyboard
    )

@bot.on.message(text="💰 Цены")
async def prices_handler(message: Message):
    await message.answer(
        "💰 Наши услуги:\n\n"
        "🤖 AI-бот для ВК (Mistral) — от 60 000 ₽\n"
        "⚙️ Автоматизация на n8n — от 40 000 ₽\n"
        "🔗 Простой бот с воронкой — от 30 000 ₽\n"
        "🌐 Лендинг под ключ — от 20 000 ₽\n"
        "🛠 Поддержка — от 8 000 ₽/мес\n\n"
        "Первая консультация бесплатно — просто оставь заявку 👇",
        keyboard=menu_keyboard
    )

# --- Кнопка "Задать вопрос" — идет в Mistral ---
@bot.on.message(text="❓ Задать вопрос")
async def question_handler(message: Message):
    await message.answer(
        "Задавай — отвечу на любой вопрос об автоматизации и наших услугах 💬",
        keyboard=cancel_keyboard
    )

# --- Старт анкеты ---
@bot.on.message(text="📝 Оставить заявку")
async def start_order(message: Message):
    await message.answer(
        "Отлично! Оставь заявку — перезвоним и обсудим задачу.\n\n"
        "Как тебя зовут?",
        keyboard=cancel_keyboard
    )
    await bot.state_dispenser.set(message.peer_id, OrderState.WAITING_FOR_NAME)

# --- Шаг 1: имя ---
@bot.on.message(state=OrderState.WAITING_FOR_NAME)
async def get_name_step(message: Message):
    if message.text.lower() in ["❌ отмена", "отмена", "стоп", "назад"]:
        await bot.state_dispenser.delete(message.peer_id)
        await message.answer("Хорошо, отменили 👌 Если что — возвращайся!", keyboard=menu_keyboard)
        return

    await bot.state_dispenser.set(message.peer_id, OrderState.WAITING_FOR_PHONE, name=message.text)
    await message.answer(
        f"Приятно познакомиться, {message.text}! 👋\n\nНапиши номер телефона для связи:",
        keyboard=cancel_keyboard
    )

# --- Шаг 2: телефон ---
@bot.on.message(state=OrderState.WAITING_FOR_PHONE)
async def get_phone_step(message: Message):
    if message.text.lower() in ["❌ отмена", "отмена", "стоп", "назад"]:
        await bot.state_dispenser.delete(message.peer_id)
        await message.answer("Хорошо, отменили 👌", keyboard=menu_keyboard)
        return

    state_info: StatePeer = await bot.state_dispenser.get(message.peer_id)
    name = state_info.payload.get("name")

    await bot.state_dispenser.set(
        message.peer_id, OrderState.WAITING_FOR_PROBLEM,
        name=name, phone=message.text
    )
    await message.answer(
        "Принял! Теперь коротко — какая задача или проблема?\n\n"
        "Например: 'хочу бота для записи клиентов' или 'нужна автоматизация заявок'",
        keyboard=cancel_keyboard
    )

# --- Шаг 3: задача — финал ---
@bot.on.message(state=OrderState.WAITING_FOR_PROBLEM)
async def get_problem_step(message: Message):
    if message.text.lower() in ["❌ отмена", "отмена", "стоп", "назад"]:
        await bot.state_dispenser.delete(message.peer_id)
        await message.answer("Хорошо, отменили 👌", keyboard=menu_keyboard)
        return

    state_info: StatePeer = await bot.state_dispenser.get(message.peer_id)
    name = state_info.payload.get("name")
    phone = state_info.payload.get("phone")
    problem = message.text

    await message.answer(
        f"✅ Заявка принята!\n\n"
        f"👤 {name}\n"
        f"📞 {phone}\n"
        f"💬 {problem}\n\n"
        f"Свяжемся с тобой в ближайшее время 🚀",
        keyboard=menu_keyboard
    )

    await bot.api.messages.send(
        user_id=ADMIN_ID,
        message=(
            f"🔥 НОВАЯ ЗАЯВКА\n\n"
            f"👤 Имя: {name}\n"
            f"📞 Телефон: {phone}\n"
            f"💬 Задача: {problem}\n\n"
            f"VK: vk.com/id{message.from_id}"
        ),
        random_id=0
    )

    await bot.state_dispenser.delete(message.peer_id)

# --- Все остальные сообщения — Mistral ---
@bot.on.message()
async def ai_handler(message: Message):
    if not message.text or message.text.startswith("/"):
        return

    state = await bot.state_dispenser.get(message.peer_id)
    if state:
        return

    try:
        reply = await ask_mistral(message.from_id, message.text)
        await message.answer(reply, keyboard=menu_keyboard)
    except Exception as e:
        await message.answer(
            "Что-то пошло не так, попробуй ещё раз 🙏",
            keyboard=menu_keyboard
        )

# ==========================================
# ЗАПУСК
# ==========================================
if __name__ == "__main__":
    print("🚀 AI-бот запущен!")
    bot.run_forever()