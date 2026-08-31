import os
import time
import threading
import requests
import telebot
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler

# 1. خادم ويب للحفاظ على اتصال السيرفر 24/7
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

web_thread = threading.Thread(target=run_web_server, daemon=True)
web_thread.start()

# 2. مفاتيح البوت و 5SIM
BOT_TOKEN = os.getenv("BOT_TOKEN", "7963490715:AAFFY4D7pT4lJg7rB1uJ6lC...")
FIVESIM_API_KEY = os.getenv("FIVESIM_API_KEY", "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MTkzODY1MzQsImlhdCI6MTc4Nzg1MDUzNCwicmF5IjoiNTQ2ZGUzMGYzYzgzN2I0ZTFjOGY1OTBiZTRiYzFjOGQiLCJzdWIiOjQ0NzgxNTN9.wBm9S_D_ZyySSX0o4cJ_io_90Edn4PG9_vIn2s65-hciWtTFTaVFAzXHFNYUHbfAkOXqhGJZ_5YhpDn-GsfP0JtyyVWbMHgZ1wT2qViiXxGbbv_icGfxrrT37ynjqUT84J-DWWt2pbEX0O79gpMyrOykacd5EQv_24a85zhwiv666dDen5pQ9ShBucIt19JPH94DjPkFfLs3JvDSjK0Bs7f3m-d2VCAEVB0p2yn5-5QjiIDb_UdlaU2wEvN3zUWxWvjuB5DLfm-bY0dhVkMAw3RVE5TCnF931w-9gPMTahmfOEAAxfH38tdu-BItQnShlkLP2TpLFKeS24PuvJp2GQ")

bot = telebot.TeleBot(BOT_TOKEN)

HEADERS = {
    'Authorization': f'Bearer {FIVESIM_API_KEY}',
    'Accept': 'application/json',
}

# جلب الرصيد الحقيقي بالدولار
def get_5sim_balance():
    try:
        url = 'https://5sim.net/v1/user/profile'
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            balance = data.get('balance', 0)
            return float(balance)
    except Exception as e:
        print(f"Balance error: {e}")
    return None

# دالة شراء الرقم من 5SIM
def buy_5sim_number(country, service):
    try:
        url = f'https://5sim.net/v1/user/buy/activation/{country}/any/{service}'
        res = requests.get(url, headers=HEADERS, timeout=15)
        
        if res.status_code == 200:
            return True, res.json()
        else:
            err_text = res.text
            if "no product" in err_text or "no free phones" in err_text:
                return False, f"⚠️ أرقام تطبيق ({service}) في دولة ({country}) غير متوفرة في هذه اللحظة عند المشغل. يرجى تجربة دولة أخرى من القائمة!"
            elif "not enough user balance" in err_text:
                return False, "❌ رصيد الحساب غير كافٍ."
            return False, f"رد المزود: {err_text}"
    except Exception as e:
        return False, str(e)

# فحص وصول كود التحقق
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
            print(f"Error checking SMS: {e}")
            
    try:
        requests.get(f'https://5sim.net/v1/user/cancel/{order_id}', headers=HEADERS)
        bot.send_message(chat_id, f"⌛ انتهت مهلة الـ 10 دقائق للرقم `{phone_number}` وتم إلغاء الطلب تلقائياً.")
    except Exception as e:
        print(f"Cancel error: {e}")

# ----------------- أوامر البوت -----------------

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn_apps = types.InlineKeyboardButton("📱 شراء رقم تفعيل", callback_data="menu_apps")
    btn_balance = types.InlineKeyboardButton("💳 رصيد حساب 5SIM", callback_data="check_balance")
    btn_help = types.InlineKeyboardButton("ℹ️ مساعدة والدعم", callback_data="help")
    
    markup.add(btn_apps)
    markup.add(btn_balance, btn_help)
    
    bot.reply_to(
        message, 
        f"مرحباً بك يا {message.from_user.first_name} في بوت تفعيل الأرقام الوهمية 🌟\n\n"
        f"اختر الخدمة المطلوبة من الأزرار أدناه:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    # 1. عرض الرصيد الحقيقي بالدولار
    if call.data == "check_balance":
        balance = get_5sim_balance()
        if balance is not None:
            bot.answer_callback_query(call.id)
            text = (
                f"💰 **رصيد حسابك في 5SIM:**\n\n"
                f"💵 الرصيد الحالي: **{balance:.2f} $ (دولار أمريكي)**\n"
                f"✅ رصيدك ممتاز وجاهز لشراء أرقام متعددة!"
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

    # 3. قائمة الدول للتطبيق المختار
    elif call.data.startswith("srv_"):
        service_code = call.data.replace("srv_", "")
        bot.answer_callback_query(call.id)
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        # مجموعة من أكثر الدول توفراً لأرقام الواتساب والتيليجرام في 5SIM
        markup.add(
            types.InlineKeyboardButton("🇮🇩 إندونيسيا", callback_data=f"buy_{service_code}_indonesia"),
            types.InlineKeyboardButton("🇷🇺 روسيا", callback_data=f"buy_{service_code}_russia")
        )
        markup.add(
            types.InlineKeyboardButton("🇰🇿 كازاخستان", callback_data=f"buy_{service_code}_kazakhstan"),
            types.InlineKeyboardButton("🇬🇧 بريطانيا", callback_data=f"buy_{service_code}_england")
        )
        markup.add(
            types.InlineKeyboardButton("🇧🇷 البرازيل", callback_data=f"buy_{service_code}_brazil"),
            types.InlineKeyboardButton("🇪🇬 مصر", callback_data=f"buy_{service_code}_egypt")
        )
        markup.add(
            types.InlineKeyboardButton("🇵🇭 الفلبين", callback_data=f"buy_{service_code}_philippines"),
            types.InlineKeyboardButton("🇺🇸 أمريكا", callback_data=f"buy_{service_code}_usa")
        )
        markup.add(types.InlineKeyboardButton("🔙 تغيير التطبيق", callback_data="menu_apps"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"🌍 **اختر الدولة للخدمة ({service_code}):**\n_إذا نفدت الأرقام في دولة، جرب دولة أخرى مباشرة_",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 4. تنفيذ شراء الرقم
    elif call.data.startswith("buy_"):
        parts = call.data.split("_")
        service_code = parts[1]
        country_code = parts[2]
        
        bot.answer_callback_query(call.id, "جاري حجز الرقم من 5SIM...")
        msg = bot.send_message(chat_id, f"⏳ جاري حجز رقم لدولة ({country_code}) لتطبيق ({service_code})...")
        
        success, result = buy_5sim_number(country=country_code, service=service_code)
        if success:
            order_id = result.get('id')
            phone = result.get('phone')
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"✅ **تم حجز الرقم بنجاح!**\n\n"
                     f"📱 الرقم: `{phone}`\n"
                     f"🆔 رقم الطلب: `{order_id}`\n\n"
                     f"⏳ أدخل الرقم الآن في التطبيق، وسيقوم البوت بإرسال كود التحقق هنا فور وصوله تلقائياً...",
                parse_mode="Markdown"
            )
            t = threading.Thread(target=wait_for_sms, args=(chat_id, order_id, phone))
            t.start()
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"❌ **تعذر حجز الرقم:**\n{result}",
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
            "1. اضغط على 'شراء رقم تفعيل'.\n"
            "2. اختر التطبيق (واتساب، تيليجرام، جوجل...).\n"
            "3. اختر الدولة (مثل: إندونيسيا، البرازيل، كازاخستان، روسيا).\n"
            "4. سيعطيك البوت الرقم مباشرة.\n"
            "5. ادخل الرقم في التطبيق، وانتظر وصول الكود في محادثة البوت!"
        )

if __name__ == "__main__":
    print("🚀 البوت بدأ العمل بنجاح...")
    bot.infinity_polling()