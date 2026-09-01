import os
import sys
import time
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
    API_KEY = getattr(config, 'HERO_SMS_API_KEY', '67ef5b751b1A4f2bef57dAd7bA2A248c').strip()
    ADMIN_ID = str(getattr(config, 'ADMIN_ID', '8097770003')).strip()
    SUPPORT_USERNAME = getattr(config, 'SUPPORT_USERNAME', 'Yas_in7').strip()
    CURRENCY = getattr(config, 'CURRENCY', '$').strip()
    MAIN_CHANNEL_URL = getattr(config, 'MAIN_CHANNEL_URL', 'https://t.me/Yas_in7').strip()
    INSTRUCTIONS_CHANNEL_URL = getattr(config, 'INSTRUCTIONS_CHANNEL_URL', 'https://t.me/Yas_in7').strip()
    ACTIVATION_CHANNEL_ID = getattr(config, 'ACTIVATION_CHANNEL_ID', '').strip()
except Exception:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8998307482:AAHlUFDu0E_0ltdVQVEGQ5z2pats24kK3rU").strip()
    API_KEY = os.getenv("HERO_SMS_API_KEY", "67ef5b751b1A4f2bef57dAd7bA2A248c").strip()
    ADMIN_ID = str(os.getenv("ADMIN_ID", "8097770003")).strip()
    SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "Yas_in7").strip()
    CURRENCY = "$"
    MAIN_CHANNEL_URL = os.getenv("MAIN_CHANNEL_URL", "https://t.me/Yas_in7").strip()
    INSTRUCTIONS_CHANNEL_URL = os.getenv("INSTRUCTIONS_CHANNEL_URL", "https://t.me/Yas_in7").strip()
    ACTIVATION_CHANNEL_ID = os.getenv("ACTIVATION_CHANNEL_ID", "").strip()

import catalog

RUB_PER_USD = 30.0
PAGE_SIZE = 12

PAYMENT_INFO = {
    "jeeb": {"name": "ياسين علي اليمني", "acc": "3093092", "desc": "محفظة جيب (Jeeb)"},
    "kuraimi": {"name": "ياسين محمد احمد اليمني", "acc": "3068499525", "desc": "بنك الكريمي (حساب مميز)"},
    "binance": {"name": "Yassin AL yemeni", "acc": "979688758", "desc": "بينانس (Binance Pay ID)"}
}

session = requests.Session()
retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries, pool_connections=50, pool_maxsize=100)
session.mount("https://", adapter)
session.mount("http://", adapter)

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
                joined_at TEXT,
                referrer_id TEXT DEFAULT ''
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Init DB Error: {e}")

init_db()

def get_or_create_user(user_id, username="", first_name="", referrer_id=""):
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
                'INSERT INTO users (user_id, username, first_name, balance, rub_balance, orders_count, is_banned, joined_at, referrer_id) VALUES (?, ?, ?, ?, ?, 0, 0, ?, ?)',
                (uid_str, uname, fname, init_bal, init_rub, now_str, str(referrer_id))
            )
            conn.commit()
            conn.close()

            # مكافأة الإحالة إذا دخل عبر مستخدم آخر
            if referrer_id and referrer_id != uid_str:
                update_user_balance(referrer_id, 0.05) # 5 سنت مكافأة دعوة
                try:
                    bot.send_message(referrer_id, f"🎁 حصلت على **+0.05 $** هدية لانضمام صديق عبر رابط إحالتك!")
                except Exception:
                    pass

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

# ----------------- خادم Keep-Alive -----------------
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Number SMS Store Engine Online 24/7")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()

    def log_message(self, format, *args):
        return

def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        server.serve_forever()
    except Exception as e:
        print(f"Server notice: {e}")

web_thread = threading.Thread(target=start_health_server, daemon=True)
web_thread.start()

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

API_ENDPOINTS = [
    "https://sms-hero.com/stubs/handler_api.php",
    "https://hero-sms.com/stubs/handler_api.php",
    "https://api.sms-hero.com/stubs/handler_api.php"
]

def api_request(params):
    params['api_key'] = API_KEY
    for endpoint in API_ENDPOINTS:
        try:
            res = session.get(endpoint, params=params, timeout=7)
            if res.status_code == 200 and res.text.strip():
                return res.text.strip()
        except Exception:
            continue
    return "ERROR_CONNECTION"

def fetch_hero_balance():
    resp = api_request({'action': 'getBalance'})
    if resp.startswith("ACCESS_BALANCE:"):
        return True, resp.split(":")[1]
    return False, f"رد المزود: {resp}"

def buy_hero_number(service_code, country_id):
    resp = api_request({'action': 'getNumber', 'service': service_code, 'country': country_id})
    if resp.startswith("ACCESS_NUMBER:"):
        parts = resp.split(":")
        return True, {"id": parts[1], "phone": parts[2]}
    elif resp == "NO_NUMBERS":
        return False, "الأرقام لهذه الدولة غير متوفرة حالياً في هذا السيرفر."
    elif resp == "NO_BALANCE":
        return False, "رصيد السيرفر غير كافٍ."
    return False, f"رد المزود: {resp}"

def set_status(order_id, status_code):
    threading.Thread(target=api_request, args=({'action': 'setStatus', 'id': order_id, 'status': status_code},), daemon=True).start()

active_orders = {}

def monitor_sms_code(chat_id, message_id, order_id, phone_number, app_name, country_title, cost_str, time_now_str, time_exp_str, cost_usd, cost_rub, user_id):
    active_orders[order_id] = {
        "user_id": user_id, "start_time": time.time(),
        "cost_usd": cost_usd, "cost_rub": cost_rub, "phone": phone_number
    }
    max_duration = 1080
    start_time = time.time()

    while time.time() - start_time < max_duration:
        time.sleep(4)
        if order_id not in active_orders:
            return
        try:
            resp = api_request({'action': 'getStatus', 'id': order_id})
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
                set_status(order_id, 6)
                active_orders.pop(order_id, None)
                send_activation_log(user_id, country_title, app_name, phone_number, code, cost_str, order_id)
                return
            elif resp == "STATUS_CANCEL":
                bot.send_message(chat_id, f"⚠️ تم إلغاء طلب الرقم `+{phone_number}` واسترجاع الرصيد لمحفظتك.")
                update_user_balance(user_id, cost_usd, cost_rub)
                active_orders.pop(order_id, None)
                return
        except Exception:
            pass

    if order_id in active_orders:
        set_status(order_id, 8)
        update_user_balance(user_id, cost_usd, cost_rub)
        active_orders.pop(order_id, None)
        try:
            bot.send_message(chat_id, f"⌛ **انتهت المهلة للرقم `+{phone_number}`.**\n🛡️ تم استرجاع كامل المبلغ ({cost_str}) لمحفظتك تلقائياً.")
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
    markup.add(types.InlineKeyboardButton("🎥 TIKTOK - تيك توك", callback_data="srv_lf"), types.InlineKeyboardButton("☂️ Google - جوجل", callback_data="srv_go"))
    markup.add(types.InlineKeyboardButton("♣️ SNAP - سناب شات", callback_data="srv_sn"), types.InlineKeyboardButton("🪗 HARAJ - حراج", callback_data="srv_hj"))
    markup.add(types.InlineKeyboardButton("💎 IMO - ايمو", callback_data="srv_im"), types.InlineKeyboardButton("🤖 السيرفر العام", callback_data="srv_ot"))
    markup.add(types.InlineKeyboardButton("🏐 PAYPAL - بايبال", callback_data="srv_pp"), types.InlineKeyboardButton("📳 Viber - فايبر", callback_data="srv_vi"))
    markup.add(types.InlineKeyboardButton("✤ ↩️ عودة ✤", callback_data="back_to_main"))
    return markup

def build_servers_keyboard(app_code):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🌟 السيرفر (1) VIP الملكي - أعلى جودة وسرعة", callback_data=f"page_{app_code}_s1_0"),
        types.InlineKeyboardButton("⚡ السيرفر (2) السريع الاقتصادي - أفضل سعر", callback_data=f"page_{app_code}_s2_0"),
        types.InlineKeyboardButton("🎯 السيرفر (3) الاحتياطي الشامل - أكثر توفراً", callback_data=f"page_{app_code}_s3_0")
    )
    markup.add(types.InlineKeyboardButton("🔍 🚀 البحث عن دولة بالاسم 🧩", callback_data=f"prompt_search_country_{app_code}"))
    markup.add(types.InlineKeyboardButton("✤ ↩️ عودة ✤", callback_data="btn_buy_number"))
    return markup

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
        buttons.append(types.InlineKeyboardButton(btn_text, callback_data=f"card_{app_code}_{server_key}_{c_id}"))
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
    markup.add(types.InlineKeyboardButton("💳 فحص رصيد Hero SMS", callback_data="admin_check_provider"))
    markup.add(types.InlineKeyboardButton("🔙 العودة للواجهة الرئيسية", callback_data="back_to_main"))
    return markup

# ----------------- معالجة الأوامر -----------------
@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or ""
        first_name = message.from_user.first_name or "صديقنا"

        # التحقق من الإحالة (Referral)
        referrer_id = ""
        parts = message.text.split()
        if len(parts) > 1 and parts[1].isdigit():
            referrer_id = parts[1]

        bal_usd, bal_rub, orders, is_banned, fn, un = get_or_create_user(user_id, username, first_name, referrer_id)

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
        print(f"Start error: {e}")

@bot.message_handler(commands=['buy'])
def buy_command(message):
    bot.reply_to(message, "📱 **اختر التطبيق المراد تفعيله:**", reply_markup=build_apps_keyboard())

@bot.message_handler(commands=['deposit'])
def deposit_command(message):
    user_id = message.from_user.id
    bal_usd, _, _, _, _, _ = get_or_create_user(user_id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("📱 محفظة جيب (Jeeb)", callback_data="pay_jeeb"))
    markup.add(types.InlineKeyboardButton("🏦 بنك الكريمي", callback_data="pay_kuraimi"))
    markup.add(types.InlineKeyboardButton("🪙 بينانس (Binance Pay)", callback_data="pay_binance"))
    markup.add(types.InlineKeyboardButton("🔙 العودة", callback_data="back_to_main"))
    bot.reply_to(message, f"💳 **اختر وسيلة الدفع لشحن رصيدك:**\nرصيدك الحالي: **{bal_usd:.2f} $**", reply_markup=markup)

@bot.message_handler(commands=['transfer'])
def transfer_command(message):
    user_states[str(message.from_user.id)] = {"action": "transfer_step_1_id"}
    bot.reply_to(message, "🔄 **أرسل الآن معرف (ID) المستخدم المراد التحويل له مجاناً:**")

@bot.message_handler(commands=['account'])
def account_command(message):
    uid = message.from_user.id
    bal_usd, bal_rub, orders, _, _, _ = get_or_create_user(uid)
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎳 شحن الرصيد", callback_data="btn_deposit"))
    bot.reply_to(message, f"🪪 **حسابك:**\n• ID: `{uid}`\n• الرصيد: **{bal_usd:.2f} $ ({bal_rub:.1f} ₽)**\n• المشتريات: **{orders} رقم**", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.reply_to(message, "⛔ هذا الأمر مخصص لمدير البوت فقط!")
        return
    bot.reply_to(message, "👑 **لوحة تحكم الإدارة الشاملة:**", reply_markup=build_admin_main_keyboard())

# ----------------- معالجة نصوص المستخدم -----------------
@bot.message_handler(func=lambda msg: not msg.text.startswith('/'))
def handle_all_text_messages(message):
    try:
        user_id_str = str(message.from_user.id)
        text = message.text.strip()
        state = user_states.pop(user_id_str, None)

        if not state:
            return

        action = state.get("action")

        if action == "transfer_step_1_id":
            target_uid = text.strip()
            if target_uid == user_id_str:
                bot.reply_to(message, "❌ لا يمكنك تحويل الرصيد لنفسك!")
                return
            target_user = get_single_user_info(target_uid)
            if not target_user:
                bot.reply_to(message, f"❌ لم يتم العثور على مستخدم بالمعرف `{target_uid}`.")
                return

            user_states[user_id_str] = {"action": "transfer_step_2_amount", "target_uid": target_uid, "target_name": target_user[2]}
            bot.reply_to(message, f"👤 **المستلم:** **{target_user[2]}** (`{target_uid}`)\n💵 **أرسل الآن المبلغ المراد تحويله بالدولار:**")

        elif action == "transfer_step_2_amount":
            target_uid = state.get("target_uid")
            target_name = state.get("target_name")
            try:
                amt = float(text)
                if amt <= 0:
                    bot.reply_to(message, "❌ المبلغ يجب أن يكون أكبر من 0.")
                    return
                sender_usd, _, _, _, _, _ = get_or_create_user(message.from_user.id)
                if sender_usd < amt:
                    bot.reply_to(message, f"❌ **رصيدك غير كافٍ!** رصيدك الحالي: **{sender_usd:.2f} $**")
                    return

                update_user_balance(message.from_user.id, -amt)
                update_user_balance(target_uid, amt)

                bot.reply_to(message, f"✅ **تم تحويل {amt:.2f} $ بنجاح إلى {target_name}!**")
                try:
                    bot.send_message(target_uid, f"🎉 **وصلك تحويل رصيد جديد!**\n👤 • من: `{user_id_str}`\n💵 • المبلغ: **+{amt:.2f} $**")
                except Exception:
                    pass
            except Exception:
                bot.reply_to(message, "❌ يرجى إدخال رقم صحيح.")

        elif action == "search_country_for_app":
            app_code = state.get("app_code", "wa")
            server_key = state.get("server_key", "s1")
            search_query = text.lower()

            matched_countries = []
            for c_id, c_info in catalog.COUNTRIES.items():
                if (search_query in c_info["name"].lower() or search_query in c_info["title"].lower() or search_query in c_info["prefix"] or search_query == c_id):
                    matched_countries.append((c_id, c_info))

            if not matched_countries:
                bot.reply_to(message, f"🔍 لم يتم العثور على دولة مطابقة لـ `{text}`.")
                return

            markup = types.InlineKeyboardMarkup(row_width=2)
            for c_id, c_info in matched_countries:
                btn_text = f"{c_info['flag']} {c_info['title']}"
                markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"card_{app_code}_{server_key}_{c_id}"))
            markup.add(types.InlineKeyboardButton("🔙 عودة", callback_data=f"page_{app_code}_{server_key}_0"))
            bot.reply_to(message, f"🎯 **نتائج البحث عن ({text}):**", reply_markup=markup)

        elif action == "admin_input_add_target" and user_id_str == str(ADMIN_ID):
            user_states[user_id_str] = {"action": "admin_input_add_amt", "target_uid": text.strip()}
            bot.reply_to(message, f"➕ **أرسل المبلغ المراد شحنه للمستخدم `{text}` بالدولار:**")

        elif action == "admin_input_add_amt" and user_id_str == str(ADMIN_ID):
            target_uid = state.get("target_uid")
            try:
                amt = float(text)
                update_user_balance(target_uid, amt)
                bot.reply_to(message, f"✅ **تم شحن {amt:.2f} $ بنجاح لحساب `{target_uid}`.**")
                try:
                    bot.send_message(target_uid, f"🎉 **تم إيداع رصيد جديد في محفظتك!**\n💵 المبلغ: **{amt:.2f} $**")
                except Exception:
                    pass
            except Exception:
                bot.reply_to(message, "❌ القيمة المدخلة غير صحيحة.")

        elif action == "admin_input_sub_amt" and user_id_str == str(ADMIN_ID):
            target_uid = state.get("target_uid")
            try:
                amt = float(text)
                update_user_balance(target_uid, -amt)
                bot.reply_to(message, f"✅ **تم خصم {amt:.2f} $ بنجاح من حساب `{target_uid}`.**")
            except Exception:
                bot.reply_to(message, "❌ القيمة المدخلة غير صحيحة.")

        elif action == "send_direct_message" and user_id_str == str(ADMIN_ID):
            target_uid = state.get("target_uid")
            try:
                bot.send_message(target_uid, f"📩 **رسالة خاصة من إدارة البوت:**\n\n{text}")
                bot.reply_to(message, f"✅ **تم إرسال الرسالة بنجاح إلى المستخدم `{target_uid}`.**")
            except Exception as e:
                bot.reply_to(message, f"❌ فشل إرسال الرسالة: {e}")

        elif action == "verify_auto_payment":
            notify_admin = (
                f"🔔 **طلب شحن جديد!**\n"
                f"👤 • المستخدم : `{user_id_str}`\n"
                f"🧾 • رقم الإشعار : `{text}`\n"
                f"⏰ • الوقت : `{datetime.datetime.now().strftime('%H:%M | %Y-%m-%d')}`"
            )
            adm_markup = types.InlineKeyboardMarkup(row_width=2)
            adm_markup.add(
                types.InlineKeyboardButton("➕ شحن رصيد له", callback_data=f"adm_addbal_{user_id_str}"),
                types.InlineKeyboardButton("👤 حسابه", callback_data=f"adm_userinfo_{user_id_str}")
            )
            try:
                bot.send_message(ADMIN_ID, notify_admin, reply_markup=adm_markup)
            except Exception:
                pass
            bot.reply_to(message, "✅ **تم استلام رقم العملية بنجاح!** جاري المراجعة والإيداع.")

        elif action == "broadcast_all" and user_id_str == str(ADMIN_ID):
            users = get_all_users()
            sent = 0
            for u in users:
                try:
                    bot.send_message(u[0], f"📢 **إشعار هام من إدارة البوت:**\n\n{text}")
                    sent += 1
                    time.sleep(0.04)
                except Exception:
                    continue
            bot.send_message(user_id_str, f"✅ اكتملت الإذاعة لـ **{sent}** مستخدم.")

    except Exception as e:
        print(f"Handle text error: {e}")

# ----------------- معالجة أزرار الكولباك -----------------
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
            return

        if data == "back_to_main":
            text = (
                f"╭━━━〔 **NUMBER SMS** 〕━━━╮\n"
                f"🛍️ أهلاً بك في المتجر الأقوى للأرقام والتفعيلات الفورية!\n\n"
                f"👤 • معرفك (ID): `{user_id}`\n"
                f"💵 • رصيدك الحالي: **{bal_usd:.2f} {CURRENCY} | {bal_rub:.1f} ₽**\n"
                f"╰━━━━━━━━━━━━━━━━━╯"
            )
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=build_main_keyboard(user_id))

        elif data == "btn_free_points":
            bot_info = bot.get_me()
            ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
            ref_text = (
                f"💎 **نظام ربح الرصيد المجاني عبر الإحالة (Referral):**\n\n"
                f"🎁 شارك رابطك الخاص مع أصدقائك، واحصل على **+0.05 $** رصيد مجاني لكل شخص يسجل في البوت!\n\n"
                f"🔗 **رابطك الخاص:**\n`{ref_link}`"
            )
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 عودة", callback_data="back_to_main"))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=ref_text, reply_markup=markup)

        elif data == "btn_stats":
            users = get_all_users()
            stats_text = (
                f"📊 **إحصائيات متجر Number SMS:**\n\n"
                f"👥 • إجمالي المستخدمين: **{len(users)}** عضو\n"
                f"⚡ • حالة السيرفرات: **نشطة وتعمل بنسبة 100%**\n"
                f"🛡️ • نسبة نجاح وصول الأكواد: **99.2%**"
            )
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 عودة", callback_data="back_to_main"))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=stats_text, reply_markup=markup)

        elif data == "btn_bestseller":
            text = "📈 **الأكثر مبيعاً وطلباً:**\n\n1️⃣ WhatsApp (اليمن - مصر - البرازيل)\n2️⃣ Telegram (أمريكا - إندونيسيا)\n3️⃣ Google / Gmail"
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("☎️ شراء رقم الآن", callback_data="btn_buy_number"))
            markup.add(types.InlineKeyboardButton("🔙 عودة", callback_data="back_to_main"))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

        elif data in ["btn_services_games", "btn_extra_features"]:
            bot.send_message(chat_id, f"🚀 هذه الخدمة قيد التحديث والإضافة قريباً! للمزيد تواصل مع الإدارة @{SUPPORT_USERNAME}")

        elif data == "btn_transfer_balance":
            user_states[str(user_id)] = {"action": "transfer_step_1_id"}
            bot.send_message(chat_id, f"🔄 **تحويل الرصيد المجاني (0% عمولة):**\nرصيدك: **{bal_usd:.2f} $**\n👉 أرسل ID المستلم:")

        elif data == "btn_deposit":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("📱 محفظة جيب (Jeeb)", callback_data="pay_jeeb"))
            markup.add(types.InlineKeyboardButton("🏦 بنك الكريمي", callback_data="pay_kuraimi"))
            markup.add(types.InlineKeyboardButton("🪙 منصة بينانس (Binance)", callback_data="pay_binance"))
            markup.add(types.InlineKeyboardButton("🔙 عودة للرئيسية", callback_data="back_to_main"))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="💳 **اختر وسيلة الدفع:**", reply_markup=markup)

        elif data == "pay_jeeb":
            info = PAYMENT_INFO["jeeb"]
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("⚡ تأكيد الدفع التلقائي", callback_data="confirm_pay_jeeb"))
            markup.add(types.InlineKeyboardButton("🔙 عودة", callback_data="btn_deposit"))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"📱 **محفظة جيب:**\nالرقم البديل: `{info['acc']}`\nالاسم: **{info['name']}**", reply_markup=markup)

        elif data == "pay_kuraimi":
            info = PAYMENT_INFO["kuraimi"]
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("💬 مراسلة الدعم", url=f"https://t.me/{SUPPORT_USERNAME}")).add(types.InlineKeyboardButton("🔙 عودة", callback_data="btn_deposit"))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"🏦 **بنك الكريمي:**\nالحساب: `{info['acc']}`\nالاسم: **{info['name']}**", reply_markup=markup)

        elif data == "pay_binance":
            info = PAYMENT_INFO["binance"]
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("⚡ تأكيد الدفع", callback_data="confirm_pay_binance"))
            markup.add(types.InlineKeyboardButton("🔙 عودة", callback_data="btn_deposit"))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"🪙 **Binance Pay ID:**\nالـ ID: `{info['acc']}`\nالاسم: **{info['name']}**", reply_markup=markup)

        elif data == "confirm_pay_jeeb":
            user_states[str(user_id)] = {"action": "verify_auto_payment", "method": "jeeb"}
            bot.send_message(chat_id, "📱 أرسل رقم العملية في محفظة جيب:")

        elif data == "confirm_pay_binance":
            user_states[str(user_id)] = {"action": "verify_auto_payment", "method": "binance"}
            bot.send_message(chat_id, "🪙 أرسل رقم العملية من بينانس:")

        elif data in ["btn_buy_number", "btn_offers_wa", "btn_ready_tg"]:
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="📱 **اختر التطبيق المطلوب:**", reply_markup=build_apps_keyboard())

        elif data.startswith("srv_"):
            app_code = data.replace("srv_", "")
            app_info = catalog.SERVICES.get(app_code, catalog.SERVICES["wa"])
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"• **التطبيق : {app_info['name']}**\nاختر السيرفر:", reply_markup=build_servers_keyboard(app_code))

        elif data.startswith("page_"):
            parts = data.split("_")
            app_code, server_key, page = parts[1], parts[2], int(parts[3])
            markup = build_countries_page_keyboard(app_code, server_key, page)
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="🌍 **اختر الدولة المطلوبة:**", reply_markup=markup)

        elif data.startswith("prompt_search_country_"):
            parts = data.split("_")
            app_code = parts[3]
            server_key = parts[4] if len(parts) > 4 else "s1"
            user_states[str(user_id)] = {"action": "search_country_for_app", "app_code": app_code, "server_key": server_key}
            bot.send_message(chat_id, "🔍 **أرسل اسم الدولة أو مفتاحها:**")

        elif data.startswith("card_"):
            parts = data.split("_")
            app_code, server_key, c_id = parts[1], parts[2], parts[3]
            app_info = catalog.SERVICES.get(app_code, catalog.SERVICES["wa"])
            srv_info = catalog.SERVERS.get(server_key, catalog.SERVERS["s1"])
            c_info = catalog.COUNTRIES.get(c_id, catalog.COUNTRIES.get("73", {}))

            final_usd = round(c_info["base_usd"] * srv_info["multiplier"], 2)
            final_rub = round(final_usd * RUB_PER_USD, 1)

            text = (
                f"➕ **شراء رقم جديد ✅**\n\n"
                f"➖ **التطبيق | {app_info['short']}**\n"
                f"➖ **الدولة | {c_info['title']} {c_info['flag']} (+{c_info['prefix']})**\n"
                f"➖ **السيرفر | {srv_info['badge']}**\n"
                f"➖ **السعر | {final_rub} ₽ ({final_usd:.2f} $)**"
            )
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(f"💳 تأكيد الشراء ({final_usd:.2f} $)", callback_data=f"exec_buy_{app_code}_{server_key}_{c_id}"))
            markup.add(types.InlineKeyboardButton("🔙 عودة", callback_data=f"page_{app_code}_{server_key}_0"))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

        elif data.startswith("exec_buy_"):
            parts = data.split("_")
            app_code, server_key, c_id = parts[2], parts[3], parts[4]
            app_info = catalog.SERVICES.get(app_code, catalog.SERVICES["wa"])
            srv_info = catalog.SERVERS.get(server_key, catalog.SERVERS["s1"])
            c_info = catalog.COUNTRIES.get(c_id, catalog.COUNTRIES.get("73", {}))

            final_usd = round(c_info["base_usd"] * srv_info["multiplier"], 2)
            final_rub = round(final_usd * RUB_PER_USD, 1)

            if bal_usd < final_usd and str(user_id) != str(ADMIN_ID):
                bot.send_message(chat_id, f"❌ **رصيدك غير كافٍ!**\nالسعر: {final_usd:.2f} $\nرصيدك: {bal_usd:.2f} $")
                return

            success, result = buy_hero_number(app_info['code'], c_id)
            if success:
                update_user_balance(user_id, -final_usd, -final_rub)
                order_id, phone = result['id'], result['phone']
                now = datetime.datetime.now()
                expire = now + datetime.timedelta(minutes=18)
                cost_str = f"{final_rub} ₽ ({final_usd:.2f} $)"

                order_text = (
                    f"╭━━〔 **NUMBER SMS** 〕━━╮\n"
                    f"💙 **تم شراء الرقم بنجاح**\n"
                    f"🔔 • رقم الطلب : `{order_id}`\n"
                    f"🌍 • الدولة : **{c_info['title']} {c_info['flag']}**\n"
                    f"☎️ • الرقم : `+{phone}`\n"
                    f"🔑 • الكود : **قيد الانتظار ⏳**\n"
                    f"🛍️ • التطبيق : **{app_info['short']}**\n"
                    f"🏷️ • السعر : **{cost_str}**"
                )
                order_markup = types.InlineKeyboardMarkup(row_width=1)
                order_markup.add(types.InlineKeyboardButton("✤ 📩 فحص الكود ✤", callback_data=f"check_code_{order_id}"))
                order_markup.add(types.InlineKeyboardButton("✤ ❌ إلغاء الطلب ✤", callback_data=f"cancel_num_{order_id}_{phone}"))

                bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=order_text, reply_markup=order_markup)
                threading.Thread(target=monitor_sms_code, args=(chat_id, call.message.message_id, order_id, phone, app_info['short'], f"{c_info['title']} {c_info['flag']}", cost_str, "", "", final_usd, final_rub, user_id), daemon=True).start()
            else:
                bot.send_message(chat_id, f"❌ **تعذر حجز الرقم:**\n{result}")

        elif data.startswith("cancel_num_"):
            parts = data.split("_")
            order_id, phone = parts[2], parts[3]
            order_info = active_orders.get(order_id)
            if order_info:
                elapsed = time.time() - order_info["start_time"]
                if elapsed < 60:
                    bot.send_message(chat_id, f"⏳ يجب الانتظار {int(60 - elapsed)} ثانية للإلغاء.")
                    return
                set_status(order_id, 8)
                update_user_balance(user_id, order_info["cost_usd"], order_info["cost_rub"])
                active_orders.pop(order_id, None)
                bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"✅ تم إلغاء الرقم `+{phone}` واسترجاع الرصيد.")

        elif data.startswith("check_code_"):
            order_id = data.replace("check_code_", "")
            resp = api_request({'action': 'getStatus', 'id': order_id})
            if resp.startswith("STATUS_OK:"):
                bot.send_message(chat_id, f"🎉 الكود المستلم: `{resp.split(':')[1]}`")
            else:
                bot.send_message(chat_id, "⏳ الكود قيد الانتظار...")

        elif data == "btn_my_account":
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎳 شحن الرصيد", callback_data="btn_deposit")).add(types.InlineKeyboardButton("🔙 عودة", callback_data="back_to_main"))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"🪪 **حسابك الشخصي:**\n• ID: `{user_id}`\n• الرصيد: **{bal_usd:.2f} $ ({bal_rub:.1f} ₽)**\n• المشتريات: **{orders} رقم**", reply_markup=markup)

        # ----------------- لوحة الأدمن -----------------
        elif data == "btn_admin_panel" and str(user_id) == str(ADMIN_ID):
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="👑 **لوحة تحكم الإدارة:**", reply_markup=build_admin_main_keyboard())

        elif data == "admin_view_users" and str(user_id) == str(ADMIN_ID):
            users = get_all_users()
            markup = types.InlineKeyboardMarkup(row_width=1)
            for u in users[:15]:
                markup.add(types.InlineKeyboardButton(f"{u[2]} | {u[3]:.2f}$ | ID: {u[0]}", callback_data=f"adm_userinfo_{u[0]}"))
            markup.add(types.InlineKeyboardButton("🔙 عودة", callback_data="btn_admin_panel"))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"👥 **إجمالي المستخدمين:** {len(users)}", reply_markup=markup)

        elif data.startswith("adm_userinfo_") and str(user_id) == str(ADMIN_ID):
            target_uid = data.replace("adm_userinfo_", "")
            u = get_single_user_info(target_uid)
            if u:
                u_markup = types.InlineKeyboardMarkup(row_width=2)
                u_markup.add(types.InlineKeyboardButton("➕ شحن رصيد", callback_data=f"adm_addbal_{u[0]}"), types.InlineKeyboardButton("➖ خصم رصيد", callback_data=f"adm_subbal_{u[0]}"))
                u_markup.add(types.InlineKeyboardButton("🚫 حظر" if not u[6] else "🟢 فك الحظر", callback_data=f"adm_ban_{u[0]}" if not u[6] else f"adm_unban_{u[0]}"), types.InlineKeyboardButton("✉️ مراسلة", callback_data=f"adm_msg_{u[0]}"))
                u_markup.add(types.InlineKeyboardButton("🔙 عودة", callback_data="admin_view_users"))
                bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"👤 **المستخدم:** {u[2]}\n• ID: `{u[0]}`\n• الرصيد: {u[3]:.2f} $\n• الحالة: {'محظور' if u[6] else 'نشط'}", reply_markup=u_markup)

        elif data.startswith("adm_addbal_") and str(user_id) == str(ADMIN_ID):
            target_uid = data.replace("adm_addbal_", "")
            user_states[str(user_id)] = {"action": "admin_input_add_amt", "target_uid": target_uid}
            bot.send_message(chat_id, f"➕ أرسل المبلغ المراد شحنه للمستخدم `{target_uid}` بالدولار:")

        elif data.startswith("adm_msg_") and str(user_id) == str(ADMIN_ID):
            target_uid = data.replace("adm_msg_", "")
            user_states[str(user_id)] = {"action": "send_direct_message", "target_uid": target_uid}
            bot.send_message(chat_id, f"✉️ **أرسل نص الرسالة الموجهة للمستخدم `{target_uid}`:**")

        elif data.startswith("adm_ban_") and str(user_id) == str(ADMIN_ID):
            target_uid = data.replace("adm_ban_", "")
            set_user_ban_status(target_uid, True)
            bot.send_message(chat_id, f"🚫 تم حظر المستخدم `{target_uid}`.")

        elif data.startswith("adm_unban_") and str(user_id) == str(ADMIN_ID):
            target_uid = data.replace("adm_unban_", "")
            set_user_ban_status(target_uid, False)
            bot.send_message(chat_id, f"🟢 تم فك حظر المستخدم `{target_uid}`.")

        elif data == "admin_prompt_broadcast" and str(user_id) == str(ADMIN_ID):
            user_states[str(user_id)] = {"action": "broadcast_all"}
            bot.send_message(chat_id, "📢 أرسل نص الرسالة المراد إذاعتها:")

        elif data == "admin_check_provider" and str(user_id) == str(ADMIN_ID):
            _, bal = fetch_hero_balance()
            bot.send_message(chat_id, f"💳 رصيد Hero SMS المزود: `{bal} $`")

    except Exception as e:
        print(f"Callback error: {e}")

# ----------------- تشغيل المحرك -----------------
def start_bot():
    try:
        bot.delete_webhook(drop_pending_updates=True)
        bot.set_my_commands([
            types.BotCommand("start", "🏠 القائمة الرئيسية"),
            types.BotCommand("buy", "☎️ شراء رقم افتراضي"),
            types.BotCommand("deposit", "🎳 شحن الرصيد"),
            types.BotCommand("transfer", "🔄 تحويل الرصيد مجاناً"),
            types.BotCommand("account", "🪪 حسابي والمحفظة"),
            types.BotCommand("admin", "👑 لوحة تحكم الإدارة")
        ])
    except Exception:
        pass

    print("🚀 Number SMS Ultra Bot is now active and listening...")
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=15, skip_pending=True)
        except Exception as e:
            print(f"Polling loop: {e}")
            time.sleep(2)

if __name__ == "__main__":
    start_bot()