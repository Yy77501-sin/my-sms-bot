import os
import time
import threading
import requests
import telebot
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler

# 1. سيرفر الويب لفحص Render Health Check
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

# 2. إعداد التوكن والمفاتيح
BOT_TOKEN = os.getenv("BOT_TOKEN")
FIVESIM_API_KEY = os.getenv("FIVESIM_API_KEY")

# إيقاف التعدد العشوائي لمنع 409 Conflict
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

HEADERS = {
    'Authorization': f'Bearer {FIVESIM_API_KEY}',
    'Accept': 'application/json',
}

# دالة فحص الرصيد الحقيقي
def get_5sim_balance():
    try:
        url = 'https://5sim.net/v1/user/profile'
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            return float(res.json().get('balance', 0))
    except Exception as e:
        print(f"Balance error: {e}")
    return None

# دالة فحص الأسعار والمخزون الحي من 5SIM مباشرة
def get_top_available(service):
    results = []
    try:
        url = f'https://5sim.net/v1/guest/prices?product={service}'
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for country, services in data.items():
                if service in services:
                    operators = services[service]
                    for op, info in operators.items():
                        count = info.get('count', 0)
                        cost = info.get('cost', 0)
                        if count > 0:
                            results.append({
                                'country': country,
                                'operator': op,
                                'count': count,
                                'cost': cost
                            })
            # الترتيب حسب أعلى عدد أرقام متوفرة
            results.sort(key=lambda x: x['count'], reverse=True)
    except Exception as e:
        print(f"Prices API error: {e}")
    return results

# دالة شراء الرقم من 5SIM
def buy_number(country, operator, service):
    try:
        url = f'https://5sim.net/v1/user/buy/activation/{country}/{operator}/{service}'
        res = requests.get(url, headers=HEADERS, timeout=15)
        
        if res.status_code == 200:
            data = res.json()
            if "phone" in data and "id" in data:
                return True, data
            return False, f"استجابة غير متوقعة: {data}"
        else:
            return False, res.text
    except Exception as e:
        return False, str(e)

# الشراء الذكي التلقائي
def smart_auto_buy(service):
    available = get_top_available(service)
    
    if available:
        # تجربة أول 3 خيارات ذات أعلى مخزون شاغر
        for item in available[:3]:
            success, res = buy_number(item['country'], item['operator'], service)
            if success:
                res['country_name'] = item['country']
                res['op_name'] = item['operator']
                return True, res
                
    # محاولة احتياطية على المشغل الافتراضي
    fallback_countries = [("indonesia", "any"), ("russia", "any"), ("kazakhstan", "any"), ("england", "any")]
    last_err = ""
    for c, op in fallback_countries:
        success, res = buy_number(c, op, service)
        if success:
            res['country_name'] = c
            res['op_name'] = op
            return True, res
        else:
            last_err = str(res)
            
    return False, last_err if last_err else "الأرقام غير متوفرة حالياً في المخزون الحي."

# مراقبة كود التفعيل في الخلفية
def wait_for_sms(chat_id, order_id, phone_number):
    start_time = time.time()
    while time.time() - start_time < 600:
        time.sleep(6)
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
                    bot.send_message(chat_id, f"⚠️ تم إلغاء الطلب للرقم `{phone_number}`.")
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
                f"✅ جاهز لشراء وتفعيل الأرقام."
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

    # 3. عرض الدول الحية المتوفرة للتطبيق
    elif call.data.startswith("srv_"):
        service_code = call.data.replace("srv_", "")
        bot.answer_callback_query(call.id, "جاري فحص الدول المتوفرة في 5SIM...")
        
        top_list = get_top_available(service_code)
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("⚡ حجز فوري بأعلى مخزون (موصى به)", callback_data=f"fast_{service_code}"))
        
        added = set()
        for item in top_list:
            c = item['country']
            if c not in added and len(added) < 6:
                added.add(c)
                markup.add(types.InlineKeyboardButton(f"{c.upper()} ({item['count']} رقم)", callback_data=f"buy_{service_code}_{c}_{item['operator']}"))
                
        if not added:
            markup.add(
                types.InlineKeyboardButton("🇮🇩 إندونيسيا", callback_data=f"buy_{service_code}_indonesia_any"),
                types.InlineKeyboardButton("🇷🇺 روسيا", callback_data=f"buy_{service_code}_russia_any")
            )
            
        markup.add(types.InlineKeyboardButton("🔙 تغيير التطبيق", callback_data="menu_apps"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"🌍 **الدول المتوفر بها أرقام شاغرة لتطبيق ({service_code}):**",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 4. الشراء الفوري
    elif call.data.startswith("fast_"):
        service_code = call.data.replace("fast_", "")
        bot.answer_callback_query(call.id, "جاري سحب الرقم...")
        msg = bot.send_message(chat_id, f"⏳ جاري فحص المخزون وسحب رقم شاغر لتطبيق ({service_code})...")
        
        success, result = smart_auto_buy(service_code)
        if success:
            order_id = result.get('id')
            phone = result.get('phone')
            country = result.get('country_name', 'N/A')
            op = result.get('op_name', 'N/A')
            
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"✅ **تم حجز الرقم بنجاح!**\n\n"
                     f"🌍 الدولة: `{country.upper()}` ({op})\n"
                     f"📱 الرقم: `{phone}`\n"
                     f"🆔 رقم الطلب: `{order_id}`\n\n"
                     f"⏳ قم بإدخال الرقم في التطبيق الآن، وسيقوم البوت بإرسال كود التفعيل هنا فور وصوله تلقائياً...",
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
        
        success, result = buy_number(country=country_code, operator=operator, service=service_code)
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
        bot.send_message(chat_id, "📌 تعليمات:\nاختر التطبيق ثم اضغط 'حجز فوري بأعلى مخزون' لتسليم الرقم مباشرة.")

# ----------------- التشغيل الآمن -----------------
if __name__ == "__main__":
    print("⏳ جاري تنظيف الجلسات...")
    time.sleep(3)
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        print(f"Webhook reset: {e}")
        
    print("🚀 البوت بدأ العمل بنجاح...")
    
    while True:
        try:
            bot.polling(non_stop=True, interval=2, timeout=30)
        except Exception as e:
            print(f"Polling loop: {e}")
            time.sleep(5)