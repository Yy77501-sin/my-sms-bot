import os
import time
import threading
import requests
import telebot
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler

# استيراد الإعدادات والكتالوج
import config
import catalog

BOT_TOKEN = getattr(config, 'BOT_TOKEN', os.getenv("BOT_TOKEN"))
API_KEY = getattr(config, 'HERO_SMS_API_KEY', os.getenv("HERO_SMS_API_KEY"))
SUPPORT_USERNAME = getattr(config, 'SUPPORT_USERNAME', "Yas_in7")

# 1. خادم ويب لإرضاء فحص Render 24/7
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"HeroSMS Bot Server is Running Alive 24/7!")

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

# روابط واجهة الـ API لموقع Hero SMS (مع دعم الروابط البديلة)
API_ENDPOINTS = [
    "https://sms-hero.com/stubs/handler_api.php",
    "https://hero-sms.com/stubs/handler_api.php",
    "https://api.sms-hero.com/stubs/handler_api.php"
]

# دالة إرسال الطلبات الآمنة للمزود
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

# فحص رصيد حساب Hero SMS
def get_hero_balance():
    resp = api_request({'action': 'getBalance'})
    if resp.startswith("ACCESS_BALANCE:"):
        balance = float(resp.split(":")[1])
        return True, balance
    elif resp == "BAD_KEY":
        return False, "المفتاح (API Key) غير صحيح أو غير مفعل."
    elif resp == "ERROR_SQL":
        return False, "خطأ في قاعدة بيانات المزود."
    return False, resp

# طلب شراء رقم تفعيل
def buy_hero_number(service_code, country_id):
    resp = api_request({
        'action': 'getNumber',
        'service': service_code,
        'country': country_id
    })
    
    if resp.startswith("ACCESS_NUMBER:"):
        parts = resp.split(":")
        order_id = parts[1]
        phone_number = parts[2]
        return True, {"id": order_id, "phone": phone_number}
    elif resp == "NO_NUMBERS":
        return False, "الأرقام لهذه الدولة والتطبيق غير متوفرة حالياً في المخزون."
    elif resp == "NO_BALANCE":
        return False, "رصيد الحساب غير كافٍ لشراء هذا الرقم."
    elif resp == "BAD_KEY":
        return False, "مفتاح الـ API غير صالح."
    return False, f"رد المزود: {resp}"

# تغيير حالة الطلب (إلغاء / تم الاستلام)
def set_status(order_id, status_code):
    # status 8 = إلغاء الطلب واسترجاع الرصيد
    # status 6 = تم استلام الكود وإتمام الطلب بنجاح
    api_request({
        'action': 'setStatus',
        'id': order_id,
        'status': status_code
    })

# فحص كود التفعيل في الخلفية
def monitor_sms_code(chat_id, order_id, phone_number):
    start_time = time.time()
    while time.time() - start_time < 600:  # انتظار 10 دقائق
        time.sleep(6)
        try:
            resp = api_request({
                'action': 'getStatus',
                'id': order_id
            })
            
            if resp.startswith("STATUS_OK:"):
                code = resp.split(":")[1]
                bot.send_message(
                    chat_id,
                    f"🎉 **وصل كود التفعيل بنجاح!**\n\n"
                    f"📱 الرقم: `{phone_number}`\n"
                    f"🔑 الكود: `{code}`\n\n"
                    f"✅ تم تأكيد تفعيل الرقم بنجاح.",
                    parse_mode="Markdown"
                )
                set_status(order_id, 6)
                return
            elif resp == "STATUS_CANCEL":
                bot.send_message(chat_id, f"⚠️ تم إلغاء طلب الرقم `{phone_number}`.")
                return
        except Exception as e:
            print(f"SMS Check Error: {e}")
            
    # إلغاء الطلب بعد انتهاء المهلة
    set_status(order_id, 8)
    bot.send_message(chat_id, f"⌛ انتهت المهلة للرقم `{phone_number}` وتم إلغاء الطلب واسترجاع الرصيد تلقائياً.")

# ----------------- أوامر البوت -----------------

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_buy = types.InlineKeyboardButton("📱 شراء رقم تفعيل", callback_data="menu_services")
    btn_bal = types.InlineKeyboardButton("💳 رصيد Hero SMS", callback_data="check_balance")
    btn_diag = types.InlineKeyboardButton("🧪 فحص الاتصال بالـ API", callback_data="run_diag")
    btn_support = types.InlineKeyboardButton("💬 الدعم الفني", url=f"https://t.me/{SUPPORT_USERNAME}")
    
    markup.add(btn_buy)
    markup.add(btn_bal, btn_diag)
    markup.add(btn_support)
    
    welcome_text = (
        f"مرحباً بك يا {message.from_user.first_name} في **متجر تفعيل الأرقام الذكي (Hero SMS)** 🌟\n\n"
        f"اختر الخدمة المطلوبة من القائمة أدناه:"
    )
    bot.reply_to(message, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    # 1. فحص الاتصال بالـ API
    if call.data == "run_diag":
        bot.answer_callback_query(call.id, "جاري فحص الاتصال بـ Hero SMS...")
        success, res = get_hero_balance()
        if success:
            bot.send_message(
                chat_id,
                f"✅ **الاتصال ناجح ومستقر بنسبة 100%!**\n\n"
                f"• 🌐 المزود: `Hero SMS`\n"
                f"• 💵 الرصيد المتاح: **{res:.2f} $**\n"
                f"• 🚀 البوت جاهز لاستخراج الأرقام فوراً.",
                parse_mode="Markdown"
            )
        else:
            bot.send_message(chat_id, f"❌ فشل الاتصال:\n`{res}`", parse_mode="Markdown")

    # 2. عرض الرصيد
    elif call.data == "check_balance":
        success, res = get_hero_balance()
        if success:
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, f"💰 **رصيد حسابك في Hero SMS:** **{res:.2f} $**\n✅ جاهز لشراء وتفعيل الأرقام.", parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "تعذر جلب الرصيد!", show_alert=True)
            bot.send_message(chat_id, f"❌ خطأ:\n`{res}`", parse_mode="Markdown")

    # 3. عرض قائمة التطبيقات
    elif call.data == "menu_services":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for s_code, s_info in catalog.SERVICES.items():
            buttons.append(types.InlineKeyboardButton(s_info["name"], callback_data=f"srv_{s_code}"))
            
        markup.add(*buttons)
        markup.add(types.InlineKeyboardButton("🔙 الرئيسية", callback_data="back_main"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="📱 **اختر التطبيق الذي ترغب في تفعيله:**",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 4. عرض الدول المتاحة للتطبيق
    elif call.data.startswith("srv_"):
        service_code = call.data.replace("srv_", "")
        service_name = catalog.SERVICES.get(service_code, {}).get("name", service_code)
        bot.answer_callback_query(call.id)
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        # زر السحب التلقائي الذكي
        markup.add(types.InlineKeyboardButton("⚡ أسرع دولة متوفرة (تلقائي)", callback_data=f"auto_{service_code}"))
        
        c_buttons = []
        for c_id, c_data in catalog.COUNTRIES.items():
            c_buttons.append(types.InlineKeyboardButton(c_data["name"], callback_data=f"buy_{service_code}_{c_id}"))
            
        markup.add(*c_buttons)
        markup.add(types.InlineKeyboardButton("🔙 تغيير التطبيق", callback_data="menu_services"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"🌍 **اختر الدولة لخدمة {service_name}:**",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 5. الشراء التلقائي لأسرع دولة متوفرة
    elif call.data.startswith("auto_"):
        service_code = call.data.replace("auto_", "")
        service_name = catalog.SERVICES.get(service_code, {}).get("name", service_code)
        
        bot.answer_callback_query(call.id, "جاري فحص أفضل دولة وسحب الرقم...")
        msg = bot.send_message(chat_id, f"⏳ جاري البحث عن رقم متوفر لـ {service_name}...")
        
        # ترتيب الدول الأكثر وفرة
        priority_countries = ["6", "0", "2", "10", "4", "73", "8", "16"]
        success = False
        result = None
        c_name = "N/A"
        
        for c_id in priority_countries:
            success, result = buy_hero_number(service_code, c_id)
            if success:
                c_name = catalog.COUNTRIES.get(c_id, {}).get("name", "دولة متوفرة")
                break
                
        if success:
            order_id = result.get('id')
            phone = result.get('phone')
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"✅ **تم حجز الرقم بنجاح من Hero SMS!**\n\n"
                     f"🌍 الدولة: **{c_name}**\n"
                     f"📱 الرقم: `{phone}`\n"
                     f"🆔 رقم الطلب: `{order_id}`\n\n"
                     f"⏳ أدخل الرقم في التطبيق الآن، وسيقوم البوت بإرسال كود التفعيل هنا فور وصوله تلقائياً...",
                parse_mode="Markdown"
            )
            t = threading.Thread(target=monitor_sms_code, args=(chat_id, order_id, phone))
            t.start()
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"❌ تعذر الحجز التلقائي حالياً.\n👉 **يرجى اختيار دولة محددة من القائمة.**",
                parse_mode="Markdown"
            )

    # 6. شراء دولة محددة
    elif call.data.startswith("buy_"):
        parts = call.data.split("_")
        service_code = parts[1]
        country_id = parts[2]
        
        service_name = catalog.SERVICES.get(service_code, {}).get("name", service_code)
        country_name = catalog.COUNTRIES.get(country_id, {}).get("name", "الدولة")
        
        bot.answer_callback_query(call.id, f"جاري طلب رقم {country_name}...")
        msg = bot.send_message(chat_id, f"⏳ جاري حجز رقم {country_name} لتطبيق {service_name}...")
        
        success, result = buy_hero_number(service_code, country_id)
        if success:
            order_id = result.get('id')
            phone = result.get('phone')
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"✅ **تم حجز الرقم بنجاح!**\n\n"
                     f"🌍 الدولة: **{country_name}**\n"
                     f"📱 الرقم: `{phone}`\n"
                     f"🆔 رقم الطلب: `{order_id}`\n\n"
                     f"⏳ أدخل الرقم في التطبيق الآن، وسيرسل البوت كود التحقق فور وصوله...",
                parse_mode="Markdown"
            )
            t = threading.Thread(target=monitor_sms_code, args=(chat_id, order_id, phone))
            t.start()
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"❌ **تعذر حجز الرقم في {country_name}:**\n{result}\n\n👉 **جرب دولة أخرى (مثل إندونيسيا، روسيا، كازاخستان، فيتنام)**.",
                parse_mode="Markdown"
            )

    elif call.data == "back_main":
        bot.answer_callback_query(call.id)
        start_handler(call.message)

# ----------------- تشغيل البوت -----------------
if __name__ == "__main__":
    print("⏳ جاري تهيئة بوت Hero SMS...")
    time.sleep(2)
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass
    print("🚀 البوت بدأ العمل بنجاح على مزود Hero SMS...")
    bot.polling(non_stop=True, interval=1, timeout=30)