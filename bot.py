import os
import json
from nicotin import Client, filters
from fonts import convert, FONTS

# ═══════════════════════════════════════════
# تنظیمات
# ═══════════════════════════════════════════

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN تنظیم نشده!")

app = Client(bot_token=BOT_TOKEN)

# ── کش در حافظه ──
_user_cache = {}

# ── فایل دیتابیس ──
DB_FILE = "users_db.json"

# ── تنظیمات پیش‌فرض کاربر ──
DEFAULT_USER = {
    "font": "bold",
    "prefix": "𓄂 ‌",
    "suffix": " ♡𝑫𝑶𝑳𝑭𓆃",
}

# ── کلمات جایگزین برای NAME ──
PLACEHOLDER_WORDS = ["Name", "NAME", "name", "اسم"]

# ── لیست دستورات معتبر ──
COMMANDS = [
    "start", "fonts", "setfont", "templates", "settemplate",
    "settag", "setprefix", "setsuffix", "mytag", "reset",
    "cancel", "help"
]


# ═══════════════════════════════════════════
# تابع کمکی برای گرفتن آیدی فرستنده
# ═══════════════════════════════════════════

def get_sender_id(message):
    """آیدی فرستنده رو از ویژگی‌های واقعی nicotin بگیر"""
    # ⭐ chat_id مستقیم (توی چت خصوصی همون user_id هست)
    try:
        if hasattr(message, "chat_id") and message.chat_id:
            return str(message.chat_id)
    except Exception:
        pass
    
    # ⭐ from_user (ممکنه آبجکت باشه یا آیدی مستقیم)
    try:
        if hasattr(message, "from_user") and message.from_user:
            # اگه آبجکت بود و id داشت
            if hasattr(message.from_user, "id"):
                return str(message.from_user.id)
            # اگه خودش آیدی بود
            return str(message.from_user)
    except Exception:
        pass
    
    # از id پیام به عنوان آخرین راه
    try:
        if hasattr(message, "id") and message.id:
            return str(message.id)
    except Exception:
        pass
    
    print("⚠️ نتونستم آیدی رو بگیرم. ویژگی‌ها:", dir(message))
    return None


# ═══════════════════════════════════════════
# دیتابیس
# ═══════════════════════════════════════════

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("⚠️ خطا در ذخیره فایل:", e)


def get_user(user_id):
    if user_id is None:
        return DEFAULT_USER.copy()
    
    user_id = str(user_id)
    
    if user_id in _user_cache:
        return _user_cache[user_id].copy()
    
    db = load_db()
    user = db.get(user_id, DEFAULT_USER.copy())
    for k, v in DEFAULT_USER.items():
        if k not in user:
            user[k] = v
    
    _user_cache[user_id] = user.copy()
    return user


def set_user(user_id, data):
    if user_id is None:
        print("⚠️ user_id None بود، ذخیره نشد!")
        return
    
    user_id = str(user_id)
    _user_cache[user_id] = data.copy()
    print(f"💾 ذخیره شد برای {user_id}: prefix={data.get('prefix')}, suffix={data.get('suffix')}")
    
    try:
        db = load_db()
        db[user_id] = data
        save_db(db)
    except Exception as e:
        print("⚠️ خطا در ذخیره:", e)


# ═══════════════════════════════════════════
# توابع کمکی
# ═══════════════════════════════════════════

def build_tag(name, user):
    name = name.strip()
    if not name:
        return None
    converted = convert(name, user.get("font", "bold"))
    return f"{user.get('prefix','')}{converted}{user.get('suffix','')}"


def find_placeholder(text):
    for word in PLACEHOLDER_WORDS:
        if word in text:
            return word
    return None


# ═══════════════════════════════════════════
# دستورات
# ═══════════════════════════════════════════

@app.on_message(filters.command("start"))
async def cmd_start(client, message):
    await message.reply(
        "🎨 **ربات تگ‌ساز حرفه‌ای**\n\n"
        "کافیه اسمت رو بفرستی تا تگ بگیری:\n"
        "• `مریم` → 𓄂 ‌مریم ♡𝑫𝑶𝑳𝑭𓆃\n"
        "• `arsam` → 𓄂 ‌𝐚𝐫𝐬𝐚𝐦 ♡𝑫𝑶𝑳𝑭𓆃\n\n"
        "📋 **دستورات:**\n"
        "/fonts — لیست فونت‌ها\n"
        "/setfont — تغییر فونت\n"
        "/templates — قالب‌های آماده\n"
        "/settemplate — تغییر قالب\n"
        "/settag — تنظیم قالب دلخواه\n"
        "/setprefix — تغییر پیشوند\n"
        "/setsuffix — تغییر پسوند\n"
        "/mytag — تگ فعلی تو\n"
        "/reset — برگشت به پیش‌فرض\n"
        "/help — راهنما"
    )


@app.on_message(filters.command("fonts"))
async def cmd_fonts(client, message):
    sample = "arsam"
    lines = ["🔤 **فونت‌های موجود:**\n"]
    for key in FONTS.keys():
        lines.append(f"• `{key}` → {convert(sample, key)}")
    lines.append("\n📌 برای تغییر: `/setfont bold`")
    await message.reply("\n".join(lines))


@app.on_message(filters.command("setfont"))
async def cmd_setfont(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ مثال:\n`/setfont bold`")
        return
    font_name = args[1].strip().lower()
    if font_name not in FONTS:
        await message.reply(f"❌ فونت `{font_name}` وجود نداره.\nاز `/fonts` لیست رو ببین.")
        return
    user_id = get_sender_id(message)
    user = get_user(user_id)
    user["font"] = font_name
    set_user(user_id, user)
    await message.reply(
        f"✅ فونت به `{font_name}` تغییر کرد.\n\n"
        f"نمونه:\n{convert('arsam', font_name)}"
    )


# ── قالب‌های آماده ──
TEMPLATES = {
    "dolf": {
        "name": "قالب DOLF",
        "prefix": "𓄂 ‌",
        "suffix": " ♡𝑫𝑶𝑳𝑭𓆃",
        "font": "bold",
    },
    "arsam": {
        "name": "قالب ARSAM",
        "prefix": "𓄂 ‌",
        "suffix": " ♡𝑫𝑶𝑳𝑭𓆃",
        "font": "bold",
    },
}


@app.on_message(filters.command("templates"))
async def cmd_templates(client, message):
    lines = ["🎨 **قالب‌های آماده:**\n"]
    for key, t in TEMPLATES.items():
        lines.append(f"• `{key}` — {t['name']}")
    lines.append("\n📌 برای تغییر: `/settemplate dolf`")
    await message.reply("\n".join(lines))


@app.on_message(filters.command("settemplate"))
async def cmd_settemplate(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ مثال:\n`/settemplate dolf`")
        return
    tpl_name = args[1].strip().lower()
    if tpl_name not in TEMPLATES:
        await message.reply(f"❌ قالب `{tpl_name}` وجود نداره.\nاز `/templates` ببین.")
        return
    tpl = TEMPLATES[tpl_name]
    user_id = get_sender_id(message)
    user = get_user(user_id)
    user["prefix"] = tpl["prefix"]
    user["suffix"] = tpl["suffix"]
    user["font"] = tpl["font"]
    set_user(user_id, user)
    await message.reply(
        f"✅ قالب `{tpl['name']}` فعال شد.\n\n"
        f"نمونه:\n{build_tag('arsam', user)}"
    )


@app.on_message(filters.command("settag"))
async def cmd_settag(client, message):
    await message.reply(
        "🎓 **حالت یادگیری قالب**\n\n"
        "یه نمونه تگ از قالب دلخواهت بفرست.\n"
        "جای اسمت رو با کلمه‌ی `Name` مشخص کن.\n\n"
        "📌 **مثال:**\n"
        "`𓆩 Name 𓆪`\n"
        "`『 Name 』`\n"
        "`⇣☻⇡ Name ☾❼❽☽`\n\n"
        "💡 می‌تونی از `NAME`، `name` یا `اسم` هم استفاده کنی."
    )


@app.on_message(filters.command("setprefix"))
async def cmd_setprefix(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ مثال:\n`/setprefix 𓄂 ‌`")
        return
    user_id = get_sender_id(message)
    user = get_user(user_id)
    user["prefix"] = args[1]
    set_user(user_id, user)
    await message.reply(f"✅ پیشوند تغییر کرد.\n\nنمونه:\n{build_tag('arsam', user)}")


@app.on_message(filters.command("setsuffix"))
async def cmd_setsuffix(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ مثال:\n`/setsuffix ♡𝑫𝑶𝑳𝑭𓆃`")
        return
    user_id = get_sender_id(message)
    user = get_user(user_id)
    user["suffix"] = args[1]
    set_user(user_id, user)
    await message.reply(f"✅ پسوند تغییر کرد.\n\nنمونه:\n{build_tag('arsam', user)}")


@app.on_message(filters.command("mytag"))
async def cmd_mytag(client, message):
    user_id = get_sender_id(message)
    user = get_user(user_id)
    await message.reply(
        f"📌 **تنظیمات فعلی تو:**\n\n"
        f"🔤 فونت: `{user['font']}`\n"
        f"🎨 پیشوند: `{user['prefix']}`\n"
        f"🎨 پسوند: `{user['suffix']}`\n\n"
        f"نمونه:\n{build_tag('arsam', user)}"
    )


@app.on_message(filters.command("reset"))
async def cmd_reset(client, message):
    user_id = get_sender_id(message)
    set_user(user_id, DEFAULT_USER.copy())
    await message.reply("✅ همه‌چیز به حالت پیش‌فرض برگشت.")


@app.on_message(filters.command("cancel"))
async def cmd_cancel(client, message):
    await message.reply("❌ عملیات لغو شد.")


@app.on_message(filters.command("help"))
async def cmd_help(client, message):
    await message.reply(
        "📖 **راهنمای ربات**\n\n"
        "🎯 فقط اسمت رو بفرست تا تگ بگیری!\n\n"
        "**دستورات:**\n"
        "• /fonts — لیست فونت‌ها\n"
        "• /setfont bold — تغییر فونت\n"
        "• /templates — قالب‌های آماده\n"
        "• /settemplate dolf — تغییر قالب\n"
        "• /settag — تنظیم قالب دلخواه\n"
        "• /setprefix — تغییر پیشوند\n"
        "• /setsuffix — تغییر پسوند\n"
        "• /mytag — تگ فعلی\n"
        "• /reset — برگشت به پیش‌فرض"
    )


# ═══════════════════════════════════════════
# هندلر اصلی — هر متن ساده
# ═══════════════════════════════════════════

@app.on_message()
async def handle_text(client, message):
    text = message.text
    if not text:
        return

    text = text.strip()
    if not text:
        return

    if text.startswith("/"):
        cmd = text.split()[0][1:].lower()
        if cmd in COMMANDS:
            return
        text = text.lstrip("/").strip()
        if not text:
            return

    user_id = get_sender_id(message)
    print(f"📩 پیام از کاربر: {user_id} | متن: {text[:40]}")
    
    user = get_user(user_id)

    # ── حالت یادگیری قالب ──
    placeholder = find_placeholder(text)
    if placeholder:
        parts = text.split(placeholder, 1)
        user["prefix"] = parts[0]
        user["suffix"] = parts[1] if len(parts) > 1 else ""
        set_user(user_id, user)
        await message.reply(
            f"🎓 **قالب یاد گرفته شد!**\n\n"
            f"پیشوند: `{user['prefix']}`\n"
            f"پسوند: `{user['suffix']}`\n\n"
            f"نمونه:\n{build_tag('مریم', user)}\n{build_tag('arsam', user)}\n\n"
            f"✅ از این به بعد هر اسمی بفرستی با همین قالب تگ می‌شه."
        )
        return

    # ── ساخت تگ ──
    tag = build_tag(text, user)
    if tag:
        await message.reply(tag)
        print("✅ فرستاده شد:", tag)


# ═══════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════

if __name__ == "__main__":
    print("🤖 ربات فعال شد...")
    app.run()
