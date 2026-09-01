import os
import sys
import time
import sqlite3
import threading
import datetime
import requests
import telebot
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler

# استيراد الإعدادات
try:
    import config
    BOT_TOKEN = getattr(config, 'BOT_TOKEN', '8998307482:AAHlUFDu0E_0ltdVQVEGQ5z2pats24kK3rU').strip()
    API_KEY = getattr(config, 'HERO_SMS_API_KEY', '67ef5b751b1A4f2bef57dAd7bA2A248c').strip()
    ADMIN_ID = str(getattr(config, 'ADMIN_ID', '8097770003')).strip()
    SUPPORT_USERNAME = getattr(config, 'SUPPORT_USERNAME', 'Yas_in7').strip()
    CURRENCY = getattr(config, 'CURRENCY', '$').strip()
    
    # القنوات
    MAIN_CHANNEL_URL = getattr(config, 'MAIN_CHANNEL_URL', 'https://t.me/Yas_in7').strip()
    INSTRUCTIONS_CHANNEL_URL = getattr(config, 'INSTRUCTIONS_CHANNEL_URL', 'https://t.me/Yas_in7').strip()
    ACTIVATION_CHANNEL_ID = getattr(config, 'ACTIVATION_CHANNEL_ID', '').strip()
except Exception as e:
    print(f"Config Import Warning: {e}")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8998307482:AAHlUFDu0E_0ltdVQVEGQ5z2pats24kK3rU").strip()
    API_KEY = os.getenv("HERO_SMS_API_KEY", "67ef5b751b1A4f2bef57dAd7bA2A248c").strip()
    ADMIN_ID = str(os.getenv("ADMIN_ID", "8097770003")).strip()
    SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "Yas_in7").strip()
    CURRENCY = "$"
    MAIN_CHANNEL_URL = os.getenv("MAIN_CHANNEL_URL", "https://t.me/Yas_in7").strip()
    INSTRUCTIONS_CHANNEL_URL = os.getenv("INSTRUCTIONS_CHANNEL_URL", "https://t.me/Yas_in7").strip()
    ACTIVATION_CHANNEL_ID = os.getenv("ACTIVATION_CHANNEL_ID", "").strip()

import catalog

print(f"--- Starting Number SMS Bot Engine with Channels System ---")
print(f"Activation Channel Configured: {ACTIVATION_CHANNEL_ID or 'Not Set'}")

# 1. قاعدة بيانات SQLite
DB_PATH = "bot_database.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
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
        print("✅ Database initialized successfully.")
    except Exception as e:
        print(f"Init DB Error: {e}")

init_db()

def get_or_create_user(user_id, username="", first_name=""):
    try:
        uname = str(username) if username else ""
        fname = str(first_name) if first_name else "صديقنا"
        uid_str = str(user_id)
        
        conn = sqlite3.connect(DB_PATH)
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
            init_rub = 7000.0 if uid_str == str(ADMIN_ID) else 0.0
            cursor.execute(
                'INSERT INTO users (user_id, username, first_name, balance, rub_balance, orders_count, is_banned, joined_at) VALUES (?, ?, ?, ?, ?, 0, 0, ?)',
                (uid_str, uname, fname, init_bal, init_rub, now_str)
            )
            conn.commit()
            conn.close()
            return init_bal, init_rub, 0, 0, fname, uname
    except Exception as e:
        print(f"DB Get/Create Error: {e}")
        return 0.0, 0.0, 0, 0, "صديقنا", ""

def update_user_balance(user_id, amount_usd, amount_rub):
    try:
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_banned = ? WHERE user_id = ?', (1 if ban_status else 0, str(user_id)))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ban Error: {e}")

def get_all_users():
    try:
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username, first_name, balance, rub_balance, orders_count, is_banned, joined_at FROM users WHERE user_id = ? OR username = ?', (clean_q, clean_q))
        row = cursor.fetchone()
        conn.close()
        return row
    except Exception as e:
        print(f"Find User Error: {e}")
        return None

# 2. خادم ويب Render 24/7
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Number SMS Store Telegram Bot is Live 24/7!")

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

# 3. تهيئة البوت
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
user_states = {}

# ----------------- دالة إرسال التفعيل لقناة التفعيلات -----------------
def send_activation_log(user_id, country_title, service_name, phone, code, price_str, order_id):
    """
    إرسال إشعار تفعيل الرقم تلقائياً إلى قناة التفعيلات
    """
    try:
        channel_target = ACTIVATION_CHANNEL_ID or os.getenv("ACTIVATION_CHANNEL_ID", "").strip()
        if not channel_target:
            return  # لم يتم تحديد قناة التفعيلات بعد
            
        now_time = datetime.datetime.now().strftime("%H:%M | %Y-%m-%d")
        
        # إخفاء آخر 4 أرقام لحماية خصوصية الزبون
        masked_phone = phone
        if len(phone) > 6:
            masked_phone = phone[:-4] + "****"
            
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
        print(f"✅ Activation log sent to channel: {channel_target}")
    except Exception as e:
        print(f"⚠️ Failed to send log to activation channel: {e}")

# ----------------- واجهة API المزود -----------------
API_ENDPOINTS = [
    "https://sms-hero.com/stubs/handler_api.php",
    "https://hero-sms.com/stubs/handler_api.php",
    "https://api.sms-hero.com/stubs/handler_api.php"
]

def api_request(params):
    params['api_key'] = API_KEY
    for endpoint in API_ENDPOINTS:
        try:
            res = requests.get(endpoint, params=params, timeout=10)
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
    resp = api_request({
        'action': 'getNumber',
        'service': service_code,
        'country': country_id
    })
    if resp.startswith("ACCESS_NUMBER:"):
        parts = resp.split(":")
        return True, {"id": parts[1], "phone": parts[2]}
    elif resp == "NO_NUMBERS":
        return False, "الأرقام لهذه الدولة غير متوفرة حالياً في المخزون."
    elif resp == "NO_BALANCE":
        return False, "رصيد السيرفر غير كافٍ."
    return False, f"رد المزود: {resp}"

def set_status(order_id, status_code):
    api_request({'action': 'setStatus', 'id': order_id, 'status': status_code})

active_orders = {}

def monitor_sms_code(chat_id, message_id, order_id, phone_number, app_name, country_title, cost_str, time_now_str, time_exp_str, cost_usd, cost_rub, user_id):
    active_orders[order_id] = {
        "user_id": user_id,
        "start_time": time.time(),
        "cost_usd": cost_usd,
        "cost_rub": cost_rub,
        "phone": phone_number
    }
    
    max_duration = 1080  # 18 دقيقة حماية
    start_time = time.time()
    
    while time.time() - start_time < max_duration:
        time.sleep(5)
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
                
                # 🚀 إرسال التقرير التلقائي لقناة التفعيلات
                send_activation_log(user_id, country_title, app_name, phone_number, code, cost_str, order_id)
                return
            elif resp == "STATUS_CANCEL":
                bot.send_message(chat_id, f"⚠️ تم إلغاء طلب الرقم `+{phone_number}` واسترجاع الرصيد لمحفظتك.")
                update_user_balance(user_id, cost_usd, cost_rub)
                active_orders.pop(order_id, None)
                return
        except Exception as e:
            print(f"SMS Check Error: {e}")
            
    if order_id in active_orders:
        set_status(order_id, 8)
        update_user_balance(user_id, cost_usd, cost_rub)
        active_orders.pop(order_id, None)
        bot.send_message(
            chat_id,
            f"⌛ **انتهت مهلة الانتظار للرقم `+{phone_number}`.**\n"
            f"🛡️ تم إلغاء الطلب واسترجاع كامل المبلغ ({cost_str}) لمحفظتك تلقائياً."
        )

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
        types.InlineKeyboardButton("🎲 • الأكثر توفراً •", callback_data="btn_most_available")
    )
    markup.add(types.InlineKeyboardButton("🔭 • الرشق وشحن الألعاب والبرامج •", callback_data="btn_services_games"))
    markup.add(types.InlineKeyboardButton("💎 • اربح رصيد مجاناً •", callback_data="btn_free_points"))
    
    # أزرار القنوات الثلاث والدعم
    markup.add(
        types.InlineKeyboardButton("📢 قناة البوت الرسمية", url=MAIN_CHANNEL_URL),
        types.InlineKeyboardButton("📚 التعليمات والشرح", url=INSTRUCTIONS_CHANNEL_URL)
    )
    markup.add(
        types.InlineKeyboardButton("🕒 الدعم الفني", url=f"https://t.me/{SUPPORT_USERNAME}"),
        types.InlineKeyboardButton("🔄 • تحويل الرصيد •", callback_data="btn_transfer_balance")
    )
    markup.add(types.InlineKeyboardButton("✔️ • إحصائيات الشراء الناجح •", callback_data="btn_stats"))
    markup.add(types.InlineKeyboardButton("🪪 حسابي والمحفظة", callback_data="btn_my_account"))
    markup.add(types.InlineKeyboardButton("🛸 • خدمات ومميزات أخرى •", callback_data="btn_extra_features"))
    if str(user_id) == str(ADMIN_ID):
        markup.add(types.InlineKeyboardButton("👑 • لوحة تحكم الإدارة (Admin) •", callback_data="btn_admin_panel"))
    return markup

def build_apps_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🛍️ WHATSAPP - واتس اب", callback_data="srv_wa"))
    markup.add(types.InlineKeyboardButton("🎲 TELEGRAM - تليجرام", callback_data="srv_tg"))
    markup.add(types.InlineKeyboardButton("🎳 LNSTAGRAM - انستغرام", callback_data="srv_ig"))
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
    markup.add(
        types.InlineKeyboardButton("💙 2WhatsApp عروض", callback_data="srv_wa"),
        types.InlineKeyboardButton("💙 1WhatsApp عروض", callback_data="srv_wa")
    )
    markup.add(types.InlineKeyboardButton("💚 Telegram عروض 💚", callback_data="srv_tg"))
    markup.add(types.InlineKeyboardButton("✤ ↩️ عودة ✤", callback_data="back_to_main"))
    return markup

def build_servers_keyboard(app_code):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🎲 • الأكثر توفراً •", callback_data=f"list_countries_{app_code}_most"))
    markup.add(
        types.InlineKeyboardButton("• (1) السيرفر •", callback_data=f"list_countries_{app_code}_s1"),
        types.InlineKeyboardButton("• (2) السيرفر •", callback_data=f"list_countries_{app_code}_s2")
    )
    markup.add(
        types.InlineKeyboardButton("• (3) السيرفر •", callback_data=f"list_countries_{app_code}_s3"),
        types.InlineKeyboardButton("• (4) السيرفر •", callback_data=f"list_countries_{app_code}_s4")
    )
    markup.add(types.InlineKeyboardButton("• 🚀 البحث عن دولة 🧩 •", callback_data=f"prompt_search_country_{app_code}"))
    markup.add(
        types.InlineKeyboardButton("• (5) السيرفر •", callback_data=f"list_countries_{app_code}_s5"),
        types.InlineKeyboardButton("• (6) السيرفر •", callback_data=f"list_countries_{app_code}_s6")
    )
    markup.add(types.InlineKeyboardButton("✤ ↩️ عودة ✤", callback_data="btn_buy_number"))
    return markup

def build_countries_grid_keyboard(app_code):
    markup = types.InlineKeyboardMarkup(row_width=3)
    c_list = list(catalog.COUNTRIES.items())
    buttons = []
    for c_id, c_info in c_list:
        btn_text = f"{c_info['flag']} {c_info['title']}"
        buttons.append(types.InlineKeyboardButton(btn_text, callback_data=f"card_{app_code}_{c_id}"))
        
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("✤ ↩️ عودة ✤", callback_data=f"srv_{app_code}"))
    return markup

def build_admin_main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("👥 قائمة المستخدمين", callback_data="admin_view_users"),
        types.InlineKeyboardButton("🔍 بحث والتحكم بمستخدم", callback_data="admin_search_user")
    )
    markup.add(
        types.InlineKeyboardButton("➕ شحن رصيد", callback_data="admin_prompt_add_bal"),
        types.InlineKeyboardButton("➖ خصم رصيد", callback_data="admin_prompt_sub_bal")
    )
    markup.add(
        types.InlineKeyboardButton("🚫 طرد / حظر مستخدم", callback_data="admin_prompt_ban"),
        types.InlineKeyboardButton("📢 إذاعة عامة للكل", callback_data="admin_prompt_broadcast")
    )
    markup.add(
        types.InlineKeyboardButton("💳 فحص رصيد Hero SMS", callback_data="admin_check_provider")
    )
    markup.add(types.InlineKeyboardButton("🔙 العودة للواجهة الرئيسية", callback_data="back_to_main"))
    return markup

# ----------------- معالجة أمر البداية (Start) -----------------

@bot.message_handler(commands=['start'])
def start_command(message):
    print(f"📩 Received /start from {message.from_user.id} ({message.from_user.first_name})")
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

# ----------------- معالجة النصوص وحالات البحث -----------------

@bot.message_handler(func=lambda msg: not msg.text.startswith('/'))
def handle_all_text_messages(message):
    try:
        user_id_str = str(message.from_user.id)
        text = message.text.strip()
        state = user_states.pop(user_id_str, None)
        
        if not state:
            return

        action = state.get("action")
        
        if action == "search_country_for_app":
            app_code = state.get("app_code", "wa")
            search_query = text.lower()
            
            matched_countries = []
            for c_id, c_info in catalog.COUNTRIES.items():
                if (search_query in c_info["name"].lower() or 
                    search_query in c_info["title"].lower() or 
                    search_query in c_info["prefix"] or 
                    search_query == c_id):
                    matched_countries.append((c_id, c_info))
                    
            if not matched_countries:
                msg_text = f"🔍 **لم يتم العثور على دولة مطابقة لـ:** `{text}`\n\n👉 جرب اسم آخر (مثل: مصر، روسيا، إندونيسيا)."
                markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 عودة لقائمة السيرفرات", callback_data=f"srv_{app_code}")
                )
                bot.reply_to(message, msg_text, reply_markup=markup)
                return
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            for c_id, c_info in matched_countries:
                btn_text = f"{c_info['flag']} {c_info['title']}"
                markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"card_{app_code}_{c_id}"))
            markup.add(types.InlineKeyboardButton("🔙 عودة لقائمة السيرفرات", callback_data=f"srv_{app_code}"))
            
            bot.reply_to(message, f"🎯 **نتائج البحث عن ({text}):**\nاختر الدولة للمتابعة:", reply_markup=markup)

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

        elif action == "add_balance_amount" and user_id_str == str(ADMIN_ID):
            target_uid = state.get("target_uid")
            try:
                amount = float(text)
                amount_rub = amount * 90.0
                update_user_balance(target_uid, amount, amount_rub)
                bot.reply_to(message, f"✅ **تم شحن {amount:.2f} $ بنجاح للمستخدم `{target_uid}`.**")
                try:
                    bot.send_message(target_uid, f"🎉 **تم إيداع رصيد جديد في محفظتك!**\n\n💵 المبلغ: **{amount:.2f} $**\n✅ استمتع بتفعيل أرقامك الآن.")
                except Exception:
                    pass
            except Exception:
                bot.reply_to(message, "❌ يرجى كتابة أرقام فقط (مثال: 5.0).")

        elif action == "sub_balance_amount" and user_id_str == str(ADMIN_ID):
            target_uid = state.get("target_uid")
            try:
                amount = float(text)
                amount_rub = amount * 90.0
                update_user_balance(target_uid, -amount, -amount_rub)
                bot.reply_to(message, f"✅ **تم خصم {amount:.2f} $ بنجاح من حساب المستخدم `{target_uid}`.**")
                try:
                    bot.send_message(target_uid, f"⚠️ **تنبيه:** تم خصم **{amount:.2f} $** من رصيد محفظتك بواسطة الإدارة.")
                except Exception:
                    pass
            except Exception:
                bot.reply_to(message, "❌ القيمة المدخلة غير صحيحة.")

        elif action == "send_direct_message" and user_id_str == str(ADMIN_ID):
            target_uid = state.get("target_uid")
            try:
                bot.send_message(target_uid, f"📩 **رسالة خاصة من إدارة البوت:**\n\n{text}")
                bot.reply_to(message, f"✅ **تم إرسال الرسالة بنجاح للمستخدم `{target_uid}`.**")
            except Exception as e:
                bot.reply_to(message, f"❌ فشل إرسال الرسالة للمستخدم: {e}")

        elif action == "broadcast_all" and user_id_str == str(ADMIN_ID):
            users = get_all_users()
            sent_count = 0
            bot.reply_to(message, f"⏳ جاري بدء الإذاعة لـ {len(users)} مستخدم...")
            for u in users:
                uid = u[0]
                try:
                    bot.send_message(uid, f"📢 **إشعار هام من إدارة البوت:**\n\n{text}")
                    sent_count += 1
                    time.sleep(0.05)
                except Exception:
                    continue
            bot.send_message(user_id_str, f"✅ **اكتملت الإذاعة بنجاح!**\nتم التوصيل إلى **{sent_count}** مستخدم.")

    except Exception as e:
        print(f"Handle Text Error: {e}")

# ----------------- معالجة الضغط على الأزرار -----------------

@bot.callback_query_handler(func=lambda call: True)
def router_callback(call):
    try:
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        data = call.data
        bal_usd, bal_rub, orders, is_banned, fn, un = get_or_create_user(user_id, call.from_user.username, call.from_user.first_name)
        
        if is_banned and str(user_id) != str(ADMIN_ID):
            bot.answer_callback_query(call.id, "⛔ حسابك محظور من استخدام البوت!", show_alert=True)
            return

        if data == "back_to_main":
            bot.answer_callback_query(call.id)
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

        elif data.startswith("prompt_search_country_"):
            app_code = data.replace("prompt_search_country_", "")
            bot.answer_callback_query(call.id)
            user_states[str(user_id)] = {"action": "search_country_for_app", "app_code": app_code}
            bot.send_message(chat_id, "🔍 **أرسل الآن اسم الدولة أو رمز مفتاحها (مثال: مصر، كازاخستان، 966، أو 20):**")

        elif data == "btn_admin_panel":
            if str(user_id) != str(ADMIN_ID):
                bot.answer_callback_query(call.id, "⛔ ليس لديك صلاحية!", show_alert=True)
                return
            bot.answer_callback_query(call.id)
            markup = build_admin_main_keyboard()
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text="👑 **لوحة تحكم إدارة المتجر والمستخدمين:**\n\nتحكم كامل في الرصيد، الحظر، الإذاعة، وفحص السيرفرات:",
                reply_markup=markup
            )

        elif data == "admin_view_users":
            if str(user_id) != str(ADMIN_ID):
                return
            bot.answer_callback_query(call.id)
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
            bot.answer_callback_query(call.id)
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
            bot.answer_callback_query(call.id)
            user_states[str(user_id)] = {"action": "admin_search_user"}
            bot.send_message(chat_id, "🔍 **أرسل الآن معرف المستخدم (User ID) أو اليوزرنيم للبحث عنه:**")

        elif data.startswith("adm_addbal_"):
            if str(user_id) != str(ADMIN_ID):
                return
            target_uid = data.replace("adm_addbal_", "")
            bot.answer_callback_query(call.id)
            user_states[str(user_id)] = {"action": "add_balance_amount", "target_uid": target_uid}
            bot.send_message(chat_id, f"➕ **أرسل المبلغ المراد شحنه للمستخدم `{target_uid}` بالدولار (مثال: 5):**")

        elif data.startswith("adm_subbal_"):
            if str(user_id) != str(ADMIN_ID):
                return
            target_uid = data.replace("adm_subbal_", "")
            bot.answer_callback_query(call.id)
            user_states[str(user_id)] = {"action": "sub_balance_amount", "target_uid": target_uid}
            bot.send_message(chat_id, f"➖ **أرسل المبلغ المراد خصمه من المستخدم `{target_uid}` بالدولار (مثال: 2):**")

        elif data.startswith("adm_ban_"):
            if str(user_id) != str(ADMIN_ID):
                return
            target_uid = data.replace("adm_ban_", "")
            set_user_ban_status(target_uid, True)
            bot.answer_callback_query(call.id, "🚫 تم حظر وطرد المستخدم بنجاح!", show_alert=True)
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
            bot.answer_callback_query(call.id, "🟢 تم فك الحظر عن المستخدم بنجاح!", show_alert=True)
            try:
                bot.send_message(target_uid, "🎉 **تم فك الحظر عن حسابك! يمكنك الآن استخدام البوت بشكل طبيعي.**")
            except Exception:
                pass
            router_callback(types.CallbackQuery(id="0", from_user=call.from_user, message=call.message, data=f"adm_userinfo_{target_uid}", chat_instance=""))

        elif data.startswith("adm_msg_"):
            if str(user_id) != str(ADMIN_ID):
                return
            target_uid = data.replace("adm_msg_", "")
            bot.answer_callback_query(call.id)
            user_states[str(user_id)] = {"action": "send_direct_message", "target_uid": target_uid}
            bot.send_message(chat_id, f"✉️ **أرسل نص الرسالة التي تريد إرسالها للمستخدم `{target_uid}`:**")

        elif data == "admin_prompt_broadcast":
            if str(user_id) != str(ADMIN_ID):
                return
            bot.answer_callback_query(call.id)
            user_states[str(user_id)] = {"action": "broadcast_all"}
            bot.send_message(chat_id, "📢 **أرسل الآن نص الرسالة أو الإعلان المراد إذاعته لجميع المستخدمين:**")

        elif data == "admin_prompt_add_bal":
            if str(user_id) != str(ADMIN_ID):
                return
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "💡 **للشحن السريع استخدم الأمر:**\n`/add <User_ID> <المبلغ>`\nمثال: `/add 8097770003 5`")

        elif data == "admin_prompt_sub_bal":
            if str(user_id) != str(ADMIN_ID):
                return
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "💡 **للخصم السريع استخدم الأمر:**\n`/sub <User_ID> <المبلغ>`\nمثال: `/sub 8097770003 2`")

        elif data == "admin_check_provider":
            if str(user_id) != str(ADMIN_ID):
                return
            bot.answer_callback_query(call.id, "جاري فحص رصيد المزود...")
            success, bal = fetch_hero_balance()
            bot.send_message(chat_id, f"💳 **رصيد حسابك في مزود الخدمة هو:** `{bal} $`\n✅ السيرفر متصل وشغال.")

        # باقي أقسام الشراء
        elif data in ["btn_buy_number", "btn_offers_wa", "btn_ready_tg"]:
            bot.answer_callback_query(call.id)
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
            bot.answer_callback_query(call.id)
            
            text = (
                f"• **مرحباً : نظام**\n\n"
                f"➖ **التطبيق : {app_info['name']}**\n"
                f"➖ **الدول موزعة على السيرفرات أدناه**\n"
                f"➖ **قناة التفعيلات 💗**\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            markup = build_servers_keyboard(app_code)
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

        elif data.startswith("list_countries_"):
            parts = data.split("_")
            app_code = parts[2]
            bot.answer_callback_query(call.id)
            
            app_info = catalog.SERVICES.get(app_code, catalog.SERVICES["wa"])
            text = (
                f"╭━━〔 **NUMBER SMS** 〕━━╮\n"
                f"🌍 **دول التوفر لخدمة {app_info['short']}:**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"اختر الدولة المطلوبة:"
            )
            markup = build_countries_grid_keyboard(app_code)
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

        elif data.startswith("card_"):
            parts = data.split("_")
            app_code = parts[1]
            c_id = parts[2]
            
            app_info = catalog.SERVICES.get(app_code, catalog.SERVICES["wa"])
            c_info = catalog.COUNTRIES.get(c_id, catalog.COUNTRIES.get("21", {}))
            if not c_info:
                bot.answer_callback_query(call.id, "الدولة غير متوفرة", show_alert=True)
                return
            bot.answer_callback_query(call.id)
            
            text = (
                f"➕ **شراء رقم جديد ✅**\n\n"
                f"➖ **💻 التطبيق | {app_info['short']}**\n"
                f"➖ **🌍 الدولة | {c_info['title']} {c_info['flag']}**\n"
                f"➖ **🔢 مفتاح الدولة | {c_info['prefix']} 💚**\n"
                f"➖ **✔️ اضغط على أحد السيرفرات لشراء رقم ✔️**\n"
                f"➖ **✔️ يختلف التوفر والجودة من سيرفر لآخر ✔️**\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("🎲 السعر ₽", callback_data="noop"),
                types.InlineKeyboardButton("🧩 السيرفرات", callback_data="noop")
            )
            markup.add(
                types.InlineKeyboardButton(f"{c_info['cost_rub']} ₽ | {c_info['cost_usd']:.3f} $", callback_data=f"exec_buy_{app_code}_{c_id}"),
                types.InlineKeyboardButton(f"1 {c_info['flag']} {c_info['title']}", callback_data=f"exec_buy_{app_code}_{c_id}")
            )
            markup.add(types.InlineKeyboardButton("✤ ↩️ عودة ✤", callback_data=f"list_countries_{app_code}_s1"))
            
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

        elif data.startswith("exec_buy_"):
            parts = data.split("_")
            app_code = parts[2]
            c_id = parts[3]
            
            app_info = catalog.SERVICES.get(app_code, catalog.SERVICES["wa"])
            c_info = catalog.COUNTRIES.get(c_id, catalog.COUNTRIES.get("21", {}))
            if not c_info:
                bot.answer_callback_query(call.id, "الدولة غير متوفرة", show_alert=True)
                return
            
            if bal_usd < c_info['cost_usd'] and bal_rub < c_info['cost_rub'] and str(user_id) != str(ADMIN_ID):
                bot.answer_callback_query(call.id, "❌ رصيدك غير كافٍ!", show_alert=True)
                msg_text = (
                    f"❌ **عذراً، رصيد محفظتك غير كافٍ!**\n\n"
                    f"• سعر الرقم: **{c_info['cost_rub']} ₽ ({c_info['cost_usd']:.3f} $)**\n"
                    f"• رصيدك الحالي: **{bal_usd:.2f} $**\n\n"
                    f"👉 يرجى شحن رصيدك عبر قسم **🎳 شحن الرصيد**."
                )
                bot.send_message(chat_id, msg_text, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎳 شحن الرصيد", callback_data="btn_deposit")))
                return

            bot.answer_callback_query(call.id, "جاري طلب الرقم من السيرفر...")
            
            service_real_code = app_info['code']
            success, result = buy_hero_number(service_real_code, c_id)
            
            if success:
                update_user_balance(user_id, -c_info['cost_usd'], -c_info['cost_rub'])
                
                order_id = result['id']
                phone = result['phone']
                now = datetime.datetime.now()
                expire = now + datetime.timedelta(minutes=18)
                
                time_now_str = now.strftime("%H:%M | %Y-%m-%d")
                time_exp_str = expire.strftime("%H:%M | %Y-%m-%d")
                cost_str = f"{c_info['cost_rub']} ₽ ({c_info['cost_usd']:.3f} $)"
                
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
                order_markup.add(types.InlineKeyboardButton("✤ 🔄 تغيير الرقم ✤", callback_data=f"change_num_{order_id}_{app_code}_{c_id}"))
                order_markup.add(types.InlineKeyboardButton("✤ 📩 طلب الكود ✤", callback_data=f"check_code_{order_id}"))
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
                    args=(chat_id, call.message.message_id, order_id, phone, app_info['short'], f"{c_info['title']} {c_info['flag']}", cost_str, time_now_str, time_exp_str, c_info['cost_usd'], c_info['cost_rub'], user_id)
                )
                t.start()
            else:
                bot.send_message(chat_id, f"❌ **تعذر حجز الرقم من المزود:**\n{result}\n\n👉 يرجى تجربة دولة أخرى أو سيرفر آخر.")

        elif data.startswith("cancel_num_"):
            parts = data.split("_")
            order_id = parts[2]
            phone = parts[3]
            
            order_info = active_orders.get(order_id)
            if order_info:
                elapsed = time.time() - order_info["start_time"]
                if elapsed < 60:
                    remaining = int(60 - elapsed)
                    bot.answer_callback_query(
                        call.id,
                        f"⏳ سياسة السيرفر تشترط الانتظار {remaining} ثانية لتفعيل زر الإلغاء!",
                        show_alert=True
                    )
                    return
                
                bot.answer_callback_query(call.id, "جاري إلغاء الطلب واسترجاع الرصيد...")
                set_status(order_id, 8)
                update_user_balance(user_id, order_info["cost_usd"], order_info["cost_rub"])
                active_orders.pop(order_id, None)
                
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    text=f"⚠️ **تم إلغاء طلب الرقم `+{phone}` بنجاح!**\n\n✅ تم استرجاع كامل المبلغ إلى رصيد محفظتك.",
                    reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("☎️ شراء رقم آخر", callback_data="btn_buy_number"))
                )
            else:
                set_status(order_id, 8)
                bot.answer_callback_query(call.id, "تم الإلغاء.")

        elif data.startswith("change_num_"):
            parts = data.split("_")
            old_order_id = parts[2]
            app_code = parts[3]
            c_id = parts[4]
            
            order_info = active_orders.get(old_order_id)
            if order_info:
                elapsed = time.time() - order_info["start_time"]
                if elapsed < 60:
                    remaining = int(60 - elapsed)
                    bot.answer_callback_query(call.id, f"⏳ يرجى الانتظار {remaining} ثانية لاستبدال الرقم.", show_alert=True)
                    return
                set_status(old_order_id, 8)
                update_user_balance(user_id, order_info["cost_usd"], order_info["cost_rub"])
                active_orders.pop(old_order_id, None)
                
            router_callback(types.CallbackQuery(id="0", from_user=call.from_user, message=call.message, data=f"exec_buy_{app_code}_{c_id}", chat_instance=""))

        elif data.startswith("check_code_"):
            order_id = data.replace("check_code_", "")
            resp = api_request({'action': 'getStatus', 'id': order_id})
            if resp.startswith("STATUS_OK:"):
                code = resp.split(":")[1]
                bot.answer_callback_query(call.id, f"🎉 الكود: {code}", show_alert=True)
            elif resp == "STATUS_WAIT_CODE":
                bot.answer_callback_query(call.id, "⏳ الكود قيد الانتظار، لم يصل بعد...", show_alert=False)
            else:
                bot.answer_callback_query(call.id, f"الحالة: {resp}", show_alert=True)

        elif data == "btn_deposit":
            bot.answer_callback_query(call.id)
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("💬 إرسال إشعار التحويل للإدارة", url=f"https://t.me/{SUPPORT_USERNAME}"))
            markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
            
            deposit_text = (
                f"🎳 **قسم شحن الرصيد المباشر:**\n\n"
                f"💳 **حسابات الدفع المتاحة:**\n"
                f"• 🏦 **بنك الكريمي (ريال يمني / دولار):** `123456789`\n"
                f"• 🏦 **بنك البسيري / جوالي:** `777777777`\n"
                f"• 🅿️ **بايير (Payeer):** `P12345678`\n"
                f"• 🪙 **بينانس (USDT Pay ID):** `{ADMIN_ID}`\n\n"
                f"📸 بعد التحويل، أرسل صورة الإشعار مع معرف حسابك (`{user_id}`) وسيتم شحن رصيدك فوراً."
            )
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=deposit_text, reply_markup=markup)

        elif data == "btn_my_account":
            bot.answer_callback_query(call.id)
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("🎳 شحن الرصيد", callback_data="btn_deposit"))
            markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=f"🪪 **معلومات حسابك الشخصي:**\n\n• الاسم: **{call.from_user.first_name}**\n• المعرف (ID): `{user_id}`\n• الرصيد بالدولار: **{bal_usd:.2f} $**\n• الرصيد بالروبل: **{bal_rub:.1f} ₽**\n• المشتريات: **{orders} رقم**",
                reply_markup=markup
            )

    except Exception as e:
        print(f"Callback error: {e}")

# ----------------- تشغيل البوت في الخيط الرئيسي -----------------
def start_bot():
    print("🧹 Cleaning old Telegram Webhooks...")
    try:
        bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook cleaned successfully.")
    except Exception as e:
        print(f"Webhook reset warning: {e}")

    try:
        commands = [
            types.BotCommand("start", "🏠 القائمة الرئيسية"),
            types.BotCommand("buy", "☎️ شراء رقم افتراضي"),
            types.BotCommand("deposit", "🎳 شحن الرصيد"),
            types.BotCommand("account", "🪪 حسابي والمحفظة"),
            types.BotCommand("support", "💬 الدعم الفني والمساعدة"),
            types.BotCommand("admin", "👑 لوحة تحكم الإدارة")
        ]
        bot.set_my_commands(commands)
    except Exception:
        pass

    print("🚀 BOT IS NOW RUNNING & READY WITH 3 CHANNELS SUPPORT 24/7...")
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=15, skip_pending=True)
        except Exception as e:
            print(f"Polling loop crash: {e}")
            time.sleep(3)

if __name__ == "__main__":
    start_bot()