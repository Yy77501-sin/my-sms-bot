import os
import time
import threading
import requests
import telebot
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler

# 1. خادم ويب للحفاظ على اتصال Render 24/7
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Bot is Running Alive 24/7!")

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

# 2. قراءة المفاتيح
BOT_TOKEN = os.getenv("BOT_TOKEN")
FIVESIM_API_KEY = os.getenv("FIVESIM_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

HEADERS = {
    'Authorization': f'Bearer {FIVESIM_API_KEY}',
    'Accept': 'application/json',
}

# جلب الرصيد
def get_5sim_balance():
    try:
        url = 'https://5sim.net/v1/user/profile'
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            return float(res.json().get('balance', 0))
    except Exception as e:
        print(f"Balance error: {e}")
    return None

# جلب أفضل وأسرع دولة متوفرة من 5SIM مباشرة عبر الـ Live Prices API
def get_live_available_products(service):
    candidates = []
    try:
        url = f'https://5sim.net/v1/guest/prices?product={service}'
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for country_code, services_dict in data.items():
                if service in services_dict:
                    prod = services_dict[service]
                    for operator_name, details in prod.items():
                        count = details.get('count', 0)
                        cost = details.get('cost', 0)
                        if count > 0:
                            candidates.append({
                                "country": country_code,
                                "operator": operator_name,
                                "count": count,
                                "cost": cost
                            })
            # ترتيب الخيارات حسب أكبر عدد أرقام شاغرة متوفرة
            candidates.sort(key=lambda x: x['count'], reverse=True)
    except Exception as e:
        print(f"Prices API error: {e}")
    return candidates

# دالة شراء الرقم المباشرة
def execute_buy(country, operator, service):
    try:
        url = f'https://5sim.net/v1/user/buy/activation/{country}/{operator}/{service}'
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            data = res.json()
            if "id" in data and "phone" in data:
                return True, data
            return False, data
        return False, res.text
    except Exception as e:
        return False, str(e)

# الشراء السريع بالاعتماد على المخزون الحي
def smart_fast_buy(service):
    candidates = get_live_available_products(service)
    if not candidates:
        # إذا تعذر جلب الأسعار، نجرب المشغل الافتراضي
        return execute_buy("russia", "any", service)
    
    last_err = ""
    # تجربة أول 4 خيارات تمتلك أعلى مخزون
    for item in candidates[:4]:
        success, result = execute_buy(item['country'], item['operator'], service)
        if success:
            result['bought_country'] = item['country']
            result['bought_operator'] = item['operator']
            return True, result
        else:
            last_err = str(result)
            
    return False, last_err

# فحص كود التفعيل في الخلفية
def wait_for_sms(chat_id, order_id, phone_number):
    start_time = time.time()
    while time.time() - start_time < 600:
        time.sleep(5)
        try:
            check_url = f'https://5sim.net/v1/user/check/{order_id}'
            res = requests.get(check_url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                data = res.json()
                sms_list = data.get('sms', [])
                if sms_list and len(sms_list) > 0:
                    code = sms_list[0].get('code')
                    full_sms = sms_list[0].get('text')
                    bot.send_message(
                        chat_id,
                        f"🎉 **وصل كود التفعيل بنجاح!**\n\n"
                        f"📱 الرقم: `{phone_number}`\n"
                        f"🔑 الكود: `{code}`\n"
                        f"📩 الرسالة: {full_sms}",
                        parse_mode="Markdown"
                    )
                    requests.get(f'https://5sim.net/v1/user/finish/{order_id}', headers=HEADERS)
                    return
                if data.get('status') in ['CANCELED', 'TIMEOUT']:
                    bot.send_message(chat_id, f"⚠️ تم إلغاء طلب الرقم `{phone_number}`.")
                    return
        except Exception as e:
            print(f"SMS Check error: {e}")
            
    try:
        requests.get(f'https://5sim.net/v1/user/cancel/{order_id}', headers=HEADERS)
        bot.send_message(chat_id, f"⌛ انتهت المهلة للرقم `{phone_number}` وتم إلغاء الطلب واسترجاع الرصيد.")
    except Exception as e:
        print(f"Cancel error: {e}")

# ----------------- أوامر البوت -----------------

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_apps = types.InlineKeyboardButton("📱 شراء رقم تفعيل", callback_data="menu_apps")
    btn_balance = types.InlineKeyboardButton("💳 رصيد 5SIM", callback_data="check_balance")
    btn_help = types.InlineKeyboardButton("ℹ️ مساعدة", callback_data="help")
    
    markup.add(btn_apps)
    markup.add(btn_balance, btn_help)
    
    bot.reply_to(
        message, 
        f"مرحباً بك يا {message.from_user.first_name} في متجر تفعيل الأرقام الذكي 🌟\nاختر الخدمة المطلوبة:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    # 1. الرصيد
    if call.data == "check_balance":
        balance = get_5sim_balance()
        if balance is not None:
            bot.answer_callback_query(call.id)
            text = (
                f"💰 **رصيد حسابك في 5SIM:**\n\n"
                f"💵 الرصيد المتاح: **{balance:.2f} $**\n"
                f"✅ جاهز لشراء الأرقام فوراً."
            )
            bot.send_message(chat_id, text, parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "تعذر جلب الرصيد!", show_alert=True)

    # 2. قائمة التطبيقات
    elif call.data == "menu_apps":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🟢 واتساب (WhatsApp)", callback_data="srv_wa"),
            types.InlineKeyboardButton("🔵 تيليجرام (Telegram)", callback_data="srv_tg")
        )
        markup.add(
            types.InlineKeyboardButton("🔴 جوجل / جيميل", callback_data="srv_go"),
            types.InlineKeyboardButton("🎵 تيك توك (TikTok)", callback_data="srv_lf")
        )
        markup.add(
            types.InlineKeyboardButton("🐦 إكس (تويتر)", callback_data="srv_tw"),
            types.InlineKeyboardButton("📘 فيسبوك (Facebook)", callback_data="srv_fb")
        )
        markup.add(types.InlineKeyboardButton("🔙 رجوع للرئيسية", callback_data="back_main"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="📱 **اختر التطبيق الذي تريد تفعيله:**",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 3. عرض خيارات الشراء للتطبيق المختار مع جلب الدول الحية المتوفرة
    elif call.data.startswith("srv_"):
        service_code = call.data.replace("srv_", "")
        bot.answer_callback_query(call.id, "جاري فحص المخزون الحي من 5SIM...")
        
        # استعلام الدول المتوفرة حالياً
        candidates = get_live_available_products(service_code)
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("⚡ حجز فوري بأعلى توفر (موصى به)", callback_data=f"fast_{service_code}"))
        
        # إضافة الدول المتاحة فعلياً ذات الأرقام الشاغرة
        added_countries = set()
        for item in candidates:
            c = item['country']
            if c not in added_countries and len(added_countries) < 6:
                added_countries.add(c)
                btn_title = f"{c.upper()} ({item['count']} رقم)"
                markup.add(types.InlineKeyboardButton(btn_title, callback_data=f"buy_{service_code}_{c}_{item['operator']}"))
                
        # إذا لم يكن هناك خيارات كافية نضع الخيارات الشائعة
        if len(added_countries) == 0:
            markup.add(
                types.InlineKeyboardButton("🇷🇺 روسيا", callback_data=f"buy_{service_code}_russia_any"),
                types.InlineKeyboardButton("🇮🇩 إندونيسيا", callback_data=f"buy_{service_code}_indonesia_any")
            )
            
        markup.add(types.InlineKeyboardButton("🔙 تغيير التطبيق", callback_data="menu_apps"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"🌍 **الدول التي تحتوي على أرقام شاغرة لتطبيق ({service_code}):**\n_اختر 'حجز فوري' أو اختر إحدى الدول المتوفرة:_ ",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 4. الشراء الفوري الذكي
    elif call.data.startswith("fast_"):
        service_code = call.data.replace("fast_", "")
        bot.answer_callback_query(call.id, "جاري سحب الرقم من أفضل مشغل...")
        msg = bot.send_message(chat_id, f"⏳ جاري فحص المخزون وسحب رقم شاغر لتطبيق ({service_code})...")
        
        success, result = smart_fast_buy(service_code)
        if success:
            order_id = result.get('id')
            phone = result.get('phone')
            country = result.get('bought_country', 'N/A')
            operator = result.get('bought_operator', 'N/A')
            
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"✅ **تم حجز الرقم بنجاح!**\n\n"
                     f"🌍 الدولة: `{country.upper()}` ({operator})\n"
                     f"📱 الرقم: `{phone}`\n"
                     f"🆔 رقم الطلب: `{order_id}`\n\n"
                     f"⏳ قم بإدخال الرقم في التطبيق الآن، وسيرسل البوت كود التفعيل هنا فور وصوله تلقائياً...",
                parse_mode="Markdown"
            )
            t = threading.Thread(target=wait_for_sms, args=(chat_id, order_id, phone))
            t.start()
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"❌ **تعذر حجز الرقم:**\nرد 5SIM: `{result}`",
                parse_mode="Markdown"
            )

    # 5. شراء دولة محددة
    elif call.data.startswith("buy_"):
        parts = call.data.split("_")
        service_code = parts[1]
        country_code = parts[2]
        operator = parts[3] if len(parts) > 3 else "any"
        
        bot.answer_callback_query(call.id, "جاري حجز الرقم...")
        msg = bot.send_message(chat_id, f"⏳ جاري حجز رقم لدولة ({country_code}) لتطبيق ({service_code})...")
        
        success, result = execute_buy(country=country_code, operator=operator, service=service_code)
        if success:
            order_id = result.get('id')
            phone = result.get('phone')
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"✅ **تم حجز الرقم بنجاح!**\n\n"
                     f"🌍 الدولة: `{country_code.upper()}` ({operator})\n"
                     f"📱 الرقم: `{phone}`\n"
                     f"🆔 رقم الطلب: `{order_id}`\n\n"
                     f"⏳ أدخل الرقم في التطبيق، وسيرسل البوت كود التحقق فور وصوله...",
                parse_mode="Markdown"
            )
            t = threading.Thread(target=wait_for_sms, args=(chat_id, order_id, phone))
            t.start()
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"❌ **تعذر الحجز:**\n`{result}`",
                parse_mode="Markdown"
            )

    elif call.data == "back_main":
        bot.answer_callback_query(call.id)
        start_handler(call.message)
        
    elif call.data == "help":
        bot.answer_callback_query(call.id)
        bot.send_message(
            chat_id, 
            "📌 **طريقة الاستخدام:**\n\n"
            "1. اختر التطبيق المطلوب.\n"
            "2. اضغط 'حجز فوري بأعلى توفر' ليقوم البوت باختيار الدولة الأكثر وفرة وسحب الرقم فوراً.\n"
            "3. انسخ الرقم وأدخله في التطبيق.\n"
            "4. انتظر كود التحقق في هذه المحادثة."
        )

# ----------------- التشغيل الآمن -----------------
if __name__ == "__main__":
    print("⏳ جاري تنظيف الجلسات السابقة...")
    time.sleep(2)
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        print(f"Webhook reset: {e}")
        
    print("🚀 البوت بدأ العمل بنجاح...")
    
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            print(f"⚠️ Polling Exception: {e}")
            time.sleep(4)