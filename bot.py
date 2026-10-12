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

# ── چنل اجباری ──
FORCE_CHANNEL = "@VOICKAL_DOIF"
CHANNEL_LINK = "https://rubika.ir/VOICKAL_DOIF"

# ── فایل دیتابیس ──
DB_FILE = "users_db.json"

# ── تنظیمات پیش‌فرض کاربر ──
DEFAULT_USER = {
    "font": "bold",
    "prefix": "𓄂 ‌",
    "suffix": " ♡𝑫𝑶𝑳𝑭𓆃",
    "verified": False,
}

# ── لیست دستورات معتبر ──
COMMANDS = [
    "start", "fonts", "setfont", "templates", "settemplate",
    "settag", "setprefix", "setsuffix", "mytag", "reset",
    "cancel", "verify", "help"
]


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
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(user_id):
    db = load_db()
    user = db.get(str(user_id), DEFAULT_USER.copy())
    for k, v in DEFAULT_USER.items():
        if k not in user:
            user[k] = v
    return user


def set_user(user_id, data):
    db = load_db()
    db[str(user_id)] = data
    save_db(db)


# ═══════════════════════════════════════════
# توابع کمکی
# ═══════════════════════════════════════════

def build_tag(name, user):
    name = name.strip()
    if not name:
        return None
    converted = convert(name, user.get("font", "bold"))
    return f"{user.get('prefix','')}{converted}{user.get('suffix','')}"


async def is_member(client, user_id):
    """چک عضویت در چنل اجباری"""
    try:
        member = await client.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status not in ["left", "kicked"]
    except Exception as e:
        print("⚠️ خطا در چک عضویت:", e)
        return False


async def check_force_join(client, message):
    """اگه کاربر عضو نبود، پیام بده و False برگردون"""
    user = get_user(message.sender_id)
    if user.get("verified"):
        return True

    if await is_member(client, message.sender_id):
        user["verified"] = True
        set_user(message.sender_id, user)
        return True

    await message.reply(
        "🔒 **برای استفاده از ربات، اول در چنل ما عضو شو:**\n\n"
        f"📢 {FORCE_CHANNEL}\n"
        f"🔗 {CHANNEL_LINK}\n\n"
        "بعد از عضویت، دستور `/verify` رو بزن."
    )
    return False


# ═══════════════════════════════════════════
# دستورات
# ═══════════════════════════════════════════

@app.on_message(filters.command("start"))
async def cmd_start(client, message):
    if not await check_force_join(client, message):
        return
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


@app.on_message(filters.command("verify"))
async def cmd_verify(client, message):
    if await is_member(client, message.sender_id):
        user = get_user(message.sender_id)
        user["verified"] = True
        set_user(message.sender_id, user)
        await message.reply("✅ عضویتت تأیید شد! حالا می‌تونی از ربات استفاده کنی.\n\n`/start` رو بزن.")
    else:
        await message.reply(
            "❌ هنوز عضو نشدی!\n\n"
            f"📢 {FORCE_CHANNEL}\n"
            f"🔗 {CHANNEL_LINK}\n\n"
            "بعد از عضویت، دوباره `/verify` رو بزن."
        )


@app.on_message(filters.command("fonts"))
async def cmd_fonts(client, message):
    if not await check_force_join(client, message):
        return
    sample = "arsam"
    lines = ["🔤 **فونت‌های موجود:**\n"]
    for key in FONTS.keys():
        lines.append(f"• `{key}` → {convert(sample, key)}")
    lines.append("\n📌 برای تغییر: `/setfont bold`")
    await message.reply("\n".join(lines))


@app.on_message(filters.command("setfont"))
async def cmd_setfont(client, message):
    if not await check_force_join(client, message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ مثال:\n`/setfont bold`")
        return
    font_name = args[1].strip().lower()
    if font_name not in FONTS:
        await message.reply(f"❌ فونت `{font_name}` وجود نداره.\nاز `/fonts` لیست رو ببین.")
        return
    user = get_user(message.sender_id)
    user["font"] = font_name
    set_user(message.sender_id, user)
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
    if not await check_force_join(client, message):
        return
    lines = ["🎨 **قالب‌های آماده:**\n"]
    for key, t in TEMPLATES.items():
        lines.append(f"• `{key}` — {t['name']}")
    lines.append("\n📌 برای تغییر: `/settemplate dolf`")
    await message.reply("\n".join(lines))


@app.on_message(filters.command("settemplate"))
async def cmd_settemplate(client, message):
    if not await check_force_join(client, message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ مثال:\n`/settemplate dolf`")
        return
    tpl_name = args[1].strip().lower()
    if tpl_name not in TEMPLATES:
        await message.reply(f"❌ قالب `{tpl_name}` وجود نداره.\nاز `/templates` ببین.")
        return
    tpl = TEMPLATES[tpl_name]
    user = get_user(message.sender_id)
    user["prefix"] = tpl["prefix"]
    user["suffix"] = tpl["suffix"]
    user["font"] = tpl["font"]
    set_user(message.sender_id, user)
    await message.reply(
        f"✅ قالب `{tpl['name']}` فعال شد.\n\n"
        f"نمونه:\n{build_tag('arsam', user)}"
    )


@app.on_message(filters.command("settag"))
async def cmd_settag(client, message):
    if not await check_force_join(client, message):
        return
    await message.reply(
        "🎓 **حالت یادگیری قالب**\n\n"
        "یه نمونه تگ از قالب دلخواهت بفرست.\n"
        "جای اسمت رو با کلمه‌ی `NAME` مشخص کن.\n\n"
        "📌 **مثال:**\n"
        "`𓆩 𝑁𝐴𝑀𝐸 𓆪`\n"
        "`『 𝑁𝐴𝑀𝐸 』`\n"
        "`⇣☻⇡ 𝑁𝐴𝑀𝐸 ☾❼❽☽`\n\n"
        "بعد از یادگیری، هر اسمی بفرستی با همین قالب تگ می‌شه."
    )


@app.on_message(filters.command("setprefix"))
async def cmd_setprefix(client, message):
    if not await check_force_join(client, message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ مثال:\n`/setprefix 𓄂 ‌`")
        return
    user = get_user(message.sender_id)
    user["prefix"] = args[1]
    set_user(message.sender_id, user)
    await message.reply(f"✅ پیشوند تغییر کرد.\n\nنمونه:\n{build_tag('arsam', user)}")


@app.on_message(filters.command("setsuffix"))
async def cmd_setsuffix(client, message):
    if not await check_force_join(client, message):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ مثال:\n`/setsuffix ♡𝑫𝑶𝑳𝑭𓆃`")
        return
    user = get_user(message.sender_id)
    user["suffix"] = args[1]
    set_user(message.sender_id, user)
    await message.reply(f"✅ پسوند تغییر کرد.\n\nنمونه:\n{build_tag('arsam', user)}")


@app.on_message(filters.command("mytag"))
async def cmd_mytag(client, message):
    if not await check_force_join(client, message):
        return
    user = get_user(message.sender_id)
    await message.reply(
        f"📌 **تنظیمات فعلی تو:**\n\n"
        f"🔤 فونت: `{user['font']}`\n"
        f"🎨 پیشوند: `{user['prefix']}`\n"
        f"🎨 پسوند: `{user['suffix']}`\n\n"
        f"نمونه:\n{build_tag('arsam', user)}"
    )


@app.on_message(filters.command("reset"))
async def cmd_reset(client, message):
    if not await check_force_join(client, message):
        return
    new_user = DEFAULT_USER.copy()
    new_user["verified"] = True
    set_user(message.sender_id, new_user)
    await message.reply("✅ همه‌چیز به حالت پیش‌فرض برگشت.")


@app.on_message(filters.command("cancel"))
async def cmd_cancel(client, message):
    await message.reply("❌ عملیات لغو شد.")


@app.on_message(filters.command("help"))
async def cmd_help(client, message):
    if not await check_force_join(client, message):
        return
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

    # اگه دستور معتبر بود، رد کن
    if text.startswith("/"):
        cmd = text.split()[0][1:].lower()
        if cmd in COMMANDS:
            return
        text = text.lstrip("/").strip()
        if not text:
            return

    # چک عضویت اجباری
    if not await check_force_join(client, message):
        return

    user = get_user(message.sender_id)

    # ── حالت یادگیری قالب ──
    if "NAME" in text:
        parts = text.split("NAME", 1)
        user["prefix"] = parts[0]
        user["suffix"] = parts[1] if len(parts) > 1 else ""
        set_user(message.sender_id, user)
        await message.reply(
            f"🎓 **قالب یاد گرفته شد!**\n\n"
            f"پیشوند: `{user['prefix']}`\n"
            f"پسوند: `{user['suffix']}`\n\n"
            f"نمونه:\n{build_tag('مریم', user)}\n{build_tag('arsam', user)}"
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
