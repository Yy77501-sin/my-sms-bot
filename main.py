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
        self.end_headers()
        self.wfile.write(b"Bot is Running Alive 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

web_thread = threading.Thread(target=run_web_server, daemon=True)
web_thread.start()

# 2. قراءة المفاتيح بأمان من بيئة Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
FIVESIM_API_KEY = os.getenv("FIVESIM_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

try:
    bot.remove_webhook()
except Exception:
    pass

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

# دالة شراء الرقم مع دعم المحاولة التلقائية على المشغلين المتاحين
def buy_number_from_5sim(country, service):
    try:
        # المحاولة أولاً باختيار أي مشغل متاح
        url = f'https://5sim.net/v1/user/buy/activation/{country}/any/{service}'
        res = requests.get(url, headers=HEADERS, timeout=15)
        
        if res.status_code == 200:
            return True, res.json()
        else:
            return False, res.text
    except Exception as e:
        return False, str(e)

# فحص كود التفعيل في الخلفية
def wait_for_sms(chat_id, order_id, phone_number):
    start_time = time.time()
    while time.time() - start_time < 600:  # 10 دقائق
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
        bot.send_message(chat_id, f"⌛ انتهت المهلة للرقم `{phone_number}` وتم إلغاء الطلب واسترجاع الرصيد.")
    except Exception as e:
        print(f"Cancel error: {e}")

# ----------------- أوامر البوت -----------------

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_apps = types.InlineKeyboardButton("📱 شراء رقم تفعيل", callback_data="menu_apps")
    btn_balance = types.InlineKeyboardButton("💳 رصيد حساب 5SIM", callback_data="check_balance")
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
            bot.answer_callback_query(call.id, "تعذر جلب الرصيد! تأكد من مفتاح الـ API في Render", show_alert=True)

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

    # 3. قائمة أكثر الدول توفراً ومضمونة في 5SIM
    elif call.data.startswith("srv_"):
        service_code = call.data.replace("srv_", "")
        bot.answer_callback_query(call.id)
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        # الدول الأكثر توفراً وضماناً في 5SIM
        markup.add(
            types.InlineKeyboardButton("🇮🇩 إندونيسيا (الأعلى توفراً)", callback_data=f"buy_{service_code}_indonesia"),
            types.InlineKeyboardButton("🇷🇺 روسيا", callback_data=f"buy_{service_code}_russia")
        )
        markup.add(
            types.InlineKeyboardButton("🇰🇿 كازاخستان", callback_data=f"buy_{service_code}_kazakhstan"),
            types.InlineKeyboardButton("🇻🇳 فيتنام", callback_data=f"buy_{service_code}_vietnam")
        )
        markup.add(
            types.InlineKeyboardButton("🇵🇭 الفلبين", callback_data=f"buy_{service_code}_philippines"),
            types.InlineKeyboardButton("🇰🇪 كينيا", callback_data=f"buy_{service_code}_kenya")
        )
        markup.add(
            types.InlineKeyboardButton("🇬🇧 بريطانيا", callback_data=f"buy_{service_code}_england"),
            types.InlineKeyboardButton("🇨🇴 كولومبيا", callback_data=f"buy_{service_code}_colombia")
        )
        markup.add(types.InlineKeyboardButton("🔙 تغيير التطبيق", callback_data="menu_apps"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"🌍 **اختر الدولة لخدمة ({service_code}):**\n_💡 ننصح باختيار إندونيسيا، روسيا، كازاخستان لسرعة توفر الأرقام_",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 4. تنفيذ حجز الرقم
    elif call.data.startswith("buy_"):
        parts = call.data.split("_")
        service_code = parts[1]
        country_code = parts[2]
        
        bot.answer_callback_query(call.id, "جاري استخراج الرقم...")
        msg = bot.send_message(chat_id, f"⏳ جاري حجز رقم لدولة ({country_code}) لتطبيق ({service_code})...")
        
        success, result = buy_number_from_5sim(country=country_code, service=service_code)
        if success:
            order_id = result.get('id')
            phone = result.get('phone')
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"✅ **تم حجز الرقم بنجاح!**\n\n"
                     f"📱 الرقم: `{phone}`\n"
                     f"🆔 رقم الطلب: `{order_id}`\n\n"
                     f"⏳ أدخل الرقم الآن في التطبيق، وسيقوم البوت بإرسال كود التفعيل هنا فور وصوله تلقائياً...",
                parse_mode="Markdown"
            )
            t = threading.Thread(target=wait_for_sms, args=(chat_id, order_id, phone))
            t.start()
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"❌ **تعذر حجز الرقم في ({country_code}):**\nالأرقام نفدت مؤقتاً في هذه الدولة.\n👉 **يرجى اختيار دولة أخرى (مثل إندونيسيا أو كازاخستان أو روسيا)**.",
                parse_mode="Markdown"
            )

    elif call.data == "back_main":
        bot.answer_callback_query(call.id)
        start_handler(call.message)
        
    elif call.data == "help":
        bot.answer_callback_query(call.id)
        bot.send_message(
            chat_id, 
            "📌 **تعليمات الاستخدام:**\n\n"
            "1. اختر التطبيق الذي تريد تفعيله.\n"
            "2. اختر الدولة (ننصح بإندونيسيا أو روسيا أو كازاخستان).\n"
            "3. انسخ الرقم واستخدمه في التطبيق.\n"
            "4. انتظر كود التحقق وسيصلك هنا في المحادثة مباشرة!"
        )

if __name__ == "__main__":
    print("🚀 البوت بدأ العمل بنجاح...")
    bot.infinity_polling(skip_pending=True)