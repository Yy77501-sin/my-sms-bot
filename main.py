import os
import time
import threading
import requests
import telebot
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler

# 1. استيراد الإعدادات من config.py
try:
    import config
    BOT_TOKEN = getattr(config, 'BOT_TOKEN', "8717009668:AAE07ahqxrBFpgto2RJ0R8Kha9WEpofxS74")
    FIVESIM_API_KEY = getattr(config, 'FIVESIM_API_KEY', "")
    SUPPORT_USERNAME = getattr(config, 'SUPPORT_USERNAME', "Yas_in7")
except Exception:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8717009668:AAE07ahqxrBFpgto2RJ0R8Kha9WEpofxS74")
    FIVESIM_API_KEY = os.getenv("FIVESIM_API_KEY", "")
    SUPPORT_USERNAME = "Yas_in7"

# 2. خادم ويب لإرضاء فحص Render 24/7
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Bot Server 5SIM is Live and Active 24/7!")

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

# 3. إعداد البوت
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

def get_auth_headers():
    key = FIVESIM_API_KEY.strip() if FIVESIM_API_KEY else ""
    return {
        'Authorization': f'Bearer {key}',
        'Accept': 'application/json',
    }

# فحص اتصال الحساب والرصيد
def test_5sim_connection():
    try:
        headers = get_auth_headers()
        res = requests.get('https://5sim.net/v1/user/profile', headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            balance = data.get('balance', 0)
            email = data.get('email', 'N/A')
            return True, f"✅ **تم الاتصال بنجاح بموقع 5SIM!**\n\n• 📧 الحساب: `{email}`\n• 💵 الرصيد المتاح: **{balance} $**\n• 🚀 النظام جاهز لاستخراج الأرقام فوراً.", balance
        elif res.status_code == 401:
            return False, "❌ خطأ 401 (المفتاح غير معتمد أو مرفوض).", None
        else:
            return False, f"⚠️ خطأ من 5SIM ({res.status_code}):\n`{res.text}`", None
    except Exception as e:
        return False, f"❌ خطأ أثناء الاتصال: {e}", None

# دالة شراء الرقم المباشرة مع المعالجة الآمنة للـ JSON
def request_buy(country, operator, service):
    try:
        headers = get_auth_headers()
        url = f'https://5sim.net/v1/user/buy/activation/{country}/{operator}/{service}'
        res = requests.get(url, headers=headers, timeout=15)
        
        # محاولة قراءة الـ JSON
        try:
            data = res.json()
            if isinstance(data, dict) and "phone" in data and "id" in data:
                return True, data
            return False, f"رد غير متوقع: {data}"
        except Exception:
            # إذا كان الرد نصاً عادياً
            raw_text = res.text.strip()
            if "no product" in raw_text or "no free phones" in raw_text:
                return False, f"الأرقام لتطبيق ({service}) غير متوفرة حالياً لدى المشغل ({operator}) في ({country}). جرب مشغلاً أو دولة أخرى."
            elif "not enough user balance" in raw_text:
                return False, "رصيد الحساب غير كافٍ."
            return False, raw_text if raw_text else f"رمز الاستجابة: {res.status_code}"
    except Exception as e:
        return False, str(e)

# فحص المخزون الحي للأرقام المتوفرة
def get_available_stock(service):
    stock = []
    try:
        res = requests.get(f'https://5sim.net/v1/guest/prices?product={service}', timeout=10)
        if res.status_code == 200:
            data = res.json()
            for c_code, s_dict in data.items():
                if service in s_dict:
                    ops = s_dict[service]
                    for op_name, op_info in ops.items():
                        count = op_info.get('count', 0)
                        cost = op_info.get('cost', 0)
                        if count > 0:
                            stock.append({
                                'country': c_code,
                                'operator': op_name,
                                'count': count,
                                'cost': cost
                            })
            stock.sort(key=lambda x: x['count'], reverse=True)
    except Exception as e:
        print(f"Stock Error: {e}")
    return stock

# مراقبة كود التفعيل في الخلفية
def monitor_sms_code(chat_id, order_id, phone_number):
    start_time = time.time()
    headers = get_auth_headers()
    while time.time() - start_time < 600:
        time.sleep(5)
        try:
            check_url = f'https://5sim.net/v1/user/check/{order_id}'
            res = requests.get(check_url, headers=headers, timeout=10)
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
                    requests.get(f'https://5sim.net/v1/user/finish/{order_id}', headers=headers)
                    return
                if data.get('status') in ['CANCELED', 'TIMEOUT']:
                    bot.send_message(chat_id, f"⚠️ تم إلغاء طلب الرقم `{phone_number}`.")
                    return
        except Exception as e:
            print(f"SMS Error: {e}")
            
    try:
        requests.get(f'https://5sim.net/v1/user/cancel/{order_id}', headers=headers)
        bot.send_message(chat_id, f"⌛ انتهت مهلة الـ 10 دقائق للرقم `{phone_number}` وتم إلغاء الطلب واسترجاع الرصيد.")
    except Exception as e:
        print(f"Cancel error: {e}")

# ----------------- أوامر البوت -----------------

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_buy = types.InlineKeyboardButton("📱 شراء رقم تفعيل", callback_data="menu_apps")
    btn_balance = types.InlineKeyboardButton("💳 رصيد 5SIM", callback_data="check_balance")
    btn_diag = types.InlineKeyboardButton("🧪 فحص الاتصال بالـ API", callback_data="run_diag")
    btn_support = types.InlineKeyboardButton("💬 الدعم الفني", url=f"https://t.me/{SUPPORT_USERNAME}")
    
    markup.add(btn_buy)
    markup.add(btn_balance, btn_diag)
    markup.add(btn_support)
    
    welcome = (
        f"مرحباً بك يا {message.from_user.first_name} في متجر تفعيل الأرقام الذكي 🌟\n\n"
        f"اختر الخدمة المطلوبة من القائمة أدناه:"
    )
    bot.reply_to(message, welcome, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    # 1. فحص الاتصال التشخيصي
    if call.data == "run_diag":
        bot.answer_callback_query(call.id, "جاري فحص الاتصال بـ 5SIM...")
        success, report, bal = test_5sim_connection()
        bot.send_message(chat_id, report, parse_mode="Markdown")

    # 2. الرصيد
    elif call.data == "check_balance":
        success, report, bal = test_5sim_connection()
        if success:
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, f"💰 **رصيد 5SIM المتاح:** **{bal:.2f} $**\n✅ جاهز للشراء والتفعيل فوراً.", parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "تعذر جلب الرصيد!", show_alert=True)
            bot.send_message(chat_id, report, parse_mode="Markdown")

    # 3. اختيار التطبيق
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
            text="📱 **اختر التطبيق الذي ترغب في تفعيله:**",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 4. عرض الدول الحية المتوفرة
    elif call.data.startswith("srv_"):
        service_code = call.data.replace("srv_", "")
        bot.answer_callback_query(call.id, "جاري فحص المخزون الحي...")
        
        stock_list = get_available_stock(service_code)
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        # خيار الحجز الفوري التلقائي
        markup.add(types.InlineKeyboardButton("⚡ حجز فوري بأعلى مخزون متوفر", callback_data=f"auto_{service_code}"))
        
        added = set()
        for item in stock_list:
            c = item['country']
            if c not in added and len(added) < 6:
                added.add(c)
                markup.add(types.InlineKeyboardButton(f"{c.upper()} ({item['count']} رقم)", callback_data=f"order_{service_code}_{c}_{item['operator']}"))
                
        if not added:
            markup.add(
                types.InlineKeyboardButton("🇮🇩 إندونيسيا", callback_data=f"order_{service_code}_indonesia_any"),
                types.InlineKeyboardButton("🇷🇺 روسيا", callback_data=f"order_{service_code}_russia_any")
            )
            
        markup.add(types.InlineKeyboardButton("🔙 تغيير التطبيق", callback_data="menu_apps"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"🌍 **الدول المتوفر بها أرقام لتطبيق ({service_code}):**\n_اختر 'حجز فوري' أو اختر الدولة المطلوبة:_ ",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 5. الحجز الفوري التلقائي
    elif call.data.startswith("auto_"):
        service_code = call.data.replace("auto_", "")
        bot.answer_callback_query(call.id, "جاري استخراج الرقم...")
        msg = bot.send_message(chat_id, f"⏳ جاري فحص المخزون وسحب رقم شاغر لتطبيق ({service_code})...")
        
        stock_list = get_available_stock(service_code)
        success = False
        res = None
        c_used, op_used = "", ""
        
        if stock_list:
            for item in stock_list[:4]:
                success, res = request_buy(item['country'], item['operator'], service_code)
                if success:
                    c_used, op_used = item['country'], item['operator']
                    break
                    
        if not success:
            for c in ["indonesia", "russia", "kazakhstan", "vietnam"]:
                success, res = request_buy(c, "any", service_code)
                if success:
                    c_used, op_used = c, "any"
                    break

        if success:
            order_id = res.get('id')
            phone = res.get('phone')
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"✅ **تم حجز الرقم بنجاح!**\n\n"
                     f"🌍 الدولة: `{c_used.upper()}` ({op_used})\n"
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
                text=f"❌ **تعذر حجز الرقم:**\nرد سيرفر 5SIM: `{res}`",
                parse_mode="Markdown"
            )

    # 6. شراء دولة محددة
    elif call.data.startswith("order_"):
        parts = call.data.split("_")
        service_code = parts[1]
        country_code = parts[2]
        operator = parts[3] if len(parts) > 3 else "any"
        
        bot.answer_callback_query(call.id, "جاري طلب الرقم...")
        msg = bot.send_message(chat_id, f"⏳ جاري طلب رقم لدولة ({country_code}) لتطبيق ({service_code})...")
        
        success, res = request_buy(country=country_code, operator=operator, service=service_code)
        if success:
            order_id = res.get('id')
            phone = res.get('phone')
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
            t = threading.Thread(target=monitor_sms_code, args=(chat_id, order_id, phone))
            t.start()
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"❌ **تعذر حجز الرقم في ({country_code}):**\nرد 5SIM: `{res}`",
                parse_mode="Markdown"
            )

    elif call.data == "back_main":
        bot.answer_callback_query(call.id)
        start_handler(call.message)

# تشغيل البوت
if __name__ == "__main__":
    print("⏳ جاري تهيئة البوت...")
    time.sleep(2)
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass
    print("🚀 البوت بدأ العمل بنجاح...")
    bot.polling(non_stop=True, interval=1, timeout=30)