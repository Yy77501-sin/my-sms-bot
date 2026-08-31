import os
import time
import threading
import requests
import telebot
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler

# 1. إعداد سيرفر وهمي لإرضاء فحص Render Web Service
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running Alive 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"🌍 Web server listening on port {port}")
    server.serve_forever()

# تشغيل سيرفر الويب في خيط منفصل (Thread)
web_thread = threading.Thread(target=run_web_server, daemon=True)
web_thread.start()

# 2. إعدادات البوت والـ API
BOT_TOKEN = os.getenv(8998307482:AAHlUFDu0E_0ltdVQVEGQ5z2pats24kK3rU)
FIVESIM_API_KEY = os.getenv("FIVESIM_API_KEY", )

bot = telebot.TeleBot(BOT_TOKEN)

HEADERS = {
    'Authorization': f'Bearer {FIVESIM_API_KEY}',
    'Accept': 'application/json',
}

def get_5sim_balance():
    try:
        url = 'https://5sim.net/v1/user/profile'
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json().get('balance', 0)
    except Exception as e:
        print(f"Error fetching balance: {e}")
    return None

def buy_5sim_number(country="indonesia", service="wa"):
    try:
        url = f'https://5sim.net/v1/user/buy/activation/{country}/any/{service}'
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

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
            print(f"Error checking SMS: {e}")
            
    try:
        requests.get(f'https://5sim.net/v1/user/cancel/{order_id}', headers=HEADERS)
        bot.send_message(chat_id, f"⌛ انتهت المهلة للرقم `{phone_number}` وتم إلغاء الطلب.")
    except Exception as e:
        print(f"Cancel error: {e}")

# 3. أوامر التيليجرام
@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_buy = types.InlineKeyboardButton("📱 شراء رقم (واتساب)", callback_data="buy_wa")
    btn_balance = types.InlineKeyboardButton("💳 رصيد 5SIM", callback_data="check_balance")
    btn_help = types.InlineKeyboardButton("ℹ️ مساعدة", callback_data="help")
    
    markup.add(btn_buy)
    markup.add(btn_balance, btn_help)
    
    bot.reply_to(
        message, 
        f"مرحباً بك يا {message.from_user.first_name} في بوت تفعيل الأرقام 🌟\nاختر من الأزرار أدناه:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    if call.data == "check_balance":
        balance = get_5sim_balance()
        if balance is not None:
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, f"💰 رصيد 5SIM الحالي: **{balance} ₽** (روبل)", parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "تعذر جلب الرصيد! تحقق من FIVESIM_API_KEY", show_alert=True)
            
    elif call.data == "buy_wa":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(chat_id, "⏳ جاري استخراج رقم واتساب من 5SIM...")
        success, result = buy_5sim_number(country="indonesia", service="wa")
        if success:
            order_id = result.get('id')
            phone = result.get('phone')
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"✅ **تم حجز الرقم بنجاح!**\n\n📱 الرقم: `{phone}`\n🆔 رقم الطلب: `{order_id}`\n\n⏳ أدخل الرقم في واتساب وانتظر الكود هنا...",
                parse_mode="Markdown"
            )
            t = threading.Thread(target=wait_for_sms, args=(chat_id, order_id, phone))
            t.start()
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"❌ تعذر الشراء من 5SIM:\n`{result}`",
                parse_mode="Markdown"
            )
    elif call.data == "help":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "📌 تعليمات:\nاضغط على شراء رقم، أدخله في التطبيق، وانتظر الكود.")

if __name__ == "__main__":
    print("🚀 البوت بدأ العمل بنجاح...")
    bot.infinity_polling()