Python 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import asyncio
import random
import os
import aiohttp
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import MessageReactionTypeEmoji

# Загружаем переменные из .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
BOT_USERNAME = os.getenv("BOT_USERNAME")

if not BOT_TOKEN:
    raise ValueError("Нет BOT_TOKEN в .env")
if not DEEPSEEK_API_KEY:
    raise ValueError("Нет DEEPSEEK_API_KEY в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================
# ПАМЯТЬ
# =========================

memory = {}

SYSTEM_PROMPT = """
Ты живой 19-летний человек.
Иногда шутишь.
Иногда отвечаешь коротко.
Иногда используешь сленг.
Не пиши длинные тексты.
Не говори что ты ИИ.
"""

# =========================
# DeepSeek API
# =========================

async def ask_deepseek(messages):
    url = "https://api.deepseek.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.9
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            result = await response.json()
            return result["choices"][0]["message"]["content"]

# =========================
# Реакции
# =========================

def choose_reaction(text):
    text = text.lower()

    if any(word in text for word in ["люблю", "класс", "круто"]):
        return "❤️"
    elif any(word in text for word in ["грустно", "плохо", "депресс"]):
        return "😢"
    elif "?" in text:
        return "🤔"
    else:
        return random.choice(["👀", "🔥", "✨", "💀"])

# =========================
# Обработка сообщений
# =========================

@dp.message()
async def handle_message(message: types.Message):

    if not message.text:
        return

    user_id = message.from_user.id
    text = message.text

    # В группах реагирует только если упомянули
    if message.chat.type in ["group", "supergroup"]:
        if BOT_USERNAME and f"@{BOT_USERNAME}" not in text:
            return

    # 20% шанс игнора (человечность)
    if random.random() < 0.2:
        return

    # Ставим реакцию
    try:
        reaction = choose_reaction(text)
        await bot.set_message_reaction(
            chat_id=message.chat.id,
...             message_id=message.message_id,
...             reaction=[MessageReactionTypeEmoji(emoji=reaction)]
...         )
...     except:
...         pass
... 
...     # Показывает "печатает..."
...     await bot.send_chat_action(message.chat.id, "typing")
... 
...     # Задержка перед ответом
...     await asyncio.sleep(random.randint(2, 5))
... 
...     # Память
...     if user_id not in memory:
...         memory[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
... 
...     memory[user_id].append({"role": "user", "content": text})
...     memory[user_id] = memory[user_id][-12:]
... 
...     # Ответ DeepSeek
...     try:
...         reply = await ask_deepseek(memory[user_id])
...     except Exception as e:
...         print("Ошибка DeepSeek:", e)
...         reply = "что-то сломалось 💀"
... 
...     memory[user_id].append({"role": "assistant", "content": reply})
... 
...     await message.reply(reply)
... 
... # =========================
... # Запуск
... # =========================
... 
... async def main():
...     print("Бот запущен...")
...     await dp.start_polling(bot)
... 
... if __name__ == "__main__":
