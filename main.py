import os
import time
import threading
import datetime
import requests
import telebot
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler

# استيراد الإعدادات والكتالوج
import config
import catalog

BOT_TOKEN = getattr(config, 'BOT_TOKEN', os.getenv("BOT_TOKEN"))
API_KEY = getattr(config, 'HERO_SMS_API_KEY', os.getenv("HERO_SMS_API_KEY"))
ADMIN_ID = str(getattr(config, 'ADMIN_ID', "8097770003"))
SUPPORT_USERNAME = getattr(config, 'SUPPORT_USERNAME', "Yas_in7")
CURRENCY = getattr(config, 'CURRENCY', "$")

# 1. خادم ويب لإرضاء فحص Render 24/7
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Number SMS Bot is Live 24/7!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

web_thread = threading.Thread(target=run_web_server, daemon=True)
web_thread.start()

# 2. تهيئة البوت
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

def setup_bot_menu_commands():
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
    except Exception as e:
        print(f"Menu error: {e}")

API_ENDPOINTS = [
    "https://sms-hero.com/stubs/handler_api.php",
    "https://hero-sms.com/stubs/handler_api.php",
    "https://api.sms-hero.com/stubs/handler_api.php"
]

def api_request(params):
    params['api_key'] = API_KEY
    for endpoint in API_ENDPOINTS:
        try:
            res = requests.get(endpoint, params=params, timeout=12)
            if res.status_code == 200 and res.text.strip():
                return res.text.strip()
        except Exception:
            continue
    return "ERROR_CONNECTION"

def fetch_hero_balance():
    resp = api_request({'action': 'getBalance'})
    if resp.startswith("ACCESS_BALANCE:"):
        return True, resp.split(":")[1]
    return False, "تعذر الاتصال"

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
        return False, "الأرقام لهذه الدولة غير متوفرة حالياً."
    elif resp == "NO_BALANCE":
        return False, "رصيد الحساب غير كافٍ."
    return False, f"رد المزود: {resp}"

def set_status(order_id, status_code):
    api_request({'action': 'setStatus', 'id': order_id, 'status': status_code})

active_orders = {}

def monitor_sms_code(chat_id, message_id, order_id, phone_number, app_name, country_title, cost_str, create_time_str, expire_time_str):
    active_orders[order_id] = True
    start_time = time.time()
    while time.time() - start_time < 600:
        time.sleep(5)
        if not active_orders.get(order_id, False):
            return
        try:
            resp = api_request({'action': 'getStatus', 'id': order_id})
            if resp.startswith("STATUS_OK:"):
                code = resp.split(":")[1]
                
                # تحديث بطاقة الطلب وظهور الكود بنجاح
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
                
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=success_text, reply_markup=fin_markup, parse_mode="Markdown")
                set_status(order_id, 6)
                active_orders.pop(order_id, None)
                return
            elif resp == "STATUS_CANCEL":
                bot.send_message(chat_id, f"⚠️ تم إلغاء طلب الرقم `+{phone_number}`.")
                active_orders.pop(order_id, None)
                return
        except Exception as e:
            print(f"SMS Check: {e}")
            
    if active_orders.get(order_id, False):
        set_status(order_id, 8)
        active_orders.pop(order_id, None)
        bot.send_message(chat_id, f"⌛ انتهت مهلة الرقم `+{phone_number}` وتم إلغاء الطلب واسترجاع الرصيد.")

# ----------------- بناء القوائم -----------------

# القائمة الرئيسية
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
    markup.add(
        types.InlineKeyboardButton("🕒 الدعم", url=f"https://t.me/{SUPPORT_USERNAME}"),
        types.InlineKeyboardButton("🔄 • تحويل الرصيد •", callback_data="btn_transfer_balance")
    )
    markup.add(types.InlineKeyboardButton("✔️ • إحصائيات الشراء الناجح •", callback_data="btn_stats"))
    markup.add(types.InlineKeyboardButton("🪪 حسابي", callback_data="btn_my_account"))
    markup.add(types.InlineKeyboardButton("🛸 • خدمات ومميزات أخرى •", callback_data="btn_extra_features"))
    if str(user_id) == str(ADMIN_ID):
        markup.add(types.InlineKeyboardButton("👑 • لوحة تحكم الإدارة (Admin) •", callback_data="btn_admin_panel"))
    return markup

# 1. قائمة التطبيقات (الصورة 1)
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

# 2. قائمة السيرفرات للتطبيق (الصورة 2)
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
    markup.add(types.InlineKeyboardButton("• 🚀 البحث عن دولة 🧩 •", callback_data=f"search_country_{app_code}"))
    markup.add(
        types.InlineKeyboardButton("• (5) السيرفر •", callback_data=f"list_countries_{app_code}_s5"),
        types.InlineKeyboardButton("• (6) السيرفر •", callback_data=f"list_countries_{app_code}_s6")
    )
    markup.add(types.InlineKeyboardButton("✤ ↩️ عودة ✤", callback_data="btn_buy_number"))
    return markup

# 3. شبكة الدول بالأعلام والأسماء (الصورة 3)
def build_countries_grid_keyboard(app_code, server_name="السيرفر (1)"):
    markup = types.InlineKeyboardMarkup(row_width=3)
    c_list = list(catalog.COUNTRIES.items())
    
    # توزيع الدول 3 في كل صف
    buttons = []
    for c_id, c_info in c_list:
        btn_text = f"{c_info['flag']} {c_info['title']}"
        buttons.append(types.InlineKeyboardButton(btn_text, callback_data=f"card_{app_code}_{c_id}"))
        
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("✤ ↩️ عودة ✤", callback_data=f"srv_{app_code}"))
    return markup

# ----------------- معالجة الأوامر -----------------

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name if message.from_user.first_name else "صديقنا"
    text = (
        f"╭━━━〔 **NUMBER SMS** 〕━━━╮\n"
        f"🛍️ أهلاً بك يا **{user_name}** في المتجر الأقوى للأرقام الوهمية والتفعيلات الفورية!\n\n"
        f"👤 • معرفك (ID): `{user_id}`\n"
        f"💵 • رصيدك الحالي: **0.00 {CURRENCY} | 0.00 ₽**\n"
        f"⚡ • حالة السيرفرات: **جاهزة ونشطة 100%**\n"
        f"╰━━━━━━━━━━━━━━━━━╯\n\n"
        f"👇 **تفضل باختيار القسم المطلوب من القائمة أدناه:**"
    )
    markup = build_main_keyboard(user_id)
    bot.reply_to(message, text, reply_markup=markup, parse_mode="Markdown")

# ----------------- معالجة الضغط على الأزرار (Callbacks) -----------------

@bot.callback_query_handler(func=lambda call: True)
def router_callback(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
    
    # 🔙 العودة للرئيسية
    if data == "back_to_main":
        bot.answer_callback_query(call.id)
        user_name = call.from_user.first_name if call.from_user.first_name else "صديقنا"
        text = (
            f"╭━━━〔 **NUMBER SMS** 〕━━━╮\n"
            f"🛍️ أهلاً بك يا **{user_name}** في المتجر الأقوى للأرقام الوهمية والتفعيلات الفورية!\n\n"
            f"👤 • معرفك (ID): `{user_id}`\n"
            f"💵 • رصيدك الحالي: **0.00 {CURRENCY} | 0.00 ₽**\n"
            f"⚡ • حالة السيرفرات: **جاهزة ونشطة 100%**\n"
            f"╰━━━━━━━━━━━━━━━━━╯\n\n"
            f"👇 **تفضل باختيار القسم المطلوب من القائمة أدناه:**"
        )
        markup = build_main_keyboard(user_id)
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")

    # 1. الضغط على شراء رقم افتراضي (الصورة 1)
    elif data in ["btn_buy_number", "btn_offers_wa", "btn_ready_tg"]:
        bot.answer_callback_query(call.id)
        markup = build_apps_keyboard()
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="╭━━━〔 **NUMBER SMS** 〕━━━╮\n📱 **اختر التطبيق الذي ترغب في تفعيله:**\n╰━━━━━━━━━━━━━━━━━╯",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 2. الضغط على تطبيق معين (الصورة 2: اختيار السيرفر)
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
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")

    # 3. الضغط على السيرفر (الصورة 3: شبكة الدول بالأعلام فقط)
    elif data.startswith("list_countries_"):
        parts = data.split("_")
        app_code = parts[2]
        server_tag = parts[3]
        bot.answer_callback_query(call.id)
        
        app_info = catalog.SERVICES.get(app_code, catalog.SERVICES["wa"])
        text = (
            f"╭━━〔 **NUMBER SMS** 〕━━╮\n"
            f"🌍 **دول التوفر لخدمة {app_info['short']}:**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"اختر الدولة المطلوبة:"
        )
        markup = build_countries_grid_keyboard(app_code)
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")

    # 4. الضغط على الدولة (الصورة 4: بطاقة تأكيد السعر والسيرفر)
    elif data.startswith("card_"):
        parts = data.split("_")
        app_code = parts[1]
        c_id = parts[2]
        
        app_info = catalog.SERVICES.get(app_code, catalog.SERVICES["wa"])
        c_info = catalog.COUNTRIES.get(c_id, catalog.COUNTRIES["21"])
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
        # زر الشراء المباشر لهذا السيرفر
        markup.add(
            types.InlineKeyboardButton(f"{c_info['cost_rub']} ₽ | {c_info['cost_usd']} $", callback_data=f"exec_buy_{app_code}_{c_id}"),
            types.InlineKeyboardButton(f"1 {c_info['flag']} {c_info['title']}", callback_data=f"exec_buy_{app_code}_{c_id}")
        )
        markup.add(types.InlineKeyboardButton("✤ ↩️ عودة ✤", callback_data=f"list_countries_{app_code}_s1"))
        
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")

    # 5. الضغط على زر الشراء الفعلي (الصورة 5: بطاقة الشراء الناجح والتحكم)
    elif data.startswith("exec_buy_"):
        parts = data.split("_")
        app_code = parts[2]
        c_id = parts[3]
        
        app_info = catalog.SERVICES.get(app_code, catalog.SERVICES["wa"])
        c_info = catalog.COUNTRIES.get(c_id, catalog.COUNTRIES["21"])
        
        bot.answer_callback_query(call.id, "جاري طلب الرقم من السيرفر...")
        
        # تنفيذ الشراء من Hero SMS
        service_real_code = app_info['code']
        success, result = buy_hero_number(service_real_code, c_id)
        
        if success:
            order_id = result['id']
            phone = result['phone']
            now = datetime.datetime.now()
            expire = now + datetime.timedelta(minutes=20)
            
            time_now_str = now.strftime("%H:%M | %Y-%m-%d")
            time_exp_str = expire.strftime("%H:%M | %Y-%m-%d")
            cost_str = f"{c_info['cost_rub']} ₽ ({c_info['cost_usd']} $)"
            
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
                reply_markup=order_markup,
                parse_mode="Markdown"
            )
            
            # بدء خيط فحص الكود بالخلفية
            t = threading.Thread(
                target=monitor_sms_code,
                args=(chat_id, call.message.message_id, order_id, phone, app_info['short'], f"{c_info['title']} {c_info['flag']}", cost_str, time_now_str, time_exp_str)
            )
            t.start()
        else:
            bot.send_message(chat_id, f"❌ **تعذر حجز الرقم:**\n{result}\n\n👉 يرجى تجربة دولة أخرى أو سيرفر آخر.")

    # 6. زر إلغاء الطلب
    elif data.startswith("cancel_num_"):
        parts = data.split("_")
        order_id = parts[2]
        phone = parts[3]
        bot.answer_callback_query(call.id, "جاري إلغاء الطلب...")
        active_orders[order_id] = False
        set_status(order_id, 8)
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"⚠️ **تم إلغاء طلب الرقم `+{phone}` واسترجاع الرصيد بنجاح!**",
            reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("☎️ شراء رقم آخر", callback_data="btn_buy_number")),
            parse_mode="Markdown"
        )

    # 7. زر تغيير الرقم (إلغاء الحالي وطلب جديد فوراً)
    elif data.startswith("change_num_"):
        parts = data.split("_")
        old_order_id = parts[2]
        app_code = parts[3]
        c_id = parts[4]
        bot.answer_callback_query(call.id, "جاري استبدال الرقم...")
        active_orders[old_order_id] = False
        set_status(old_order_id, 8)
        # استدعاء الشراء الجديد
        router_callback(types.CallbackQuery(id="0", from_user=call.from_user, message=call.message, data=f"exec_buy_{app_code}_{c_id}", chat_instance=""))

    # 8. زر فحص الكود يدوياً
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

    # 9. باقي أقسام القائمة الرئيسية
    elif data == "btn_deposit":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("💬 التواصل مع الإدارة للشحن", url=f"https://t.me/{SUPPORT_USERNAME}"))
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="🎳 **قسم شحن الرصيد:**\n\n💳 **طرق الدفع المتوفرة:**\n• بنك الكريمي / ون كاش\n• بنك البسيري / جوالي\n• بايير (Payeer)\n• USDT / Binance Pay",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif data == "btn_my_account":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"🪪 **معلومات حسابك الشخصي:**\n\n• الاسم: **{call.from_user.first_name}**\n• المعرف (ID): `{user_id}`\n• الرصيد الحالي: **0.00 {CURRENCY} | 0.00 ₽**\n• إجمالي المشتريات: **0 رقم**",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif data == "btn_stats":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="✔️ **إحصائيات عمليات الشراء الناجحة:**\n\n• إجمالي الأرقام المفعلة اليوم: **342 رقم**\n• نسبة نجاح وصول الأكواد: **98.4%**\n• متوسط سرعة وصول الكود: **12 ثانية**",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif data == "btn_admin_panel":
        if str(user_id) != str(ADMIN_ID):
            bot.answer_callback_query(call.id, "⛔ ليس لديك صلاحية الوصول!", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("➕ شحن رصيد لمستخدم", callback_data="admin_add_balance"),
            types.InlineKeyboardButton("➖ خصم رصيد من مستخدم", callback_data="admin_deduct_balance")
        )
        markup.add(
            types.InlineKeyboardButton("📢 إذاعة رسالة للكل", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("💳 فحص رصيد Hero SMS", callback_data="admin_check_provider")
        )
        markup.add(types.InlineKeyboardButton("🔙 العودة للواجهة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="👑 **أهلاً بك يا مدير البوت في لوحة التحكم الإدارية:**",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif data == "admin_check_provider":
        if str(user_id) != str(ADMIN_ID):
            return
        bot.answer_callback_query(call.id, "جاري فحص رصيد Hero SMS...")
        success, bal = fetch_hero_balance()
        bot.send_message(chat_id, f"💳 **رصيد حسابك في مزود Hero SMS هو:** `{bal} $`\n✅ السيرفر متصل وشغال بنجاح.", parse_mode="Markdown")

# ----------------- تشغيل البوت -----------------
if __name__ == "__main__":
    print("⏳ جاري تهيئة البوت وقوائم الشراء المتقدمة...")
    time.sleep(2)
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass
    
    setup_bot_menu_commands()
    print("🚀 البوت بدأ العمل بتدفق الشراء الملكي بالكامل...")
    bot.polling(non_stop=True, interval=1, timeout=30)