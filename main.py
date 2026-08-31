import os
import time
import threading
import requests
import telebot
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler

# استيراد الإعدادات من ملف config.py
try:
    import config
    BOT_TOKEN = getattr(config, 'BOT_TOKEN', os.getenv("BOT_TOKEN"))
    FIVESIM_API_KEY = getattr(config, 'FIVESIM_API_KEY', os.getenv("FIVESIM_API_KEY"))
    SUPPORT_USERNAME = getattr(config, 'SUPPORT_USERNAME', "Yas_in7")
    ADMIN_ID = getattr(config, 'ADMIN_ID', "")
except Exception:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    FIVESIM_API_KEY = os.getenv("FIVESIM_API_KEY")
    SUPPORT_USERNAME = "Yas_in7"
    ADMIN_ID = ""

# 1. خادم ويب للحفاظ على اتصال Render 24/7
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Bot Server is Live and Active 24/7!")

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

# 2. تهيئة البوت والـ Headers
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

HEADERS = {
    'Authorization': f'Bearer {FIVESIM_API_KEY}',
    'Accept': 'application/json',
}

# جلب رصيد 5SIM
def get_balance():
    try:
        res = requests.get('https://5sim.net/v1/user/profile', headers=HEADERS, timeout=10)
        if res.status_code == 200:
            return float(res.json().get('balance', 0))
    except Exception as e:
        print(f"Balance error: {e}")
    return None

# جلب الدول المتوفرة في 5SIM لتطبيق معين
def get_available_countries(service):
    candidates = []
    try:
        res = requests.get(f'https://5sim.net/v1/guest/prices?product={service}', timeout=10)
        if res.status_code == 200:
            data = res.json()
            for c_code, s_dict in data.items():
                if service in s_dict:
                    ops = s_dict[service]
                    for op_name, op_data in ops.items():
                        count = op_data.get('count', 0)
                        cost = op_data.get('cost', 0)
                        if count > 0:
                            candidates.append({
                                'country': c_code,
                                'operator': op_name,
                                'count': count,
                                'cost': cost
                            })
            candidates.sort(key=lambda x: x['count'], reverse=True)
    except Exception as e:
        print(f"Prices error: {e}")
    return candidates

# طلب شراء رقم من 5SIM
def order_number(country, operator, service):
    try:
        url = f'https://5sim.net/v1/user/buy/activation/{country}/{operator}/{service}'
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            data = res.json()
            if "phone" in data and "id" in data:
                return True, data
            return False, f"استجابة غير مكتملة: {data}"
        else:
            return False, res.text
    except Exception as e:
        return False, str(e)

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
            print(f"SMS Check Error: {e}")
            
    try:
        requests.get(f'https://5sim.net/v1/user/cancel/{order_id}', headers=HEADERS)
        bot.send_message(chat_id, f"⌛ انتهت مهلة الـ 10 دقائق للرقم `{phone_number}` وتم إلغاء الطلب تلقائياً.")
    except Exception as e:
        print(f"Cancel Error: {e}")

# ----------------- أوامر البوت -----------------

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_buy = types.InlineKeyboardButton("📱 شراء رقم وهمي", callback_data="menu_apps")
    btn_balance = types.InlineKeyboardButton("💳 رصيد 5SIM", callback_data="check_balance")
    btn_support = types.InlineKeyboardButton("💬 الدعم الفني", url=f"https://t.me/{SUPPORT_USERNAME}")
    btn_help = types.InlineKeyboardButton("ℹ️ مساعدة", callback_data="help")
    
    markup.add(btn_buy)
    markup.add(btn_balance, btn_support)
    markup.add(btn_help)
    
    bot.reply_to(
        message, 
        f"مرحباً بك يا {message.from_user.first_name} في متجر تفعيل الأرقام الذكي 🌟\n\nاختر من القائمة أدناه للبدء:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    # 1. فحص الرصيد
    if call.data == "check_balance":
        bal = get_balance()
        if bal is not None:
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, f"💰 **رصيد 5SIM المتاح:** **{bal:.2f} $**\n✅ جاهز للشراء والتفعيل.", parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "تعذر جلب الرصيد! تحقق من المفتاح", show_alert=True)

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
        markup.add(types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_main"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="📱 **اختر التطبيق الذي ترغب في تفعيله:**",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 3. عرض الدول الحية المتوفرة
    elif call.data.startswith("srv_"):
        service_code = call.data.replace("srv_", "")
        bot.answer_callback_query(call.id, "جاري فحص المخزون الحي...")
        
        candidates = get_available_countries(service_code)
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        # حجز فوري
        markup.add(types.InlineKeyboardButton("⚡ حجز فوري بأعلى توفر (موصى به)", callback_data=f"fast_{service_code}"))
        
        added = set()
        for item in candidates:
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
            text=f"🌍 **الدول المتوفر بها أرقام لتطبيق ({service_code}):**",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 4. الشراء الفوري
    elif call.data.startswith("fast_"):
        service_code = call.data.replace("fast_", "")
        bot.answer_callback_query(call.id, "جاري استخراج الرقم...")
        msg = bot.send_message(chat_id, f"⏳ جاري فحص أفضل مشغل وحجز رقم لتطبيق ({service_code})...")
        
        candidates = get_available_countries(service_code)
        success = False
        result = None
        c_name, op_name = "N/A", "N/A"
        
        if candidates:
            for item in candidates[:3]:
                success, result = order_number(item['country'], item['operator'], service_code)
                if success:
                    c_name, op_name = item['country'], item['operator']
                    break
                    
        if not success:
            # محاولة احتياطية
            for c in ["indonesia", "russia", "kazakhstan"]:
                success, result = order_number(c, "any", service_code)
                if success:
                    c_name, op_name = c, "any"
                    break

        if success:
            order_id = result.get('id')
            phone = result.get('phone')
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"✅ **تم حجز الرقم بنجاح!**\n\n"
                     f"🌍 الدولة: `{c_name.upper()}` ({op_name})\n"
                     f"📱 الرقم: `{phone}`\n"
                     f"🆔 رقم الطلب: `{order_id}`\n\n"
                     f"⏳ أدخل الرقم في التطبيق الآن، وسيرسل البوت كود التفعيل هنا فور وصوله...",
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
        
        bot.answer_callback_query(call.id, "جاري طلب الرقم...")
        msg = bot.send_message(chat_id, f"⏳ جاري طلب رقم لدولة ({country_code}) لتطبيق ({service_code})...")
        
        success, result = order_number(country=country_code, operator=operator, service=service_code)
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
                text=f"❌ **تعذر حجز الرقم:**\n`{result}`",
                parse_mode="Markdown"
            )

    elif call.data == "back_main":
        bot.answer_callback_query(call.id)
        start_handler(call.message)
        
    elif call.data == "help":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"📌 **المساعدة والدعم:**\n- يمكنك التواصل مع الدعم الفني: @{SUPPORT_USERNAME}\n- يتم إلغاء أي رقم لا يصله كود تلقائياً بعد 10 دقائق دون أي خصم.")

# ----------------- تشغيل البوت -----------------
if __name__ == "__main__":
    print("⏳ جاري تهيئة البوت...")
    time.sleep(2)
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass
    print("🚀 البوت بدأ العمل بنجاح...")
    bot.polling(non_stop=True, interval=1, timeout=30)