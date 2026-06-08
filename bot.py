import asyncio
import aiohttp
import json
import os
import random
import platform
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# ======================== CONFIGURATION ========================
BOT_TOKEN = "8995249684:AAG-ekXYja1CtUjEN4Qfi_UxlPVXlDvQUwM"
OWNER_ID = 8066199853
OWNER_USERNAME = "@TheownerDev"
BOT_USERNAME = "DevXFXBot"

BOT_NAME = "🦋⃟‌⃟ 𝕯єν X FX BOT"
START_IMAGE = "https://i.ibb.co/0RwPFqKL/8d547eeed99e12413c4d58780b33c9cd.jpg"

REQUIRED_CHATS = []
USER_DATA_FILE = "user_data.json"

TOKEN_PRICES = [
    {"tokens": 50, "price": "₹50"},
    {"tokens": 120, "price": "₹100"},
    {"tokens": 250, "price": "₹200"},
    {"tokens": 650, "price": "₹500"},
    {"tokens": 1400, "price": "₹1000"},
]

WAITING_FOR_INPUT = 1

# ======================== SYSTEM INFO (Without psutil) ========================
def get_system_info():
    try:
        info = f"""
<b>🤖 SYSTEM INFORMATION</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🖥️ System:</b> {platform.system()} {platform.release()}
<b>🐍 Python:</b> {sys.version.split()[0]}
<b>👥 Users:</b> {len(user_data)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return info
    except:
        return ""

# ======================== DATA HANDLERS ========================
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user_data(data):
    try:
        with open(USER_DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except:
        pass

user_data = load_user_data()

def init_user(user_id, username=None, referrer_id=None):
    uid = str(user_id)
    if uid not in user_data:
        user_data[uid] = {
            "tokens": 10,
            "username": username,
            "referrals": 0,
            "referred_by": referrer_id,
            "joined": str(datetime.now()),
        }
        save_user_data(user_data)
        if referrer_id and referrer_id != user_id and str(referrer_id) in user_data:
            user_data[str(referrer_id)]["tokens"] += 10
            user_data[str(referrer_id)]["referrals"] += 1
            save_user_data(user_data)
        return True
    return False

def get_user_tokens(user_id):
    return user_data.get(str(user_id), {}).get("tokens", 0)

def deduct_token(user_id):
    uid = str(user_id)
    if uid in user_data and user_data[uid]["tokens"] > 0:
        user_data[uid]["tokens"] -= 1
        save_user_data(user_data)
        return True
    return False

def add_tokens(user_id, amount):
    uid = str(user_id)
    if uid in user_data:
        user_data[uid]["tokens"] += amount
        save_user_data(user_data)
        return True
    return False

def set_tokens(user_id, amount):
    uid = str(user_id)
    if uid in user_data:
        user_data[uid]["tokens"] = amount
        save_user_data(user_data)
        return True
    return False

def get_referral_link(user_id):
    return f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"

# ======================== API HANDLER ========================
async def fetch_api(url: str, retry_count=2) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    
    for attempt in range(retry_count):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=12) as resp:
                    if resp.status == 200:
                        try:
                            text = await resp.text()
                            data = json.loads(text) if text else {}
                            if data:
                                return data
                            return {"error": "No data found"}
                        except:
                            return {"error": "Invalid JSON"}
                    else:
                        return {"error": f"HTTP {resp.status}"}
        except asyncio.TimeoutError:
            if attempt == retry_count - 1:
                return {"error": "Request timeout"}
        except Exception as e:
            if attempt == retry_count - 1:
                return {"error": str(e)[:50]}
        await asyncio.sleep(1)
    
    return {"error": "Failed after retries"}

# ======================== COMMAND HANDLERS ========================
async def start(update: Update, context):
    user = update.effective_user
    referrer_id = None
    
    if context.args and context.args[0].startswith("ref_"):
        try:
            referrer_id = int(context.args[0][4:])
            if referrer_id == user.id:
                referrer_id = None
        except:
            pass
    
    init_user(user.id, user.username, referrer_id)
    tokens = get_user_tokens(user.id)
    system_info = get_system_info()
    
    caption = f"""<b>✨ Welcome to {BOT_NAME} ✨</b>

<b>👤 User:</b> {user.first_name}
<b>💎 Tokens:</b> <code>{tokens}</code>

{system_info}

<b>📌 Use /menu to see all commands</b>

👑 <b>Owner:</b> {OWNER_USERNAME}
"""
    
    try:
        await update.message.reply_photo(photo=START_IMAGE, caption=caption, parse_mode="HTML")
    except:
        await update.message.reply_text(caption, parse_mode="HTML")

async def menu(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("📱 Mobile Number", callback_data="cmd_num"),
         InlineKeyboardButton("👤 Telegram ID", callback_data="cmd_tg")],
        [InlineKeyboardButton("🌐 IP Address", callback_data="cmd_ip"),
         InlineKeyboardButton("👨‍👩‍👧 Ration Card", callback_data="cmd_family")],
        [InlineKeyboardButton("📍 Pincode", callback_data="cmd_pincode"),
         InlineKeyboardButton("🔐 FFUID", callback_data="cmd_ffuid")],
        [InlineKeyboardButton("🆔 Aadhar Card", callback_data="cmd_aadhar"),
         InlineKeyboardButton("🏢 GST Number", callback_data="cmd_gst")],
        [InlineKeyboardButton("🚗 Vehicle RC", callback_data="cmd_rc2")],
        [InlineKeyboardButton("💎 My Tokens", callback_data="cmd_tokens"),
         InlineKeyboardButton("👤 My Profile", callback_data="cmd_profile")],
        [InlineKeyboardButton("🔗 Referral Link", callback_data="cmd_refer"),
         InlineKeyboardButton("💰 Buy Tokens", callback_data="cmd_buy")],
    ]
    
    text = f"""<b>✨ {BOT_NAME} - Main Menu ✨</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 <b>Balance:</b> <code>{get_user_tokens(update.effective_user.id)}</code> tokens
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 <i>Each query costs 1 token</i>"""
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)

async def private_only(update: Update, context):
    if update.effective_chat.type != "private":
        await update.message.reply_text("❌ This bot works only in private chat.")
        return False
    return True

async def command_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    command = query.data.replace("cmd_", "")
    context.user_data['pending_command'] = command
    
    if command in ["tokens", "profile", "refer", "buy"]:
        await query.message.delete()
        if command == "tokens":
            await my_tokens(update, context)
        elif command == "profile":
            await profile(update, context)
        elif command == "refer":
            await refer(update, context)
        elif command == "buy":
            await buy(update, context)
        return
    
    messages = {
        "num": "📱 Send <b>mobile number</b>\nExample: <code>9876543210</code>",
        "tg": "👤 Send <b>Telegram user ID</b>\nExample: <code>123456789</code>",
        "ip": "🌐 Send <b>IP address</b>\nExample: <code>8.8.8.8</code>",
        "family": "👨‍👩‍👧 Send <b>Ration Card ID</b>",
        "pincode": "📍 Send <b>Pincode</b>\nExample: <code>110001</code>",
        "ffuid": "🔐 Send <b>FFUID</b>",
        "aadhar": "🆔 Send <b>Aadhar Number</b>",
        "gst": "🏢 Send <b>GST Number</b>",
        "rc2": "🚗 Send <b>Vehicle Number</b>",
    }
    
    if command in messages:
        await query.message.edit_text(
            messages[command],
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel_input")]])
        )
        return WAITING_FOR_INPUT
    
    return ConversationHandler.END

async def handle_input(update: Update, context):
    user_input = update.message.text.strip()
    command = context.user_data.get('pending_command')
    user_id = update.effective_user.id
    
    if not command:
        return ConversationHandler.END
    
    if get_user_tokens(user_id) <= 0:
        await update.message.reply_text("❌ Insufficient tokens!", parse_mode="HTML")
        await menu(update, context)
        return ConversationHandler.END
    
    processing = await update.message.reply_text("🔄 Processing...", parse_mode="HTML")
    
    if command == "ip":
        api_url = f"http://ip-api.com/json/{user_input}?fields=66842623"
    elif command == "pincode":
        api_url = f"https://api.postalpincode.in/pincode/{user_input}"
    else:
        api_url = f"https://shivam-ultra-api.vercel.app/{command}?key=Y&num={user_input}"
    
    await processing.delete()
    
    if api_url and deduct_token(user_id):
        data = await fetch_api(api_url)
        
        if not data or "error" in data:
            await update.message.reply_text(f"❌ No information found for {user_input}", parse_mode="HTML")
        elif command == "ip" and data.get("status") == "success":
            result = f"""🌐 <b>IP INFORMATION</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 <b>IP:</b> <code>{data.get('query', 'N/A')}</code>
🗺️ <b>Country:</b> {data.get('country', 'N/A')}
🏙️ <b>Region:</b> {data.get('regionName', 'N/A')}
🌆 <b>City:</b> {data.get('city', 'N/A')}
📍 <b>Zip:</b> {data.get('zip', 'N/A')}
📡 <b>ISP:</b> {data.get('isp', 'N/A')}"""
            await update.message.reply_text(result, parse_mode="HTML")
        elif command == "pincode" and isinstance(data, list) and data and data[0].get("Status") == "Success":
            posts = data[0].get("PostOffice", [])
            if posts:
                result = f"📍 <b>PINCODE: {user_input}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                for po in posts[:3]:
                    result += f"🏣 <b>{po.get('Name', 'N/A')}</b>\n"
                    result += f"   📍 District: {po.get('District', 'N/A')}\n"
                    result += f"   🗺️ State: {po.get('State', 'N/A')}\n"
                    result += f"   📮 Pincode: {po.get('Pincode', 'N/A')}\n\n"
                await update.message.reply_text(result, parse_mode="HTML")
            else:
                await update.message.reply_text(f"❌ No data for pincode: {user_input}", parse_mode="HTML")
        else:
            await update.message.reply_text("❌ No information found", parse_mode="HTML")
    else:
        await update.message.reply_text("❌ Insufficient tokens!", parse_mode="HTML")
    
    await menu(update, context)
    return ConversationHandler.END

async def cancel_input(update: Update, context):
    query = update.callback_query
    await query.answer()
    await menu(update, context)
    return ConversationHandler.END

async def verify_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    await menu(update, context)

async def my_tokens(update: Update, context):
    if not await private_only(update, context):
        return
    tokens = get_user_tokens(update.effective_user.id)
    msg = await update.message.reply_text(f"💎 <b>Your Tokens:</b> <code>{tokens}</code>", parse_mode="HTML")
    await asyncio.sleep(2)
    await msg.delete()
    await menu(update, context)

async def refer(update: Update, context):
    if not await private_only(update, context):
        return
    uid = update.effective_user.id
    link = get_referral_link(uid)
    referrals = user_data.get(str(uid), {}).get("referrals", 0)
    text = f"""<b>🔗 Your Referral Link</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<code>{link}</code>

👥 Referred: <b>{referrals}</b> users
💎 Earned: <b>{referrals * 10}</b> tokens"""
    await update.message.reply_text(text, parse_mode="HTML")

async def buy(update: Update, context):
    if not await private_only(update, context):
        return
    keyboard = [[InlineKeyboardButton(f"💎 {item['tokens']} tokens → {item['price']}", callback_data=f"buy_{item['tokens']}_{item['price']}")] for item in TOKEN_PRICES]
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")])
    await update.message.reply_text("<b>💎 Buy Tokens</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nSelect a package:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def buy_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_to_menu":
        await menu(update, context)
        return
    
    _, tokens, price = query.data.split("_", 2)
    user = query.from_user
    
    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=f"<b>🛒 Purchase Request</b>\n\n👤 User: {user.first_name}\n🆔 ID: <code>{user.id}</code>\n💎 Tokens: {tokens}\n💰 Price: {price}",
        parse_mode="HTML"
    )
    
    await query.edit_message_text(
        f"<b>✅ Request Sent!</b>\n\n💰 Price: {price}\n💎 Tokens: {tokens}\n\n📩 Owner: {OWNER_USERNAME}",
        parse_mode="HTML"
    )
    
    await asyncio.sleep(3)
    await menu(update, context)

async def profile(update: Update, context):
    if not await private_only(update, context):
        return
    user = update.effective_user
    uid = str(user.id)
    tokens = get_user_tokens(user.id)
    referrals = user_data.get(uid, {}).get("referrals", 0)
    
    text = f"""<b>👤 YOUR PROFILE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📛 <b>Name:</b> {user.first_name}
🆔 <b>ID:</b> <code>{user.id}</code>
💬 <b>Username:</b> @{user.username if user.username else 'None'}
💎 <b>Tokens:</b> <code>{tokens}</code>
👥 <b>Referrals:</b> {referrals}"""
    
    msg = await update.message.reply_text(text, parse_mode="HTML")
    await asyncio.sleep(3)
    await msg.delete()
    await menu(update, context)

async def help_command(update: Update, context):
    await menu(update, context)

# ======================== ADMIN COMMANDS ========================
async def broadcast(update: Update, context):
    if update.effective_user.id != OWNER_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    msg = " ".join(context.args)
    await update.message.reply_text("📢 Broadcasting...")
    sent = 0
    for uid in user_data.keys():
        try:
            await context.bot.send_message(chat_id=int(uid), text=f"<b>📢 Announcement</b>\n\n{msg}", parse_mode="HTML")
            sent += 1
            await asyncio.sleep(0.05)
        except:
            pass
    await update.message.reply_text(f"✅ Sent to {sent} users.")

async def add_tokens_admin(update: Update, context):
    if update.effective_user.id != OWNER_ID:
        return
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /add_tokens <user_id> <amount>")
        return
    try:
        uid = int(context.args[0])
        amount = int(context.args[1])
        if add_tokens(uid, amount):
            await update.message.reply_text(f"✅ Added {amount} tokens to user {uid}")
        else:
            await update.message.reply_text("❌ User not found")
    except:
        await update.message.reply_text("❌ Invalid input")

async def stats(update: Update, context):
    if update.effective_user.id != OWNER_ID:
        return
    total = len(user_data)
    tokens = sum(u.get("tokens", 0) for u in user_data.values())
    await update.message.reply_text(f"<b>📊 Stats</b>\n\n👥 Users: {total}\n💎 Tokens: {tokens}", parse_mode="HTML")

# ======================== MAIN ========================
def main():
    print(f"🤖 {BOT_NAME} Starting...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(command_callback, pattern="^cmd_")],
        states={WAITING_FOR_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)]},
        fallbacks=[CallbackQueryHandler(cancel_input, pattern="cancel_input")],
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(verify_callback, pattern="check_joined"))
    app.add_handler(CallbackQueryHandler(buy_callback, pattern="^buy_|back_to_menu"))
    app.add_handler(CallbackQueryHandler(cancel_input, pattern="cancel_input"))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("my_tokens", my_tokens))
    app.add_handler(CommandHandler("refer", refer))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("add_tokens", add_tokens_admin))
    app.add_handler(CommandHandler("stats", stats))
    
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
