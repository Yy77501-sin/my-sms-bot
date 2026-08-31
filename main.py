import os
import time
import threading
import requests
import telebot
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler

# 1. خادم ويب لإرضاء فحص Render 24/7
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

# دالة شراء ذكية تجرب المشغلين الأكثر وفرة
def buy_number_smart(country, service):
    # قائمة المشغلين المتاحين لأشهر الدول
    country_operators = {
        "indonesia": ["any", "axis", "indosat", "three", "telkomsel", "smartfren"],
        "russia": ["any", "tele2", "beeline", "megafon", "mts", "rostelecom"],
        "kazakhstan": ["any", "tele2", "beeline", "altel", "kcell"],
        "vietnam": ["any", "viettel", "vinaphone", "mobifone", "vietnamobile"],
        "philippines": ["any", "globe", "smart", "dito"],
        "kenya": ["any", "safaricom", "airtel"],
        "england": ["any", "ee", "vodafone", "o2", "three"],
        "colombia": ["any", "claro", "tigo", "movistar"],
        "brazil": ["any", "claro", "vivo", "tim"]
    }
    
    operators = country_operators.get(country, ["any"])
    last_error = ""

    for op in operators:
        try:
            url = f'https://5sim.net/v1/user/buy/activation/{country}/{op}/{service}'
            res = requests.get(url, headers=HEADERS, timeout=12)
            if res.status_code == 200:
                data = res.json()
                if "id" in data and "phone" in data:
                    return True, data, op
            else:
                last_error = res.text
        except Exception as e:
            last_error = str(e)
            
    return False, last_error, None

# دالة سحب أسرع رقم متاح في أي دولة لهذه الخدمة
def buy_fastest_available(service):
    priority_countries = ["indonesia", "russia", "kazakhstan", "vietnam", "kenya", "philippines", "colombia", "brazil", "england"]
    
    for c in priority_countries:
        success, data, op = buy_number_smart(c, service)
        if success:
            return True, data, c, op
            
    return False, "لم نتمكن من العثور على أرقام شاغرة في الدول المقترحة حالياً.", None, None

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
                        f"📩 نص الرسالة: {full_sms}",
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
        bot.send_message(chat_id, f"⌛ انتهت المهلة للرقم `{phone_number}` وتم إلغاء الطلب تلقائياً.")
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

    # 3. قائمة الدول مع زر الشراء السريع
    elif call.data.startswith("srv_"):
        service_code = call.data.replace("srv_", "")
        bot.answer_callback_query(call.id)
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        # زر الشراء الفوري التلقائي
        markup.add(types.InlineKeyboardButton("⚡ أسرع رقم متوفر فوراً (تلقائي)", callback_data=f"fast_{service_code}"))
        
        markup.add(
            types.InlineKeyboardButton("🇮🇩 إندونيسيا", callback_data=f"buy_{service_code}_indonesia"),
            types.InlineKeyboardButton("🇷🇺 روسيا", callback_data=f"buy_{service_code}_russia")
        )
        markup.add(
            types.InlineKeyboardButton("🇰🇿 كازاخستان", callback_data=f"buy_{service_code}_kazakhstan"),
            types.InlineKeyboardButton("🇻🇳 فيتنام", callback_data=f"buy_{service_code}_vietnam")
        )
        markup.add(
            types.InlineKeyboardButton("🇰🇪 كينيا", callback_data=f"buy_{service_code}_kenya"),
            types.InlineKeyboardButton("🇵🇭 الفلبين", callback_data=f"buy_{service_code}_philippines")
        )
        markup.add(
            types.InlineKeyboardButton("🇬🇧 بريطانيا", callback_data=f"buy_{service_code}_england"),
            types.InlineKeyboardButton("🇨🇴 كولومبيا", callback_data=f"buy_{service_code}_colombia")
        )
        markup.add(types.InlineKeyboardButton("🔙 تغيير التطبيق", callback_data="menu_apps"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"🌍 **اختر الدولة لتطبيق ({service_code}):**\n_يمكنك اختيار 'أسرع رقم متوفر فوراً' ليقوم البوت بحجز رقم شاغر مباشرة!_",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 4. الشراء الفوري التلقائي
    elif call.data.startswith("fast_"):
        service_code = call.data.replace("fast_", "")
        bot.answer_callback_query(call.id, "جاري فحص أفضل دولة وحجز الرقم...")
        msg = bot.send_message(chat_id, f"🔍 جاري البحث عن أسرع رقم شاغر لتطبيق ({service_code})...")
        
        success, result, country, op = buy_fastest_available(service_code)
        if success:
            order_id = result.get('id')
            phone = result.get('phone')
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"✅ **تم حجز الرقم بنجاح!**\n\n"
                     f"🌍 الدولة: `{country}` ({op})\n"
                     f"📱 الرقم: `{phone}`\n"
                     f"🆔 رقم الطلب: `{order_id}`\n\n"
                     f"⏳ أدخل الرقم الآن في التطبيق، وسيرسل البوت كود التفعيل هنا فور وصوله تلقائياً...",
                parse_mode="Markdown"
            )
            t = threading.Thread(target=wait_for_sms, args=(chat_id, order_id, phone))
            t.start()
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"❌ تعذر الحجز التلقائي حالياً.\nالسبب: `{result}`",
                parse_mode="Markdown"
            )

    # 5. الشراء لدولة محددة
    elif call.data.startswith("buy_"):
        parts = call.data.split("_")
        service_code = parts[1]
        country_code = parts[2]
        
        bot.answer_callback_query(call.id, "جاري فحص المشغلين واستخراج الرقم...")
        msg = bot.send_message(chat_id, f"⏳ جاري فحص مشغلي دولة ({country_code}) لحجز رقم ({service_code})...")
        
        success, result, op = buy_number_smart(country=country_code, service=service_code)
        if success:
            order_id = result.get('id')
            phone = result.get('phone')
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"✅ **تم حجز الرقم بنجاح!**\n\n"
                     f"🌍 الدولة: `{country_code}` ({op})\n"
                     f"📱 الرقم: `{phone}`\n"
                     f"🆔 رقم الطلب: `{order_id}`\n\n"
                     f"⏳ أدخل الرقم في التطبيق الآن، وبمجرد وصول الرسالة ستظهر هنا فوراً...",
                parse_mode="Markdown"
            )
            t = threading.Thread(target=wait_for_sms, args=(chat_id, order_id, phone))
            t.start()
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"❌ **تعذر حجز الرقم في ({country_code}):**\nرد 5SIM: `{result}`\n\n👉 **جرب زر 'أسرع رقم متوفر فوراً' أو اختر دولة أخرى مثل روسيا أو كازاخستان.**",
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
            "2. اضغط 'أسرع رقم متوفر فوراً' لحجز أسرع رقم متاح.\n"
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