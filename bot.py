import os
from nicotin import Client, filters
from fonts import convert, FONTS
from database import get_user, set_user
from templates import TEMPLATES

# ── توکن از متغیر محیطی خونده می‌شه ──
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ متغیر BOT_TOKEN تنظیم نشده! توی Railway → Variables اضافه‌اش کن.")

app = Client(bot_token=BOT_TOKEN)

REQUIRED_CHANNELS = ["@your_channel1", "@your_channel2"]
ADMINS = [123456789]


def build_tag(name, user):
    converted = convert(name.strip(), user["font"])
    return f"{user['prefix']}{converted}{user['suffix']}"


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "🎨 **ربات تگ‌ساز حرفه‌ای**\n\n"
        "اسمت رو بفرست تا تگ بسازم:\n"
        "`مریم` → 𓄂 ‌مریم ♡𝑫𝑶𝑳𝑭𓆃\n\n"
        "📋 **دستورات:**\n"
        "/fonts — لیست فونت‌ها\n"
        "/setfont [نام فونت] — تغییر فونت\n"
        "/templates — لیست قالب‌ها\n"
        "/settemplate [نام قالب] — تغییر قالب\n"
        "/mytag — تگ فعلی تو\n"
        "/premium — قالب سفارشی\n"
        "/check — چک عضویت چنل‌ها\n"
        "/help — راهنما"
    )


@app.on_message(filters.command("fonts"))
async def fonts_cmd(client, message):
    sample = "Sullivan"
    lines = ["🔤 **لیست فونت‌های موجود:**\n"]
    for key in FONTS.keys():
        lines.append(f"• `{key}` → {convert(sample, key)}")
    lines.append("\n📌 برای تغییر: `/setfont bold`")
    await message.reply("\n".join(lines))


@app.on_message(filters.command("setfont"))
async def setfont(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ مثال: `/setfont bold`")
        return
    font_name = args[1].strip()
    if font_name not in FONTS:
        await message.reply(f"❌ فونت `{font_name}` وجود نداره.\nاز `/fonts` لیست رو ببین.")
        return
    user = get_user(message.sender_id)
    user["font"] = font_name
    set_user(message.sender_id, user)
    await message.reply(f"✅ فونت به `{font_name}` تغییر کرد.\nنمونه: {convert('Sullivan', font_name)}")


@app.on_message(filters.command("templates"))
async def templates_cmd(client, message):
    lines = ["🎨 **قالب‌های موجود:**\n"]
    for key, t in TEMPLATES.items():
        lock = "🔒" if t["premium"] else "✅"
        lines.append(f"{lock} `{key}` — {t['name']}")
    lines.append("\n📌 برای تغییر: `/settemplate karma`")
    await message.reply("\n".join(lines))


@app.on_message(filters.command("settemplate"))
async def settemplate(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ مثال: `/settemplate karma`")
        return
    tpl_name = args[1].strip()
    if tpl_name not in TEMPLATES:
        await message.reply(f"❌ قالب `{tpl_name}` وجود نداره.\nاز `/templates` لیست رو ببین.")
        return
    tpl = TEMPLATES[tpl_name]
    if tpl["premium"]:
        await message.reply(
            "🔒 این قالب **ویژه** است.\n\n"
            "برای استفاده:\n" +
            "\n".join([f"• {ch}" for ch in REQUIRED_CHANNELS]) +
            "\n\nبعد از عضو شدن، `/check` رو بزن."
        )
        return
    user = get_user(message.sender_id)
    user["prefix"] = tpl["prefix"]
    user["suffix"] = tpl["suffix"]
    user["font"] = tpl["font"]
    set_user(message.sender_id, user)
    await message.reply(f"✅ قالب `{tpl['name']}` فعال شد.\nنمونه:\n{build_tag('Sullivan', user)}")


@app.on_message(filters.command("check"))
async def check(client, message):
    try:
        for ch in REQUIRED_CHANNELS:
            member = await client.get_chat_member(ch, message.sender_id)
            if member.status in ["left", "kicked"]:
                await message.reply(f"❌ هنوز در {ch} عضو نشدی.")
                return
        user = get_user(message.sender_id)
        user["paid"] = True
        set_user(message.sender_id, user)
        await message.reply("✅ عضویتت تأیید شد!")
    except Exception as e:
        await message.reply(f"⚠️ خطا: {e}")


@app.on_message(filters.command("mytag"))
async def mytag(client, message):
    user = get_user(message.sender_id)
    await message.reply(
        f"📌 **تنظیمات فعلی تو:**\n\n"
        f"🔤 فونت: `{user['font']}`\n"
        f"🎨 پیشوند: `{user['prefix']}`\n"
        f"🎨 پسوند: `{user['suffix']}`\n"
        f"💎 پرمیوم: {'✅' if user['paid'] else '❌'}\n\n"
        f"نمونه:\n{build_tag('مریم', user)}"
    )


@app.on_message(filters.command("premium"))
async def premium(client, message):
    await message.reply(
        "💎 **قالب سفارشی**\n\n"
        "با پرمیوم می‌تونی پیشوند و پسوند دلخواه خودت رو بذاری.\n\n"
        "🎁 **رایگان:** عضویت در چنل‌های زیر:\n" +
        "\n".join([f"• {ch}" for ch in REQUIRED_CHANNELS]) +
        "\n\n📌 بعدش `/check` رو بزن."
    )


@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    await message.reply(
        "📖 **راهنما**\n\n"
        "فقط اسمت رو بفرست تا تگ بگیری!\n\n"
        "• /fonts — لیست فونت‌ها\n"
        "• /setfont [نام] — تغییر فونت\n"
        "• /templates — لیست قالب‌ها\n"
        "• /settemplate [نام] — تغییر قالب\n"
        "• /mytag — تگ فعلی\n"
        "• /premium — قالب سفارشی\n"
        "• /check — چک عضویت"
    )


@app.on_message(filters.private & filters.text & ~filters.command([
    "start", "fonts", "setfont", "templates", "settemplate",
    "check", "mytag", "premium", "help"
]))
async def handle_name(client, message):
    text = message.text.strip()
    user = get_user(message.sender_id)
    if "|" in text and (user["paid"] or message.sender_id in ADMINS):
        parts = [p.strip() for p in text.split("|")]
        if len(parts) == 3:
            user["prefix"] = parts[0]
            user["suffix"] = parts[1]
            user["font"] = parts[2] if parts[2] in FONTS else "bold"
            set_user(message.sender_id, user)
            await message.reply(f"✅ قالب سفارشی ذخیره شد.\nنمونه:\n{build_tag('مریم', user)}")
            return
    await message.reply(build_tag(text, user))


if __name__ == "__main__":
    print("🤖 ربات تگ‌ساز فعال شد...")
    app.run()
