import asyncio
import json
import logging
import os
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
# ------------------------------------------------------------------
# SOZLAMALAR
# ------------------------------------------------------------------

TOKEN = os.getenv("8469333012:AAE5tiaoVexn1RogHnYXrqxwl0g9_a4NVHY")
DB_FILE = os.getenv("DB_PATH", "users.db")

# ------------------------------------------------------------------
# 57 TA SAVOL (Eysenck EPI testi)
# ------------------------------------------------------------------
QUESTIONS = [
    "Siz tez-tez yangi taassurotlarga, o'zingizni silkitib olishga, hayajonlanishga intilasizmi?",
    "Sizni tushunadigan, dalda yoki tasalli beradigan do'stlarga ehtiyoj sezasizmi?",
    "Siz beparvo odammisiz?",
    "Biror narsani so'rashsa, rad etish siz uchun juda qiyinmi?",
    "Biror ish qilishdan oldin o'ylab ko'rasizmi?",
    "Biror narsaga va'da bersangiz, noqulay bo'lsa ham, doim va'dangizni bajarasizmi?",
    "Kayfiyatingiz tez-tez ko'tarilib-tushib turadimi?",
    "Odatda tez harakat qilasiz va uzoq o'ylamasdan gapirasizmi?",
    "Hech qanday sababsiz o'zingizni baxtsiz his qilganmisiz?",
    "Tikishda deyarli hamma narsani qilishga tayyormisiz?",
    "Chiroyli notanish odam bilan gaplashmoqchi bo'lganingizda to'satdan uyalib qolasizmi?",
    "Ba'zan jahlingiz chiqib, g'azablanasizmi?",
    "Siz tez-tez o'sha onning ta'siri bilan harakat qilasizmi?",
    "Aytmasligingiz yoki qilmasligingiz kerak bo'lgan narsalar haqida tez-tez tashvishlanasizmi?",
    "Odamlar bilan uchrashgandan ko'ra kitob o'qishni afzal ko'rasizmi?",
    "Hissiyotlaringizni xafa qilish oson deb o'ylaysizmi?",
    "Do'stlar bilan davralarga tez-tez borishni yoqtirasizmi?",
    "Boshqalar bilishini xohlamaydigan fikrlaringiz bormi?",
    "Ba'zan energiyaga to'lib-toshasiz, ba'zan esa butunlay bo'shashib ketasizmi?",
    "Do'stlaringiz kam, lekin juda yaqin bo'lishini afzal ko'rasizmi?",
    "Siz ko'p xayol surasizmi?",
    "Sizga baqirishsa, siz ham baqirib javob berasizmi?",
    "Sizni tez-tez aybdorlik hissi qiynaydimi?",
    "Sizning barcha odatlaringiz yaxshi va maqbulmi?",
    "Do'stlar davrasida o'zingizni erkin qo'yib, xursand bo'la olasizmi?",
    "Siz o'zingizni hayajonlangan, 'tarang' odam deb hisoblaysizmi?",
    "Sizni jonli va quvnoq odam deb bilishadimi?",
    "Muhim ish qilganingizdan keyin, uni yaxshiroq qilish mumkin edi deb o'ylaysizmi?",
    "Boshqalar bilan birga bo'lganingizda ko'proq jim turasizmi?",
    "Ba'zan g'iybat qilasizmi?",
    "Ba'zan fikrlar boshingizga to'lib, uxlay olmay qolasizmi?",
    "Biror narsani bilmoqchi bo'lsangiz, birovdan so'rashdan ko'ra kitobdan qidirishni afzal ko'rasizmi?",
    "Yuragingiz tez-tez ura boshlaydimi (yurak urishi sezilib ketadimi)?",
    "Diqqat bilan ishlashni talab qiladigan ishni yoqtirasizmi?",
    "Sizda titroq (qaltirash) xurujlari bo'ladimi?",
    "Bojxonada, aniqlanmasligingizga ishonchingiz komil bo'lsa ham, hamma narsani e'lon qilarmidingiz?",
    "Odamlar bir-birini masxara qiladigan davrada bo'lish sizga yoqmaydimi?",
    "Siz serjahl (tez asabiylashadigan) odammisiz?",
    "Tezlikni talab qiladigan ishni yoqtirasizmi?",
    "Mumkin bo'lgan yoqimsiz voqealar haqida tashvishlanasizmi?",
    "Siz harakatlarda sekin va shoshilmaydigan odammisiz?",
    "Siz biror uchrashuvga yoki ishga kechikkanmisiz?",
    "Sizga tez-tez qo'rqinchli tushlar ko'rinadimi?",
    "Gaplashishni shunchalik yoqtirasizki, notanish odam bilan gaplashish imkoniyatini qo'ldan chiqarmaysizmi?",
    "Og'riqlar sizni bezovta qiladimi?",
    "Agar odamlardan uzoq vaqt ajralib qolsangiz, o'zingizni juda baxtsiz his qilarmidingiz?",
    "O'zingizni asabiy (nervoz) odam deb atarmidingiz?",
    "Tanishlaringiz orasida sizga aniq yoqmaydigan odamlar bormi?",
    "O'zingizni ishonchli odam deb ayta olasizmi?",
    "Odamlar xatolaringizni yoki ishingizdagi kamchilikni aytsa, tez xafa bo'lasizmi?",
    "Jonli bazmdan chinakam zavq olish siz uchun qiyinmi?",
    "Sizni pastlik (o'zini kam his qilish) tuyg'usi bezovta qiladimi?",
    "Zerikarli davrani jonlantirish siz uchun osonmi?",
    "Ba'zan o'zingiz hech narsa bilmaydigan narsa haqida gapirasizmi?",
    "Sog'lig'ingiz haqida tashvishlanasizmi?",
    "Boshqalarga hazil-mutoyiba qilishni yoqtirasizmi?",
    "Uyqusizlikdan azob chekasizmi?",
]
assert len(QUESTIONS) == 57, "Savollar soni aynan 57 ta bo'lishi shart!"

# Kalit: "Ha" deb javob berilsa 1 ball
E_YES = {1, 3, 8, 10, 13, 17, 22, 25, 27, 39, 44, 46, 49, 53, 56}  # Ekstraversiya
E_NO = {5, 15, 20, 29, 32, 34, 37, 41, 51}                          # "Yo'q" -> ball
N_YES = {2, 4, 7, 9, 11, 14, 16, 19, 21, 23, 26, 28, 31, 33, 35,
         38, 40, 43, 45, 47, 50, 52, 55, 57}                        # Nevrotizm
L_YES = {6, 24, 36}                                                 # Yolg'on shkalasi
L_NO = {12, 18, 30, 42, 48, 54}

TEMPERAMENTS = {
    "sanguinik": (
        "🌞 SANGVINIK",
        "Siz quvnoq, ochiq, tez til topishadigan, muammolarga yengil qaraydigan odamsiz. "
        "Yangi tanishuvlar va o'zgarishlarni yaxshi ko'rasiz. "
        "Kamchiligi: ba'zan ishni oxirigacha yetkazmay qo'yishingiz mumkin.",
    ),
    "xolerik": (
        "🔥 XOLERIK",
        "Siz energiyali, tez, o'jar va qizg'in odamsiz. Yetakchilikka moyilsiz, "
        "maqsad sari intilasiz. Kamchiligi: jahldorlik va sabrsizlik.",
    ),
    "flegmatik": (
        "🌊 FLEGMATIK",
        "Siz xotirjam, vazmin, ishonchli va barqaror odamsiz. "
        "Hissiyotlaringizni tashqariga kam chiqarasiz, ishni sabr bilan bajarasiz. "
        "Kamchiligi: o'zgarishlarga sekin moslashasiz.",
    ),
    "melanxolik": (
        "🌧 MELANXOLIK",
        "Siz sezgir, chuqur his qiladigan, mulohazali odamsiz. "
        "Yaxshi tahlil qilasiz, ammo tez ta'sirlanasiz va tashvishlanasiz. "
        "Kamchiligi: o'ziga ishonchning pastligi.",
    ),
}


# ------------------------------------------------------------------
# MA'LUMOTLAR BAZASI (progress saqlanadi -> Telegramdan chiqib ketsangiz ham davom etadi)
# ------------------------------------------------------------------
def db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                answers TEXT NOT NULL DEFAULT '[]',
                finished INTEGER NOT NULL DEFAULT 0,
                result TEXT
            )"""
        )


def get_user(user_id):
    with db() as c:
        row = c.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        if row is None:
            c.execute("INSERT INTO users(user_id) VALUES (?)", (user_id,))
            return {"answers": [], "finished": 0, "result": None}
        return {
            "answers": json.loads(row["answers"]),
            "finished": row["finished"],
            "result": row["result"],
        }


def save_user(user_id, answers, finished=0, result=None):
    with db() as c:
        c.execute(
            "UPDATE users SET answers=?, finished=?, result=? WHERE user_id=?",
            (json.dumps(answers), finished, result, user_id),
        )


# ------------------------------------------------------------------
# HISOBLASH
# ------------------------------------------------------------------
def calculate(answers):
    """answers: 57 ta element, 1 = Ha, 0 = Yo'q"""
    e = n = lie = 0
    for i, a in enumerate(answers, start=1):
        if i in E_YES and a == 1:
            e += 1
        if i in E_NO and a == 0:
            e += 1
        if i in N_YES and a == 1:
            n += 1
        if i in L_YES and a == 1:
            lie += 1
        if i in L_NO and a == 0:
            lie += 1

    extravert = e > 12
    nervous = n > 12
    if extravert and not nervous:
        key = "sanguinik"
    elif extravert and nervous:
        key = "xolerik"
    elif not extravert and not nervous:
        key = "flegmatik"
    else:
        key = "melanxolik"
    return e, n, lie, key


def result_text(answers):
    e, n, lie, key = calculate(answers)
    title, desc = TEMPERAMENTS[key]
    text = (
        f"✅ Test tugadi!\n\n"
        f"Sizning temperamentingiz: {title}\n\n{desc}\n\n"
        f"📊 Natijalar:\n"
        f"• Ekstraversiya: {e}/24 ({'ekstravert' if e > 12 else 'introvert'})\n"
        f"• Nevrotizm: {n}/24 ({'yuqori' if n > 12 else 'past'})\n"
        f"• Samimiylik (yolg'on shkalasi): {lie}/9"
    )
    if lie > 4:
        text += "\n\n⚠️ Yolg'on shkalasi yuqori: javoblar to'liq samimiy bo'lmagan bo'lishi mumkin."
    text += "\n\nQaytadan topshirish: /start"
    return text, key


# ------------------------------------------------------------------
# TUGMALAR
# ------------------------------------------------------------------
def question_kb(idx):
    rows = [[
        InlineKeyboardButton(text="✅ Ha", callback_data=f"a:{idx}:1"),
        InlineKeyboardButton(text="❌ Yo'q", callback_data=f"a:{idx}:0"),
    ]]
    if idx > 0:
        rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"back:{idx}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def question_text(idx):
    done = idx
    bar = "▓" * (done * 10 // 57) + "░" * (10 - done * 10 // 57)
    return f"Savol {idx + 1}/57\n{bar}\n\n{QUESTIONS[idx]}"


def one_button(text, data):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, callback_data=data)]])


# ------------------------------------------------------------------
# BOT
# ------------------------------------------------------------------
dp = Dispatcher()


@dp.message(CommandStart())
async def start(m: Message):
    user = get_user(m.from_user.id)
    answered = len(user["answers"])

    if 0 < answered < 57 and not user["finished"]:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"▶️ Davom ettirish ({answered}/57)", callback_data="continue")],
            [InlineKeyboardButton(text="🔄 Qaytadan boshlash", callback_data="restart")],
        ])
        await m.answer(
            f"Qaytganingiz bilan! Siz testni {answered}-savolgacha topshirgansiz. Davom etamizmi?",
            reply_markup=kb,
        )
        return

    await m.answer(
        "👋 Assalomu alaykum!\n\n"
        "Bu bot sizning temperamentingizni aniqlaydi (Eysenck testi).\n"
        "📝 Jami 57 ta savol. Har biriga \"Ha\" yoki \"Yo'q\" deb javob bering.\n"
        "💾 Telegramdan chiqib ketsangiz ham, javoblaringiz saqlanadi — keyin davom ettirasiz.\n\n"
        "Tayyormisiz?",
        reply_markup=one_button("🚀 Testni boshlash", "restart"),
    )


@dp.message(Command("result"))
async def last_result(m: Message):
    user = get_user(m.from_user.id)
    if user["finished"] and len(user["answers"]) == 57:
        text, _ = result_text(user["answers"])
        await m.answer(text)
    else:
        await m.answer("Siz hali testni tugatmagansiz. /start ni bosing.")


@dp.callback_query(F.data == "restart")
async def restart(c: CallbackQuery):
    save_user(c.from_user.id, [], 0, None)
    await c.message.edit_text(question_text(0), reply_markup=question_kb(0))
    await c.answer()


@dp.callback_query(F.data == "continue")
async def cont(c: CallbackQuery):
    user = get_user(c.from_user.id)
    idx = len(user["answers"])
    if idx >= 57:
        await c.answer()
        return
    await c.message.edit_text(question_text(idx), reply_markup=question_kb(idx))
    await c.answer()


@dp.callback_query(F.data.startswith("a:"))
async def answer(c: CallbackQuery):
    _, idx_s, val_s = c.data.split(":")
    idx, val = int(idx_s), int(val_s)

    user = get_user(c.from_user.id)
    answers = user["answers"]

    # Eski/ikki marta bosilgan tugmalardan himoya
    if idx != len(answers):
        await c.answer("Bu savol allaqachon javob olgan.")
        if len(answers) < 57:
            await c.message.edit_text(
                question_text(len(answers)), reply_markup=question_kb(len(answers))
            )
        return

    answers.append(val)

    if len(answers) == 57:
        text, key = result_text(answers)
        save_user(c.from_user.id, answers, 1, key)
        await c.message.edit_text(text)
    else:
        save_user(c.from_user.id, answers, 0, None)
        nxt = len(answers)
        await c.message.edit_text(question_text(nxt), reply_markup=question_kb(nxt))
    await c.answer()


@dp.callback_query(F.data.startswith("back:"))
async def back(c: CallbackQuery):
    user = get_user(c.from_user.id)
    answers = user["answers"]
    if answers:
        answers.pop()
        save_user(c.from_user.id, answers, 0, None)
    idx = len(answers)
    await c.message.edit_text(question_text(idx), reply_markup=question_kb(idx))
    await c.answer()


async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()
    bot = Bot(TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
