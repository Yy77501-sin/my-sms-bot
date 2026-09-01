import os
import sys
import time
import json
import sqlite3
import threading
import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import telebot
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler

# ----------------- استيراد الإعدادات -----------------
try:
    import config
    BOT_TOKEN = getattr(config, 'BOT_TOKEN', '8998307482:AAHlUFDu0E_0ltdVQVEGQ5z2pats24kK3rU').strip()
    HERO_API_KEY = getattr(config, 'HERO_SMS_API_KEY', '67ef5b751b1A4f2bef57dAd7bA2A248c').strip()
    PLUS_API_KEY = getattr(config, 'PLUS_API_KEY', 'PLUS-6c3caa402169433bb15ae1a7').strip()
    PLUS_API_URL = getattr(config, 'PLUS_API_URL', 'https://sms-plus.net/stubs/handler_api.php').strip()
    ADMIN_ID = str(getattr(config, 'ADMIN_ID', '8097770003')).strip()
    SUPPORT_USERNAME = getattr(config, 'SUPPORT_USERNAME', 'Yas_in7').strip()
    CURRENCY = getattr(config, 'CURRENCY', '$').strip()
    
    PROFIT_MARGIN = getattr(config, 'PROFIT_MARGIN', 0.20)
    RUB_PER_USD = getattr(config, 'RUB_PER_USD', 30.0)
    
    MAIN_CHANNEL_URL = getattr(config, 'MAIN_CHANNEL_URL', 'https://t.me/Yas_in7').strip()
    INSTRUCTIONS_CHANNEL_URL = getattr(config, 'INSTRUCTIONS_CHANNEL_URL', 'https://t.me/Yas_in7').strip()
    ACTIVATION_CHANNEL_ID = getattr(config, 'ACTIVATION_CHANNEL_ID', '').strip()
except Exception as e:
    print(f"Config Import Warning: {e}")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8998307482:AAHlUFDu0E_0ltdVQVEGQ5z2pats24kK3rU").strip()
    HERO_API_KEY = os.getenv("HERO_SMS_API_KEY", "67ef5b751b1A4f2bef57dAd7bA2A248c").strip()
    PLUS_API_KEY = os.getenv("PLUS_API_KEY", "PLUS-6c3caa402169433bb15ae1a7").strip()
    PLUS_API_URL = os.getenv("PLUS_API_URL", "https://sms-plus.net/stubs/handler_api.php").strip()
    ADMIN_ID = str(os.getenv("ADMIN_ID", "8097770003")).strip()
    SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "Yas_in7").strip()
    CURRENCY = "$"
    PROFIT_MARGIN = 0.20
    RUB_PER_USD = 30.0
    MAIN_CHANNEL_URL = os.getenv("MAIN_CHANNEL_URL", "https://t.me/Yas_in7").strip()
    INSTRUCTIONS_CHANNEL_URL = os.getenv("INSTRUCTIONS_CHANNEL_URL", "https://t.me/Yas_in7").strip()
    ACTIVATION_CHANNEL_ID = os.getenv("ACTIVATION_CHANNEL_ID", "").strip()

import catalog

PAGE_SIZE = 12

# ----------------- بيانات الدفع -----------------
PAYMENT_INFO = {
    "jeeb": {
        "name": "ياسين علي اليمني",
        "acc": "3093092",
        "desc": "محفظة جيب (Jeeb)"
    },
    "kuraimi": {
        "name": "ياسين محمد احمد اليمني",
        "acc": "3068499525",
        "desc": "بنك الكريمي (حساب مميز)"
    },
    "binance": {
        "name": "Yassin AL yemeni",
        "acc": "979688758",
        "desc": "بينانس (Binance Pay ID)"
    }
}

print(f"🚀 Initializing Two-Server Engine (+20% Dynamic Real-Time Margin & Accurate Routing)...")

# ----------------- اتصال شبكي سريع -----------------
session = requests.Session()
retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries, pool_connections=50, pool_maxsize=100)
session.mount("https://", adapter)
session.mount("http://", adapter)

# ----------------- قاعدة بيانات -----------------
DB_PATH = "bot_database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                balance REAL DEFAULT 0.0,
                rub_balance REAL DEFAULT 0.0,
                orders_count INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                joined_at TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Database ready.")
    except Exception as e:
        print(f"Init DB Error: {e}")

init_db()

def get_or_create_user(user_id, username="", first_name=""):
    try:
        uname = str(username) if username else ""
        fname = str(first_name) if first_name else "صديقنا"
        uid_str = str(user_id)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT balance, rub_balance, orders_count, is_banned, first_name, username FROM users WHERE user_id = ?', (uid_str,))
        row = cursor.fetchone()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        if row:
            cursor.execute('UPDATE users SET username = ?, first_name = ? WHERE user_id = ?', (uname, fname, uid_str))
            conn.commit()
            conn.close()
            return float(row[0]), float(row[1]), int(row[2]), int(row[3]), str(row[4]), str(row[5])
        else:
            init_bal = 100.0 if uid_str == str(ADMIN_ID) else 0.0
            init_rub = init_bal * RUB_PER_USD
            cursor.execute(
                'INSERT INTO users (user_id, username, first_name, balance, rub_balance, orders_count, is_banned, joined_at) VALUES (?, ?, ?, ?, ?, 0, 0, ?)',
                (uid_str, uname, fname, init_bal, init_rub, now_str)
            )
            conn.commit()
            conn.close()
            return init_bal, init_rub, 0, 0, fname, uname
    except Exception as e:
        print(f"DB Error: {e}")
        return 0.0, 0.0, 0, 0, "صديقنا", ""

def update_user_balance(user_id, amount_usd, amount_rub=None):
    try:
        if amount_rub is None:
            amount_rub = amount_usd * RUB_PER_USD
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET balance = balance + ?, rub_balance = rub_balance + ? WHERE user_id = ?',
            (amount_usd, amount_rub, str(user_id))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Update Bal Error: {e}")

def set_user_ban_status(user_id, ban_status):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_banned = ? WHERE user_id = ?', (1 if ban_status else 0, str(user_id)))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ban Error: {e}")

def get_all_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username, first_name, balance, is_banned, joined_at FROM users ORDER BY rowid DESC')
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Get All Users Error: {e}")
        return []

def get_single_user_info(query):
    try:
        clean_q = query.strip().replace("@", "")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username, first_name, balance, rub_balance, orders_count, is_banned, joined_at FROM users WHERE user_id = ? OR username = ?', (clean_q, clean_q))
        row = cursor.fetchone()
        conn.close()
        return row
    except Exception as e:
        print(f"Find User Error: {e}")
        return None

# ----------------- خادم ويب خفيف -----------------
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Number SMS Store Dual Engine Live 24/7!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()

    def log_message(self, format, *args):
        return

def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

web_thread = threading.Thread(target=start_health_server, daemon=True)
web_thread.start()

# ----------------- تهيئة البوت -----------------
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown", threaded=True, num_threads=32)
user_states = {}
user_click_lock = {}

def send_activation_log(user_id, country_title, service_name, phone, code, price_str, order_id):
    try:
        channel_target = ACTIVATION_CHANNEL_ID or os.getenv("ACTIVATION_CHANNEL_ID", "").strip()
        if not channel_target:
            return
            
        now_time = datetime.datetime.now().strftime("%H:%M | %Y-%m-%d")
        masked_phone = phone[:-4] + "****" if len(phone) > 6 else phone
            
        log_text = (
            f"🟢 **عملية تفعيل جديدة ناجحة!**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🌍 • **الدولة :** {country_title}\n"
            f"🛍️ • **التطبيق :** {service_name}\n"
            f"☎️ • **الرقم :** `+{masked_phone}`\n"
            f"🔑 • **كود التفعيل :** `{code}`\n"
            f"💰 • **السعر :** {price_str}\n"
            f"🔔 • **رقم الطلب :** `{order_id}`\n"
            f"👤 • **المستخدم :** `{user_id}`\n"
            f"⏰ • **الوقت :** `{now_time}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🤖 • بواسطة : **Number SMS Bot**"
        )
        bot.send_message(channel_target, log_text)
    except Exception as e:
        print(f"Activation log notice: {e}")

# ----------------- استعلامات المزودين التلقائية -----------------
HERO_ENDPOINTS = [
    "https://sms-hero.com/stubs/handler_api.php",
    "https://hero-sms.com/stubs/handler_api.php",
    "https://api.sms-hero.com/stubs/handler_api.php"
]

PLUS_ENDPOINTS = [
    "https://sms-plus.net/stubs/handler_api.php",
    "https://api.sms-plus.net/stubs/handler_api.php"
]

def hero_request(params):
    params['api_key'] = HERO_API_KEY
    for endpoint in HERO_ENDPOINTS:
        try:
            res = session.get(endpoint, params=params, timeout=7)
            if res.status_code == 200 and res.text.strip():
                return res.text.strip()
        except Exception:
            continue
    return "ERROR_CONNECTION"

def plus_request(params):
    params['api_key'] = PLUS_API_KEY
    for endpoint in PLUS_ENDPOINTS:
        try:
            res = session.get(endpoint, params=params, timeout=7)
            if res.status_code == 200 and res.text.strip():
                return res.text.strip()
        except Exception:
            continue
    return "ERROR_CONNECTION"

def provider_api_request(provider_name, params):
    if provider_name == "plus":
        return plus_request(params)
    return hero_request(params)

# دالة جلب السعر الفعلي وإضافة 20%
price_cache = {}

def get_server_price(provider_name, service_code, country_id):
    cache_key = f"{provider_name}_{service_code}_{country_id}"
    now_ts = time.time()
    
    if cache_key in price_cache and now_ts - price_cache[cache_key]["time"] < 60:
        return price_cache[cache_key]["rub"], price_cache[cache_key]["usd"]
        
    try:
        resp = provider_api_request(provider_name, {'action': 'getPrices', 'service': service_code, 'country': str(country_id)})
        data = json.loads(resp)
        if str(country_id) in data and service_code in data[str(country_id)]:
            srv_data = data[str(country_id)][service_code]
            raw_cost_rub = float(list(srv_data.keys())[0]) if isinstance(srv_data, dict) else float(srv_data.get('cost', 20))
            
            final_rub = round(raw_cost_rub * (1.0 + PROFIT_MARGIN), 1)
            final_usd = round(final_rub / RUB_PER_USD, 2)
            
            price_cache[cache_key] = {"rub": final_rub, "usd": final_usd, "time": now_ts}
            return final_rub, final_usd
    except Exception:
        pass
        
    c_info = catalog.COUNTRIES.get(str(country_id), {"default_rub": 20.0})
    raw_rub = c_info.get("default_rub", 20.0)
    final_rub = round(raw_rub * (1.0 + PROFIT_MARGIN), 1)
    final_usd = round(final_rub / RUB_PER_USD, 2)
    return final_rub, final_usd

# دالة شراء الرقم مع التحقق الصارم من الدولة (لمنع استلام رقم دولة أخرى مثل السعودية بدلاً من اليمن)
def buy_server_number(provider_name, service_code, country_id):
    c_info = catalog.COUNTRIES.get(str(country_id), {})
    expected_prefix = c_info.get("prefix", "")
    
    params = {
        'action': 'getNumber',
        'service': service_code,
        'country': str(country_id)
    }
    
    resp = provider_api_request(provider_name, params)
    if resp.startswith("ACCESS_NUMBER:"):
        parts = resp.split(":")
        order_id = parts[1]
        phone = parts[2]
        
        # حماية صارمة: إذا كان الرقم المطلوب لليمن مثلاً ولم يبدأ بمفتاح اليمن، يتم إلغاؤه فوراً
        if expected_prefix and not phone.startswith(expected_prefix):
            # إلغاء الرقم الخاطئ فوراً عند المزود
            provider_api_request(provider_name, {'action': 'setStatus', 'id': order_id, 'status': '8'})
            return False, f"تنبيه: أرسل المزود رقم بدولة أخرى غير مطابقة، تم إلغاؤه لحمايتك. جرب مجدداً."
            
        return True, {"id": order_id, "phone": phone, "provider": provider_name}
    elif resp == "NO_NUMBERS":
        return False, "الأرقام لهذه الدولة غير متوفرة حالياً في هذا السيرفر."
    elif resp == "NO_BALANCE":
        return False, "رصيد السيرفر غير كافٍ."
    return False, f"رد المزود: {resp}"

def set_server_status(provider_name, order_id, status_code):
    threading.Thread(target=provider_api_request, args=(provider_name, {'action': 'setStatus', 'id': order_id, 'status': status_code}), daemon=True).start()

active_orders = {}

def monitor_sms_code(chat_id, message_id, order_id, phone_number, app_name, country_title, cost_str, time_now_str, time_exp_str, cost_usd, cost_rub, user_id, provider_name):
    active_orders[order_id] = {
        "user_id": user_id,
        "start_time": time.time(),
        "cost_usd": cost_usd,
        "cost_rub": cost_rub,
        "phone": phone_number,
        "provider": provider_name
    }
    
    max_duration = 1080
    start_time = time.time()
    
    while time.time() - start_time < max_duration:
        time.sleep(4)
        if order_id not in active_orders:
            return
        try:
            resp = provider_api_request(provider_name, {'action': 'getStatus', 'id': order_id})
            if resp.startswith("STATUS_OK:"):
                code = resp.split(":")[1]
                
                success_text = (
                    f"╭━━〔 **NUMBER SMS** 〕━━╮\n"
                    f"💙 **تم استلام كود التفعيل بنجاح!**\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"🔔 • رقم الطلب : `{order_id}`\n"
                    f"🌍 • الدولة : **{country_title}**\n"
                    f"☎️ • الرقم : `+{phone_number}`\n"
                    f"🔑 • **الكود المستلم :** `{code}`\n"
                    f"🔎 • الحالة : **COMPLETED ✔️**\n"
                    f"🛍️ • التطبيق : **{app_name}**\n"
                    f"🏷️ • السعر : **{cost_str}**\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"✅ تم تأكيد تفعيل الرقم بنجاح."
                )
                
                fin_markup = types.InlineKeyboardMarkup(row_width=1)
                fin_markup.add(types.InlineKeyboardButton("☎️ شراء رقم آخر", callback_data="btn_buy_number"))
                fin_markup.add(types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_main"))
                
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=success_text, reply_markup=fin_markup)
                set_server_status(provider_name, order_id, 6)
                active_orders.pop(order_id, None)
                
                send_activation_log(user_id, country_title, app_name, phone_number, code, cost_str, order_id)
                return
            elif resp == "STATUS_CANCEL":
                bot.send_message(chat_id, f"⚠️ تم إلغاء طلب الرقم `+{phone_number}` واسترجاع الرصيد لمحفظتك.")
                update_user_balance(user_id, cost_usd, cost_rub)
                active_orders.pop(order_id, None)
                return
        except Exception as e:
            print(f"SMS Check Notice: {e}")
            
    if order_id in active_orders:
        set_server_status(provider_name, order_id, 8)
        update_user_balance(user_id, cost_usd, cost_rub)
        active_orders.pop(order_id, None)
        try:
            bot.send_message(
                chat_id,
                f"⌛ **انتهت مهلة الانتظار للرقم `+{phone_number}`.**\n"
                f"🛡️ تم إلغاء الطلب واسترجاع كامل المبلغ ({cost_str}) لمحفظتك تلقائياً."
            )
        except Exception:
            pass

# ----------------- بناء القوائم -----------------

def build_main_keyboard(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("☎️ شراء رقم افتراضي", callback_data="btn_buy_number"))
    markup.add(
        types.InlineKeyboardButton("💬 عروض WhatsApp", callback_data="btn_offers_wa"),
        types.InlineKeyboardButton("✈️ جاهز Telegram", callback_data="btn_ready_tg")
    )
    markup.add(types.InlineKeyboardButton("📈 السيرفرات الأكثر مبيعاً", callback_data="btn_bestseller"))
    markup.add(
        types.InlineKeyboardButton("🎳 • شحن الرصيد •", callback_data="btn_deposit"),
        types.InlineKeyboardButton("🔄 • تحويل الرصيد (مجاناً) •", callback_data="btn_transfer_balance")
    )
    markup.add(types.InlineKeyboardButton("🔭 • الرشق وشحن الألعاب والبرامج •", callback_data="btn_services_games"))
    markup.add(types.InlineKeyboardButton("💎 • اربح رصيد مجاناً •", callback_data="btn_free_points"))
    
    markup.add(
        types.InlineKeyboardButton("📢 قناة البوت الرسمية", url=MAIN_CHANNEL_URL),
        types.InlineKeyboardButton("📚 التعليمات والشرح", url=INSTRUCTIONS_CHANNEL_URL)
    )
    markup.add(
        types.InlineKeyboardButton("🕒 الدعم الفني", url=f"https://t.me/{SUPPORT_USERNAME}"),
        types.InlineKeyboardButton("✔️ • إحصائيات الشراء الناجح •", callback_data="btn_stats")
    )
    markup.add(types.InlineKeyboardButton("🪪 حسابي والمحفظة", callback_data="btn_my_account"))
    markup.add(types.InlineKeyboardButton("🛸 • خدمات ومميزات أخرى •", callback_data="btn_extra_features"))
    if str(user_id) == str(ADMIN_ID):
        markup.add(types.InlineKeyboardButton("👑 • لوحة تحكم الإدارة (Admin) •", callback_data="btn_admin_panel"))
    return markup

def build_apps_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🛍️ WHATSAPP - واتس اب", callback_data="srv_wa"))
    markup.add(types.InlineKeyboardButton("🎲 TELEGRAM - تليجرام", callback_data="srv_tg"))
    markup.add(types.InlineKeyboardButton("🎳 INSTAGRAM - انستغرام", callback_data="srv_ig"))
    markup.add(types.InlineKeyboardButton("🎯 FACEBOOK - فيسبوك", callback_data="srv_fb"))
    markup.add(types.InlineKeyboardButton("🐤 TWITTER - تويتر", callback_data="srv_tw"))
    markup.add(
        types.InlineKeyboardButton("🎥 TIKTOK - تيك توك", callback_data="srv_lf"),
        types.InlineKeyboardButton("☂️ Google - جوجل", callback_data="srv_go")
    )
    markup.add(
        types.InlineKeyboardButton("♣️ SNAP - سناب شات", callback_data="srv_sn"),
        types.InlineKeyboardButton("🪗 HARAJ - حراج", callback_data="srv_hj")
    )
    markup.add(
        types.InlineKeyboardButton("💎 IMO - ايمو", callback_data="srv_im"),
        types.InlineKeyboardButton("🤖 السيرفر العام", callback_data="srv_ot")
    )
    markup.add(
        types.InlineKeyboardButton("🏐 PAYPAL - بايبال", callback_data="srv_pp"),
        types.InlineKeyboardButton("📳 Viber - فايبر", callback_data="srv_vi")
    )
    markup.add(types.InlineKeyboardButton("✤ ↩️ عودة ✤", callback_data="back_to_main"))
    return markup

# سرفرين فقط
def build_servers_keyboard(app_code):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🌟 السيرفر (1) Plus SMS", callback_data=f"page_{app_code}_s1_0"),
        types.InlineKeyboardButton("⚡ السيرفر (2) Hero SMS", callback_data=f"page_{app_code}_s2_0")
    )
    markup.add(types.InlineKeyboardButton("🔍 🚀 البحث عن دولة بالاسم 🧩", callback_data=f"prompt_search_country_{app_code}"))
    markup.add(types.InlineKeyboardButton("✤ ↩️ عودة ✤", callback_data="btn_buy_number"))
    return markup

# نظام صفحات الدول مع حفظ مكان الصفحة الدقيق
def build_countries_page_keyboard(app_code, server_key, page=0):
    markup = types.InlineKeyboardMarkup(row_width=2)
    c_list = list(catalog.COUNTRIES.items())
    total_countries = len(c_list)
    total_pages = (total_countries + PAGE_SIZE - 1) // PAGE_SIZE
    
    start_idx = page * PAGE_SIZE
    end_idx = min(start_idx + PAGE_SIZE, total_countries)
    current_batch = c_list[start_idx:end_idx]
    
    buttons = []
    for c_id, c_info in current_batch:
        btn_text = f"{c_info['flag']} {c_info['title']}"
        # تمرير رقم الصفحة الحالية للحفاظ على موقع المستخدم
        buttons.append(types.InlineKeyboardButton(btn_text, callback_data=f"card_{app_code}_{server_key}_{c_id}_{page}"))
    markup.add(*buttons)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton("➡️ السابق", callback_data=f"page_{app_code}_{server_key}_{page-1}"))
    nav_buttons.append(types.InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav_buttons.append(types.InlineKeyboardButton("التالي ⬅️", callback_data=f"page_{app_code}_{server_key}_{page+1}"))
    
    markup.row(*nav_buttons)
    markup.add(types.InlineKeyboardButton("🔍 🚀 البحث عن دولة 🧩", callback_data=f"prompt_search_country_{app_code}_{server_key}"))
    markup.add(types.InlineKeyboardButton("✤ ↩️ عودة للسيرفرات ✤", callback_data=f"srv_{app_code}"))
    return markup

def build_smm_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    for smm_id, smm_info in catalog.SMM_SERVICES.items():
        btn_title = f"{smm_info['title']} - {smm_info['cost_usd']:.2f}$"
        markup.add(types.InlineKeyboardButton(btn_title, callback_data=f"smm_card_{smm_id}"))
    markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
    return markup

def build_admin_main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("👥 قائمة المستخدمين", callback_data="admin_view_users"),
        types.InlineKeyboardButton("🔍 بحث والتحكم بمستخدم", callback_data="admin_search_user")
    )
    markup.add(
        types.InlineKeyboardButton("➕ شحن رصيد يدوي", callback_data="admin_prompt_add_bal"),
        types.InlineKeyboardButton("➖ خصم رصيد", callback_data="admin_prompt_sub_bal")
    )
    markup.add(
        types.InlineKeyboardButton("🚫 طرد / حظر مستخدم", callback_data="admin_prompt_ban"),
        types.InlineKeyboardButton("📢 إذاعة عامة للكل", callback_data="admin_prompt_broadcast")
    )
    markup.add(
        types.InlineKeyboardButton("💳 فحص Hero SMS", callback_data="admin_check_provider"),
        types.InlineKeyboardButton("🚀 فحص Plus API", callback_data="admin_check_plus")
    )
    markup.add(types.InlineKeyboardButton("🔙 العودة للواجهة الرئيسية", callback_data="back_to_main"))
    return markup

# ----------------- معالجة أمر البداية (Start) -----------------

@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or ""
        first_name = message.from_user.first_name or "صديقنا"
        
        bal_usd, bal_rub, orders, is_banned, fn, un = get_or_create_user(user_id, username, first_name)
        
        if is_banned and str(user_id) != str(ADMIN_ID):
            bot.reply_to(message, "⛔ **تم حظرك من استخدام هذا البوت!**\nتواصل مع الإدارة إذا كنت تعتقد أن هذا خطأ.")
            return
            
        text = (
            f"╭━━━〔 **NUMBER SMS** 〕━━━╮\n"
            f"🛍️ أهلاً بك يا **{first_name}** في المتجر الأقوى للأرقام الوهمية والتفعيلات الفورية!\n\n"
            f"👤 • معرفك (ID): `{user_id}`\n"
            f"💵 • رصيدك الحالي: **{bal_usd:.2f} {CURRENCY} | {bal_rub:.1f} ₽**\n"
            f"⚡ • حالة السيرفرات: **جاهزة ونشطة 100%**\n"
            f"╰━━━━━━━━━━━━━━━━━╯\n\n"
            f"👇 **تفضل باختيار القسم المطلوب من القائمة أدناه:**"
        )
        markup = build_main_keyboard(user_id)
        bot.reply_to(message, text, reply_markup=markup)
    except Exception as e:
        print(f"Start command error: {e}")

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.reply_to(message, "⛔ هذا الأمر خاص بإدارة البوت فقط!")
        return
    markup = build_admin_main_keyboard()
    bot.reply_to(message, "👑 **أهلاً بك يا مدير البوت في لوحة التحكم الإدارية الشاملة:**", reply_markup=markup)

# ----------------- معالجة النصوص -----------------

@bot.message_handler(func=lambda msg: not msg.text.startswith('/'))
def handle_all_text_messages(message):
    try:
        user_id_str = str(message.from_user.id)
        text = message.text.strip()
        state = user_states.pop(user_id_str, None)
        
        if not state:
            return

        action = state.get("action")
        
        # 1. نظام تحويل الرصيد المجاني
        if action == "transfer_step_1_id":
            target_uid = text.strip()
            if target_uid == user_id_str:
                bot.reply_to(message, "❌ لا يمكنك تحويل الرصيد لنفسك!")
                return
            target_user = get_single_user_info(target_uid)
            if not target_user:
                bot.reply_to(message, f"❌ لم يتم العثور على مستخدم بالمعرف `{target_uid}`. تأكد من رقم المعرف.")
                return
            
            user_states[user_id_str] = {"action": "transfer_step_2_amount", "target_uid": target_uid, "target_name": target_user[2]}
            bot.reply_to(
                message,
                f"👤 **المستلم:** **{target_user[2]}** (`{target_uid}`)\n\n"
                f"💵 **أرسل الآن المبلغ المراد تحويله بالدولار (التحويل مجاني 0% عمولة):**"
            )

        elif action == "transfer_step_2_amount":
            target_uid = state.get("target_uid")
            target_name = state.get("target_name")
            try:
                amt = float(text)
                if amt <= 0:
                    bot.reply_to(message, "❌ يرجى إدخال مبلغ أكبر من الصفر.")
                    return
                sender_usd, _, _, _, _, _ = get_or_create_user(message.from_user.id)
                if sender_usd < amt:
                    bot.reply_to(message, f"❌ **رصيدك غير كافٍ!** رصيدك الحالي هو: **{sender_usd:.2f} $**")
                    return
                
                update_user_balance(message.from_user.id, -amt)
                update_user_balance(target_uid, amt)
                
                bot.reply_to(
                    message,
                    f"✅ **تم تحويل {amt:.2f} $ بنجاح إلى {target_name} (`{target_uid}`) مجاناً!**",
                    reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="back_to_main"))
                )
                try:
                    bot.send_message(
                        target_uid,
                        f"🎉 **وصلك تحويل رصيد جديد!**\n\n"
                        f"👤 • من: `{user_id_str}`\n"
                        f"💵 • المبلغ: **+{amt:.2f} $** ({amt * RUB_PER_USD:.1f} ₽)\n"
                        f"✅ تمت إضافة الرصيد لمحفظتك مجاناً."
                    )
                except Exception:
                    pass
            except Exception:
                bot.reply_to(message, "❌ يرجى إدخال رقم صحيح (مثال: 2 أو 5.5).")

        # 2. طلبات الرشق وشحن الألعاب
        elif action == "submit_smm_order":
            smm_id = state.get("smm_id")
            smm_info = catalog.SMM_SERVICES.get(smm_id)
            if not smm_info:
                return
            
            bal_usd, bal_rub, _, _, _, _ = get_or_create_user(message.from_user.id)
            if bal_usd < smm_info['cost_usd'] and str(message.from_user.id) != str(ADMIN_ID):
                bot.reply_to(message, f"❌ رصيدك غير كافٍ! سعر الخدمة {smm_info['cost_usd']:.2f} $ ورصيدك {bal_usd:.2f} $.")
                return
            
            update_user_balance(message.from_user.id, -smm_info['cost_usd'])
            order_id = f"SMM-{int(time.time())}"
            
            notify_admin = (
                f"🚀 **طلب رشق / شحن ألعاب جديد!**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🔔 • رقم الطلب : `{order_id}`\n"
                f"👤 • المستخدم : `{user_id_str}` (@{message.from_user.username or 'بدون_يوزر'})\n"
                f"🛍️ • الخدمة : **{smm_info['title']}**\n"
                f"🔗 • الرابط / الآيدي : `{text}`\n"
                f"💰 • التكلفة : **{smm_info['cost_usd']:.2f} $**\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            try:
                bot.send_message(ADMIN_ID, notify_admin)
            except Exception:
                pass
                
            bot.reply_to(
                message,
                f"✅ **تم تسجيل طلبك بنجاح!**\n\n"
                f"🔔 • رقم الطلب: `{order_id}`\n"
                f"🛍️ • الخدمة: **{smm_info['title']}**\n"
                f"🎯 • الهدف: `{text}`\n\n"
                f"⏳ جاري تنفيذ الطلب وإرسال التغذية فوراً.",
                reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="back_to_main"))
            )

        # 3. البحث عن دولة
        elif action == "search_country_for_app":
            app_code = state.get("app_code", "wa")
            server_key = state.get("server_key", "s1")
            search_query = text.lower()
            
            matched_countries = []
            for c_id, c_info in catalog.COUNTRIES.items():
                if (search_query in c_info["name"].lower() or 
                    search_query in c_info["title"].lower() or 
                    search_query in c_info["prefix"] or 
                    search_query == c_id):
                    matched_countries.append((c_id, c_info))
                    
            if not matched_countries:
                msg_text = f"🔍 **لم يتم العثور على دولة مطابقة لـ:** `{text}`\n\n👉 جرب اسم آخر (مثل: اليمن، السعودية، البرازيل)."
                markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 عودة لقائمة الدول", callback_data=f"page_{app_code}_{server_key}_0")
                )
                bot.reply_to(message, msg_text, reply_markup=markup)
                return
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            for c_id, c_info in matched_countries:
                btn_text = f"{c_info['flag']} {c_info['title']}"
                markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"card_{app_code}_{server_key}_{c_id}_0"))
            markup.add(types.InlineKeyboardButton("🔙 عودة لقائمة الدول", callback_data=f"page_{app_code}_{server_key}_0"))
            
            bot.reply_to(message, f"🎯 **نتائج البحث عن ({text}):**\nاختر الدولة المطلوبة:", reply_markup=markup)

        # 4. شحن وخصم يدوي من الإدارة
        elif action == "admin_input_add_target" and user_id_str == str(ADMIN_ID):
            target_uid = text.strip()
            user_states[user_id_str] = {"action": "admin_input_add_amt", "target_uid": target_uid}
            bot.reply_to(message, f"➕ **أرسل الآن المبلغ المراد شحنه للمستخدم `{target_uid}` بالدولار (مثال: 5):**")

        elif action == "admin_input_add_amt" and user_id_str == str(ADMIN_ID):
            target_uid = state.get("target_uid")
            try:
                amt = float(text)
                update_user_balance(target_uid, amt)
                bot.reply_to(message, f"✅ **تم شحن {amt:.2f} $ بنجاح لحساب `{target_uid}`.**")
                try:
                    bot.send_message(target_uid, f"🎉 **تم إيداع رصيد جديد في محفظتك!**\n\n💵 المبلغ: **{amt:.2f} $** ({amt * RUB_PER_USD:.1f} ₽)")
                except Exception:
                    pass
            except Exception:
                bot.reply_to(message, "❌ القيمة المدخلة غير صحيحة.")

        elif action == "admin_input_sub_target" and user_id_str == str(ADMIN_ID):
            target_uid = text.strip()
            user_states[user_id_str] = {"action": "admin_input_sub_amt", "target_uid": target_uid}
            bot.reply_to(message, f"➖ **أرسل الآن المبلغ المراد خصمه من المستخدم `{target_uid}` بالدولار (مثال: 2):**")

        elif action == "admin_input_sub_amt" and user_id_str == str(ADMIN_ID):
            target_uid = state.get("target_uid")
            try:
                amt = float(text)
                update_user_balance(target_uid, -amt)
                bot.reply_to(message, f"✅ **تم خصم {amt:.2f} $ بنجاح من حساب `{target_uid}`.**")
                try:
                    bot.send_message(target_uid, f"⚠️ **تنبيه:** تم خصم **{amt:.2f} $** من رصيدك بواسطة الإدارة.")
                except Exception:
                    pass
            except Exception:
                bot.reply_to(message, "❌ القيمة المدخلة غير صحيحة.")

        elif action == "verify_auto_payment":
            method = state.get("method", "jeeb")
            method_title = "محفظة جيب" if method == "jeeb" else "منصة بينانس"
            notify_admin = (
                f"🔔 **طلب شحن وتأكيد دفع جديد!**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👤 • المستخدم : `{user_id_str}` (@{message.from_user.username or 'بدون_يوزر'})\n"
                f"🏦 • طريقة الدفع : **{method_title}**\n"
                f"🧾 • رقم الإشعار / العملية : `{text}`\n"
                f"⏰ • الوقت : `{datetime.datetime.now().strftime('%H:%M | %Y-%m-%d')}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👇 للشحن الفوري للمستخدم اضغط الزر أدناه:"
            )
            adm_markup = types.InlineKeyboardMarkup(row_width=2)
            adm_markup.add(
                types.InlineKeyboardButton("➕ شحن رصيد له", callback_data=f"adm_addbal_{user_id_str}"),
                types.InlineKeyboardButton("👤 ملف حسابه", callback_data=f"adm_userinfo_{user_id_str}")
            )
            try:
                bot.send_message(ADMIN_ID, notify_admin, reply_markup=adm_markup)
            except Exception:
                pass
                
            bot.reply_to(
                message,
                f"✅ **تم استلام رقم العملية (`{text}`) بنجاح!**\n\n"
                f"⏳ جاري مطابقة العملية وإيداع الرصيد في محفظتك تلقائياً.",
                reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
            )

        elif action == "admin_search_user" and user_id_str == str(ADMIN_ID):
            user_info = get_single_user_info(text)
            if not user_info:
                markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 عودة للوحة الإدارة", callback_data="btn_admin_panel"))
                bot.reply_to(message, f"❌ **لم يتم العثور على مستخدم بالمعرف أو الاسم:** `{text}`", reply_markup=markup)
                return
            
            uid, uname, fname, bal_usd, bal_rub, orders, is_banned, joined = user_info
            status_text = "🚫 محظور (مطرود)" if is_banned else "✅ نشط"
            card = (
                f"👤 **ملف المستخدم:**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"• الاسم: **{fname}**\n"
                f"• المعرف (ID): `{uid}`\n"
                f"• اليوزر: @{uname if uname else 'بدون_يوزر'}\n"
                f"• الرصيد: **{bal_usd:.2f} $** ({bal_rub:.1f} ₽)\n"
                f"• المشتريات: **{orders} رقم**\n"
                f"• الحالة: **{status_text}**\n"
                f"• تاريخ الانضمام: `{joined}`\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            u_markup = types.InlineKeyboardMarkup(row_width=2)
            u_markup.add(
                types.InlineKeyboardButton("➕ شحن رصيد", callback_data=f"adm_addbal_{uid}"),
                types.InlineKeyboardButton("➖ خصم رصيد", callback_data=f"adm_subbal_{uid}")
            )
            ban_btn_text = "🟢 إلغاء الحظر" if is_banned else "🚫 طرد / حظر"
            ban_cb = f"adm_unban_{uid}" if is_banned else f"adm_ban_{uid}"
            u_markup.add(
                types.InlineKeyboardButton(ban_btn_text, callback_data=ban_cb),
                types.InlineKeyboardButton("✉️ مراسلة خاصة", callback_data=f"adm_msg_{uid}")
            )
            u_markup.add(types.InlineKeyboardButton("🔙 عودة للوحة الإدارة", callback_data="btn_admin_panel"))
            bot.reply_to(message, card, reply_markup=u_markup)

        elif action == "broadcast_all" and user_id_str == str(ADMIN_ID):
            users = get_all_users()
            sent_count = 0
            bot.reply_to(message, f"⏳ جاري بدء الإذاعة لـ {len(users)} مستخدم...")
            for u in users:
                uid = u[0]
                try:
                    bot.send_message(uid, f"📢 **إشعار هام من إدارة البوت:**\n\n{text}")
                    sent_count += 1
                    time.sleep(0.04)
                except Exception:
                    continue
            bot.send_message(user_id_str, f"✅ **اكتملت الإذاعة بنجاح!**\nتم التوصيل إلى **{sent_count}** مستخدم.")

    except Exception as e:
        print(f"Handle Text Error: {e}")

# ----------------- معالجة الأزرار (Callbacks) -----------------

@bot.callback_query_handler(func=lambda call: True)
def router_callback(call):
    try:
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        data = call.data
        
        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass

        now_ts = time.time()
        if user_id in user_click_lock and now_ts - user_click_lock[user_id] < 0.25:
            return
        user_click_lock[user_id] = now_ts

        bal_usd, bal_rub, orders, is_banned, fn, un = get_or_create_user(user_id, call.from_user.username, call.from_user.first_name)
        
        if is_banned and str(user_id) != str(ADMIN_ID):
            try:
                bot.send_message(chat_id, "⛔ حسابك محظور من استخدام البوت!")
            except Exception:
                pass
            return

        if data == "back_to_main":
            user_name = call.from_user.first_name if call.from_user.first_name else "صديقنا"
            text = (
                f"╭━━━〔 **NUMBER SMS** 〕━━━╮\n"
                f"🛍️ أهلاً بك يا **{user_name}** في المتجر الأقوى للأرقام الوهمية والتفعيلات الفورية!\n\n"
                f"👤 • معرفك (ID): `{user_id}`\n"
                f"💵 • رصيدك الحالي: **{bal_usd:.2f} {CURRENCY} | {bal_rub:.1f} ₽**\n"
                f"⚡ • حالة السيرفرات: **جاهزة ونشطة 100%**\n"
                f"╰━━━━━━━━━━━━━━━━━╯\n\n"
                f"👇 **تفضل باختيار القسم المطلوب من القائمة أدناه:**"
            )
            markup = build_main_keyboard(user_id)
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

        # ----------------- قسم الرشق وشحن الألعاب -----------------
        elif data == "btn_services_games":
            markup = build_smm_keyboard()
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text="🔭 **قسم الرشق وشحن الألعاب والبرامج:**\nاختر الخدمة المطلوبة من القائمة أدناه:",
                reply_markup=markup
            )

        elif data.startswith("smm_card_"):
            smm_id = data.replace("smm_card_", "")
            smm_info = catalog.SMM_SERVICES.get(smm_id)
            if not smm_info:
                return
            
            text = (
                f"🛍️ **تفاصيل الخدمة:**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📌 • **الخدمة :** {smm_info['title']}\n"
                f"💰 • **السعر :** **{smm_info['cost_usd']:.2f} $** ({smm_info['cost_rub']:.1f} ₽)\n"
                f"📝 • **الوصف :** {smm_info['desc']}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👇 اضغط على زر طلب الخدمة للمتابعة:"
            )
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("🚀 طلب وتنفيذ الخدمة الآن", callback_data=f"smm_buy_{smm_id}"))
            markup.add(types.InlineKeyboardButton("🔙 عودة لقائمة الرشق", callback_data="btn_services_games"))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

        elif data.startswith("smm_buy_"):
            smm_id = data.replace("smm_buy_", "")
            user_states[str(user_id)] = {"action": "submit_smm_order", "smm_id": smm_id}
            bot.send_message(chat_id, "🔗 **أرسل الآن رابط الحساب أو القناة أو الآيدي (ID) المراد إرسال الخدمة إليه:**")

        # ----------------- تحويل الرصيد المجاني -----------------
        elif data == "btn_transfer_balance":
            user_states[str(user_id)] = {"action": "transfer_step_1_id"}
            text = (
                f"🔄 **قسم تحويل الرصيد الفوري المجاني (0% عمولة):**\n\n"
                f"💵 • رصيدك الحالي: **{bal_usd:.2f} $**\n\n"
                f"👉 **أرسل الآن معرف (ID) المستخدم المراد التحويل له:**"
            )
            bot.send_message(chat_id, text)

        # ----------------- شحن الرصيد اليدوي للأدمن -----------------
        elif data == "admin_prompt_add_bal":
            if str(user_id) != str(ADMIN_ID):
                return
            user_states[str(user_id)] = {"action": "admin_input_add_target"}
            bot.send_message(chat_id, "➕ **أرسل الآن معرف (User ID) الشخص المراد شحن الرصيد له:**")

        elif data == "admin_prompt_sub_bal":
            if str(user_id) != str(ADMIN_ID):
                return
            user_states[str(user_id)] = {"action": "admin_input_sub_target"}
            bot.send_message(chat_id, "➖ **أرسل الآن معرف (User ID) الشخص المراد خصم الرصيد منه:**")

        # ----------------- قسم الشحن والدفع -----------------
        elif data == "btn_deposit":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("📱 محفظة جيب (Jeeb) - شحن فوري", callback_data="pay_jeeb"))
            markup.add(types.InlineKeyboardButton("🏦 بنك الكريمي (حساب يمني / دولار)", callback_data="pay_kuraimi"))
            markup.add(types.InlineKeyboardButton("🪙 منصة بينانس (Binance Pay ID)", callback_data="pay_binance"))
            markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
            
            deposit_text = (
                f"╭━━〔 **قسم شحن الرصيد** 〕━━╮\n"
                f"💳 **اختر وسيلة الدفع المناسبة لك لشحن محفظتك:**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"💵 • سعر الصرف في البوت: **1 دولار = {RUB_PER_USD:.0f} روبل**\n"
                f"⚡ • يتوفر دعم الإيداع الفوري التلقائي.\n"
                f"╰━━━━━━━━━━━━━━━━━╯"
            )
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=deposit_text, reply_markup=markup)

        elif data == "pay_jeeb":
            info = PAYMENT_INFO["jeeb"]
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("⚡ تأكيد وتفعيل الدفع التلقائي", callback_data="confirm_pay_jeeb"))
            markup.add(types.InlineKeyboardButton("💬 مراسلة الدعم الفني للإشعار اليدوي", url=f"https://t.me/{SUPPORT_USERNAME}"))
            markup.add(types.InlineKeyboardButton("🔙 عودة لقائمة وسائل الدفع", callback_data="btn_deposit"))
            
            text = (
                f"📱 **الدفع عبر محفظة جيب (Jeeb):**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🔢 • **الرقم البديل للمحفظة :** `{info['acc']}`\n"
                f"👤 • **الاسم المعتمد :** **{info['name']}**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📌 **طريقة الشحن:**\n"
                f"1. حول المبلغ المطلوب إلى الرقم البديل أعلاه.\n"
                f"2. اضغط على زر **(⚡ تأكيد وتفعيل الدفع التلقائي)** وأرسل رقم العملية وسيتم شحن رصيدك تلقائياً!"
            )
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

        elif data == "pay_kuraimi":
            info = PAYMENT_INFO["kuraimi"]
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("💬 إرسال إشعار التحويل للإدارة", url=f"https://t.me/{SUPPORT_USERNAME}"))
            markup.add(types.InlineKeyboardButton("🔙 عودة لقائمة وسائل الدفع", callback_data="btn_deposit"))
            
            text = (
                f"🏦 **الدفع عبر بنك الكريمي المميز:**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🔢 • **رقم الحساب :** `{info['acc']}`\n"
                f"👤 • **الاسم :** **{info['name']}**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📸 بعد التحويل، أرسل صورة الإشعار مع معرفك (`{user_id}`) للدعم الفني وسيتم إضافة الرصيد فوراً."
            )
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

        elif data == "pay_binance":
            info = PAYMENT_INFO["binance"]
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("⚡ تأكيد وتفعيل الدفع التلقائي", callback_data="confirm_pay_binance"))
            markup.add(types.InlineKeyboardButton("💬 إرسال إشعار التحويل للإدارة", url=f"https://t.me/{SUPPORT_USERNAME}"))
            markup.add(types.InlineKeyboardButton("🔙 عودة لقائمة وسائل الدفع", callback_data="btn_deposit"))
            
            text = (
                f"🪙 **الدفع عبر بينانس (Binance Pay ID):**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🔢 • **Binance Pay ID :** `{info['acc']}`\n"
                f"👤 • **الاسم المعتمد :** **{info['name']}**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📌 **طريقة الشحن:**\n"
                f"1. ادخل على تطبيق Binance واختر Pay ثم أدخل الـ ID أعلاه وأرسل مبلغ USDT المطلوب.\n"
                f"2. اضغط على زر **(⚡ تأكيد وتفعيل الدفع التلقائي)** وأرسل رقم العملية."
            )
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

        elif data == "confirm_pay_jeeb":
            user_states[str(user_id)] = {"action": "verify_auto_payment", "method": "jeeb"}
            bot.send_message(chat_id, "📱 **أرسل الآن رقم العملية أو رقم المرجع الخاص بالتحويل في محفظة جيب:**")

        elif data == "confirm_pay_binance":
            user_states[str(user_id)] = {"action": "verify_auto_payment", "method": "binance"}
            bot.send_message(chat_id, "🪙 **أرسل الآن رقم العملية (Order ID / Pay ID) الخاص بتحويل بينانس:**")

        # ----------------- مسارات تصفح التطبيقات والسيرفرين -----------------
        elif data in ["btn_buy_number", "btn_offers_wa", "btn_ready_tg"]:
            markup = build_apps_keyboard()
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text="╭━━━〔 **NUMBER SMS** 〕━━━╮\n📱 **اختر التطبيق الذي ترغب في تفعيله:**\n╰━━━━━━━━━━━━━━━━━╯",
                reply_markup=markup
            )

        elif data.startswith("srv_"):
            app_code = data.replace("srv_", "")
            app_info = catalog.SERVICES.get(app_code, catalog.SERVICES["wa"])
            
            text = (
                f"• **التطبيق المختار : {app_info['name']}**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"اختر السيرفر المناسب لك أدناه:"
            )
            markup = build_servers_keyboard(app_code)
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

        elif data.startswith("page_"):
            parts = data.split("_")
            app_code = parts[1]
            server_key = parts[2]
            page = int(parts[3])
            
            app_info = catalog.SERVICES.get(app_code, catalog.SERVICES["wa"])
            srv_info = catalog.SERVERS.get(server_key, catalog.SERVERS["s1"])
            
            text = (
                f"╭━━〔 **NUMBER SMS** 〕━━╮\n"
                f"📱 **التطبيق :** {app_info['name']}\n"
                f"🧩 **السيرفر :** {srv_info['title']}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👇 اختر الدولة المطلوبة من القائمة:"
            )
            markup = build_countries_page_keyboard(app_code, server_key, page)
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

        elif data.startswith("prompt_search_country_"):
            parts = data.split("_")
            app_code = parts[3]
            server_key = parts[4] if len(parts) > 4 else "s1"
            user_states[str(user_id)] = {"action": "search_country_for_app", "app_code": app_code, "server_key": server_key}
            bot.send_message(chat_id, "🔍 **أرسل الآن اسم الدولة أو رمز مفتاحها (مثال: اليمن، السعودية، مصر، أو 967):**")

        elif data.startswith("card_"):
            parts = data.split("_")
            app_code = parts[1]
            server_key = parts[2]
            c_id = parts[3]
            page = int(parts[4]) if len(parts) > 4 else 0
            
            app_info = catalog.SERVICES.get(app_code, catalog.SERVICES["wa"])
            srv_info = catalog.SERVERS.get(server_key, catalog.SERVERS["s1"])
            c_info = catalog.COUNTRIES.get(c_id, catalog.COUNTRIES.get("54", {}))
            
            provider_name = srv_info["provider"]
            
            # جلب السعر اللحظي من مزود السيرفر مع هامش ربح 20%
            final_rub, final_usd = get_server_price(provider_name, app_info['code'], c_id)
            
            text = (
                f"➕ **شراء رقم جديد ✅**\n\n"
                f"➖ **💻 التطبيق | {app_info['short']}**\n"
                f"➖ **🌍 الدولة | {c_info['title']} {c_info['flag']}**\n"
                f"➖ **🔢 مفتاح الدولة | +{c_info['prefix']} 💚**\n"
                f"➖ **🧩 السيرفر | {srv_info['badge']}**\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("🎲 السعر ₽", callback_data="noop"),
                types.InlineKeyboardButton("🧩 السيرفر", callback_data="noop")
            )
            markup.add(
                types.InlineKeyboardButton(f"{final_rub} ₽ | {final_usd:.2f} $", callback_data=f"exec_buy_{app_code}_{server_key}_{c_id}_{page}"),
                types.InlineKeyboardButton(f"1 {c_info['flag']} {c_info['title']}", callback_data=f"exec_buy_{app_code}_{server_key}_{c_id}_{page}")
            )
            # زر العودة يرجع لنفس الصفحة الدقيقة
            markup.add(types.InlineKeyboardButton("✤ ↩️ عودة لقائمة الدول ✤", callback_data=f"page_{app_code}_{server_key}_{page}"))
            
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

        elif data.startswith("exec_buy_"):
            parts = data.split("_")
            app_code = parts[2]
            server_key = parts[3]
            c_id = parts[4]
            page = int(parts[5]) if len(parts) > 5 else 0
            
            app_info = catalog.SERVICES.get(app_code, catalog.SERVICES["wa"])
            srv_info = catalog.SERVERS.get(server_key, catalog.SERVERS["s1"])
            c_info = catalog.COUNTRIES.get(c_id, catalog.COUNTRIES.get("54", {}))
            provider_name = srv_info["provider"]
            
            final_rub, final_usd = get_server_price(provider_name, app_info['code'], c_id)
            
            if bal_usd < final_usd and bal_rub < final_rub and str(user_id) != str(ADMIN_ID):
                msg_text = (
                    f"❌ **عذراً، رصيد محفظتك غير كافٍ!**\n\n"
                    f"• سعر الرقم: **{final_rub} ₽ ({final_usd:.2f} $)**\n"
                    f"• رصيدك الحالي: **{bal_usd:.2f} $**\n\n"
                    f"👉 يرجى شحن رصيدك عبر قسم **🎳 شحن الرصيد**."
                )
                bot.send_message(chat_id, msg_text, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎳 شحن الرصيد", callback_data="btn_deposit")))
                return

            service_real_code = app_info['code']
            success, result = buy_server_number(provider_name, service_real_code, c_id)
            
            if success:
                update_user_balance(user_id, -final_usd, -final_rub)
                
                order_id = result['id']
                phone = result['phone']
                now = datetime.datetime.now()
                expire = now + datetime.timedelta(minutes=18)
                
                time_now_str = now.strftime("%H:%M | %Y-%m-%d")
                time_exp_str = expire.strftime("%H:%M | %Y-%m-%d")
                cost_str = f"{final_rub} ₽ ({final_usd:.2f} $)"
                
                order_text = (
                    f"╭━━〔 **NUMBER SMS** 〕━━╮\n"
                    f"💙 **تم شراء الرقم بنجاح**\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"🔔 • رقم الطلب : `{order_id}`\n"
                    f"🌍 • الدولة : **{c_info['title']} {c_info['flag']}**\n"
                    f"☎️ • الرقم : `+{phone}`\n"
                    f"🔑 • الكود : **قيد الانتظار ⏳**\n"
                    f"🔎 • الحالة : **RECEIVED 🔎**\n"
                    f"🛍️ • التطبيق : **{app_info['short']}**\n"
                    f"🏷️ • السعر : **{cost_str}**\n\n"
                    f"📫 • انشاء : `{time_now_str}`\n"
                    f"📬 • انتهاء : `{time_exp_str}`\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"📋 **انتظر، قد يستغرق وصول الكود بضع ثوانٍ**"
                )
                
                order_markup = types.InlineKeyboardMarkup(row_width=1)
                order_markup.add(types.InlineKeyboardButton("✤ 🔄 تغيير الرقم ✤", callback_data=f"change_num_{order_id}_{app_code}_{server_key}_{c_id}_{page}"))
                order_markup.add(types.InlineKeyboardButton("✤ 📩 طلب الكود ✤", callback_data=f"check_code_{order_id}_{provider_name}"))
                if app_code == "wa":
                    order_markup.add(types.InlineKeyboardButton("• تحقق من الرقم في WhatsApp ↗️ •", url=f"https://wa.me/{phone}"))
                order_markup.add(types.InlineKeyboardButton("✤ ❌ إلغاء الطلب ✤", callback_data=f"cancel_num_{order_id}_{phone}"))
                
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    text=order_text,
                    reply_markup=order_markup
                )
                
                t = threading.Thread(
                    target=monitor_sms_code,
                    args=(chat_id, call.message.message_id, order_id, phone, app_info['short'], f"{c_info['title']} {c_info['flag']}", cost_str, time_now_str, time_exp_str, final_usd, final_rub, user_id, provider_name),
                    daemon=True
                )
                t.start()
            else:
                bot.send_message(chat_id, f"❌ **تعذر حجز الرقم من المزود:**\n{result}\n\n👉 يرجى تجربة دولة أخرى أو السيرفر الآخر.")

        elif data.startswith("cancel_num_"):
            parts = data.split("_")
            order_id = parts[2]
            phone = parts[3]
            
            order_info = active_orders.get(order_id)
            if order_info:
                elapsed = time.time() - order_info["start_time"]
                if elapsed < 60:
                    remaining = int(60 - elapsed)
                    bot.send_message(chat_id, f"⏳ سياسة السيرفر تشترط الانتظار {remaining} ثانية لتفعيل زر الإلغاء!")
                    return
                
                provider_name = order_info.get("provider", "hero")
                set_server_status(provider_name, order_id, 8)
                update_user_balance(user_id, order_info["cost_usd"], order_info["cost_rub"])
                active_orders.pop(order_id, None)
                
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    text=f"⚠️ **تم إلغاء طلب الرقم `+{phone}` بنجاح!**\n\n✅ تم استرجاع كامل المبلغ إلى رصيد محفظتك.",
                    reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("☎️ شراء رقم آخر", callback_data="btn_buy_number"))
                )

        elif data.startswith("change_num_"):
            parts = data.split("_")
            old_order_id = parts[2]
            app_code = parts[3]
            server_key = parts[4]
            c_id = parts[5]
            page = parts[6] if len(parts) > 6 else "0"
            
            order_info = active_orders.get(old_order_id)
            if order_info:
                elapsed = time.time() - order_info["start_time"]
                if elapsed < 60:
                    remaining = int(60 - elapsed)
                    bot.send_message(chat_id, f"⏳ يرجى الانتظار {remaining} ثانية لاستبدال الرقم.")
                    return
                provider_name = order_info.get("provider", "hero")
                set_server_status(provider_name, old_order_id, 8)
                update_user_balance(user_id, order_info["cost_usd"], order_info["cost_rub"])
                active_orders.pop(old_order_id, None)
                
            router_callback(types.CallbackQuery(id="0", from_user=call.from_user, message=call.message, data=f"exec_buy_{app_code}_{server_key}_{c_id}_{page}", chat_instance=""))

        elif data.startswith("check_code_"):
            parts = data.split("_")
            order_id = parts[2]
            provider_name = parts[3] if len(parts) > 3 else "hero"
            
            resp = provider_api_request(provider_name, {'action': 'getStatus', 'id': order_id})
            if resp.startswith("STATUS_OK:"):
                code = resp.split(":")[1]
                bot.send_message(chat_id, f"🎉 الكود المستلم: `{code}`")
            elif resp == "STATUS_WAIT_CODE":
                bot.send_message(chat_id, "⏳ الكود قيد الانتظار، لم يصل بعد من السيرفر...")
            else:
                bot.send_message(chat_id, f"الحالة: {resp}")

        elif data == "btn_my_account":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("🎳 شحن الرصيد", callback_data="btn_deposit"))
            markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=f"🪪 **معلومات حسابك الشخصي:**\n\n• الاسم: **{call.from_user.first_name}**\n• المعرف (ID): `{user_id}`\n• الرصيد بالدولار: **{bal_usd:.2f} $**\n• الرصيد بالروبل: **{bal_rub:.1f} ₽**\n• سعر الصرف: **1$ = {RUB_PER_USD:.0f} ₽**\n• المشتريات: **{orders} رقم**",
                reply_markup=markup
            )

        # ----------------- لوحة تحكم الإدارة -----------------
        elif data == "btn_admin_panel":
            if str(user_id) != str(ADMIN_ID):
                return
            markup = build_admin_main_keyboard()
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text="👑 **لوحة تحكم إدارة المتجر والمستخدمين والشحن اليدوي:**",
                reply_markup=markup
            )

        elif data == "admin_check_plus":
            if str(user_id) != str(ADMIN_ID):
                return
            res = plus_request({'action': 'getBalance'})
            if res.startswith("ACCESS_BALANCE:"):
                bal_val = res.split(":")[1]
                bot.send_message(chat_id, f"🚀 **رصيد مزود Plus API:** `{bal_val} ₽`\n✅ السيرفر متصل.")
            else:
                bot.send_message(chat_id, f"🚀 **رد مزود Plus API:** `{res}`")

        elif data == "admin_check_provider":
            if str(user_id) != str(ADMIN_ID):
                return
            res = hero_request({'action': 'getBalance'})
            if res.startswith("ACCESS_BALANCE:"):
                bal_val = res.split(":")[1]
                bot.send_message(chat_id, f"💳 **رصيد مزود Hero SMS:** `{bal_val} $`\n✅ السيرفر متصل.")
            else:
                bot.send_message(chat_id, f"💳 **رد مزود Hero SMS:** `{res}`")

        elif data == "admin_view_users":
            if str(user_id) != str(ADMIN_ID):
                return
            users = get_all_users()
            total_users = len(users)
            total_balance = sum(u[3] for u in users) if users else 0.0
            
            user_list_text = f"👥 **إحصائيات وقائمة المستخدمين ({total_users}):**\n"
            user_list_text += f"💰 إجمالي الأرصدة الموزعة: **{total_balance:.2f} $**\n━━━━━━━━━━━━━━━━━━\n\n"
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            for u in users[:15]:
                uid, uname, fname, ubal, ubanned, joined = u
                b_icon = "🚫" if ubanned else "👤"
                btn_title = f"{b_icon} {fname} | {ubal:.2f}$ | ID: {uid}"
                markup.add(types.InlineKeyboardButton(btn_title, callback_data=f"adm_userinfo_{uid}"))
                
            markup.add(types.InlineKeyboardButton("🔍 بحث عن مستخدم محدد برقم ID", callback_data="admin_search_user"))
            markup.add(types.InlineKeyboardButton("🔙 العودة للوحة الإدارة", callback_data="btn_admin_panel"))
            
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=user_list_text + "👇 اضغط على أي مستخدم للتحكم به مباشرة:",
                reply_markup=markup
            )

        elif data.startswith("adm_userinfo_"):
            if str(user_id) != str(ADMIN_ID):
                return
            target_uid = data.replace("adm_userinfo_", "")
            user_info = get_single_user_info(target_uid)
            if not user_info:
                bot.send_message(chat_id, "❌ لم يتم العثور على المستخدم.")
                return
            uid, uname, fname, bal_usd, bal_rub, orders, is_banned, joined = user_info
            status_text = "🚫 محظور (مطرود)" if is_banned else "✅ نشط"
            card = (
                f"👤 **بطاقة التحكم بالمستخدم:**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"• الاسم: **{fname}**\n"
                f"• المعرف (ID): `{uid}`\n"
                f"• اليوزر: @{uname if uname else 'بدون_يوزر'}\n"
                f"• الرصيد: **{bal_usd:.2f} $** ({bal_rub:.1f} ₽)\n"
                f"• المشتريات: **{orders} رقم**\n"
                f"• الحالة: **{status_text}**\n"
                f"• تاريخ الانضمام: `{joined}`\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            u_markup = types.InlineKeyboardMarkup(row_width=2)
            u_markup.add(
                types.InlineKeyboardButton("➕ شحن رصيد", callback_data=f"adm_addbal_{uid}"),
                types.InlineKeyboardButton("➖ خصم رصيد", callback_data=f"adm_subbal_{uid}")
            )
            ban_btn_text = "🟢 إلغاء الحظر" if is_banned else "🚫 طرد / حظر"
            ban_cb = f"adm_unban_{uid}" if is_banned else f"adm_ban_{uid}"
            u_markup.add(
                types.InlineKeyboardButton(ban_btn_text, callback_data=ban_cb),
                types.InlineKeyboardButton("✉️ مراسلة خاصة", callback_data=f"adm_msg_{uid}")
            )
            u_markup.add(types.InlineKeyboardButton("🔙 رجوع لقائمة المستخدمين", callback_data="admin_view_users"))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=card, reply_markup=u_markup)

        elif data == "admin_search_user":
            if str(user_id) != str(ADMIN_ID):
                return
            user_states[str(user_id)] = {"action": "admin_search_user"}
            bot.send_message(chat_id, "🔍 **أرسل الآن معرف المستخدم (User ID) أو اليوزرنيم للبحث عنه:**")

        elif data.startswith("adm_addbal_"):
            if str(user_id) != str(ADMIN_ID):
                return
            target_uid = data.replace("adm_addbal_", "")
            user_states[str(user_id)] = {"action": "admin_input_add_amt", "target_uid": target_uid}
            bot.send_message(chat_id, f"➕ **أرسل المبلغ المراد شحنه للمستخدم `{target_uid}` بالدولار (مثال: 5):**")

        elif data.startswith("adm_subbal_"):
            if str(user_id) != str(ADMIN_ID):
                return
            target_uid = data.replace("adm_subbal_", "")
            user_states[str(user_id)] = {"action": "admin_input_sub_amt", "target_uid": target_uid}
            bot.send_message(chat_id, f"➖ **أرسل المبلغ المراد خصمه من المستخدم `{target_uid}` بالدولار (مثال: 2):**")

        elif data.startswith("adm_ban_"):
            if str(user_id) != str(ADMIN_ID):
                return
            target_uid = data.replace("adm_ban_", "")
            set_user_ban_status(target_uid, True)
            try:
                bot.send_message(target_uid, "⛔ **تم حظرك وطردك من استخدام البوت بقرار من الإدارة.**")
            except Exception:
                pass
            router_callback(types.CallbackQuery(id="0", from_user=call.from_user, message=call.message, data=f"adm_userinfo_{target_uid}", chat_instance=""))

        elif data.startswith("adm_unban_"):
            if str(user_id) != str(ADMIN_ID):
                return
            target_uid = data.replace("adm_unban_", "")
            set_user_ban_status(target_uid, False)
            try:
                bot.send_message(target_uid, "🎉 **تم فك الحظر عن حسابك! يمكنك الآن استخدام البوت بشكل طبيعي.**")
            except Exception:
                pass
            router_callback(types.CallbackQuery(id="0", from_user=call.from_user, message=call.message, data=f"adm_userinfo_{target_uid}", chat_instance=""))

        elif data.startswith("adm_msg_"):
            if str(user_id) != str(ADMIN_ID):
                return
            target_uid = data.replace("adm_msg_", "")
            user_states[str(user_id)] = {"action": "send_direct_message", "target_uid": target_uid}
            bot.send_message(chat_id, f"✉️ **أرسل نص الرسالة التي تريد إرسالها للمستخدم `{target_uid}`:**")

        elif data == "admin_prompt_broadcast":
            if str(user_id) != str(ADMIN_ID):
                return
            user_states[str(user_id)] = {"action": "broadcast_all"}
            bot.send_message(chat_id, "📢 **أرسل الآن نص الرسالة أو الإعلان المراد إذاعته لجميع المستخدمين:**")

    except Exception as e:
        print(f"Callback error: {e}")

# ----------------- تشغيل المحرك -----------------
def start_bot():
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass

    try:
        commands = [
            types.BotCommand("start", "🏠 القائمة الرئيسية"),
            types.BotCommand("buy", "☎️ شراء رقم افتراضي"),
            types.BotCommand("deposit", "🎳 شحن الرصيد"),
            types.BotCommand("transfer", "🔄 تحويل الرصيد مجاناً"),
            types.BotCommand("account", "🪪 حسابي والمحفظة"),
            types.BotCommand("support", "💬 الدعم الفني والمساعدة"),
            types.BotCommand("admin", "👑 لوحة تحكم الإدارة")
        ]
        bot.set_my_commands(commands)
    except Exception:
        pass

    print("🚀 DUAL SERVER (PLUS SMS & HERO SMS) WITH ACCURATE ROUTING IS LIVE...")
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=15, skip_pending=True)
        except Exception as e:
            print(f"Loop auto-recovery: {e}")
            time.sleep(2)

if __name__ == "__main__":
    start_bot()