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
ADMIN_ID = str(getattr(config, 'ADMIN_ID', "8097770003"))
SUPPORT_USERNAME = getattr(config, 'SUPPORT_USERNAME', "Yas_in7")
CURRENCY = getattr(config, 'CURRENCY', "$")

# 1. خادم ويب لإرضاء فحص Render 24/7
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Number SMS Store is Running Live 24/7!")

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

# دالة تفعيل زر القائمة السفلية (Menu Button)
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
        print("✅ تم تفعيل زر القائمة السفلية (Menu Commands) بنجاح!")
    except Exception as e:
        print(f"Error setting menu commands: {e}")

# دالة توليد لوحة المفاتيح الرئيسية المطابقة للصورة
def build_main_keyboard(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # 1. شراء رقم افتراضي
    btn_buy = types.InlineKeyboardButton("☎️ شراء رقم افتراضي", callback_data="btn_buy_number")
    markup.add(btn_buy)
    
    # 2. عروض WhatsApp وجاهز Telegram
    btn_wa = types.InlineKeyboardButton("💬 عروض WhatsApp", callback_data="btn_offers_wa")
    btn_tg = types.InlineKeyboardButton("✈️ جاهز Telegram", callback_data="btn_ready_tg")
    markup.add(btn_wa, btn_tg)
    
    # 3. السيرفرات الأكثر مبيعاً
    btn_bestseller = types.InlineKeyboardButton("📈 السيرفرات الأكثر مبيعاً", callback_data="btn_bestseller")
    markup.add(btn_bestseller)
    
    # 4. شحن الرصيد والأكثر توفراً
    btn_deposit = types.InlineKeyboardButton("🎳 • شحن الرصيد •", callback_data="btn_deposit")
    btn_most_available = types.InlineKeyboardButton("🎲 • الأكثر توفراً •", callback_data="btn_most_available")
    markup.add(btn_deposit, btn_most_available)
    
    # 5. الرشق وشحن الألعاب والبرامج
    btn_services_games = types.InlineKeyboardButton("🔭 • الرشق وشحن الألعاب والبرامج •", callback_data="btn_services_games")
    markup.add(btn_services_games)
    
    # 6. اربح مجاناً
    btn_free_ruble = types.InlineKeyboardButton("💎 • اربح رصيد مجاناً •", callback_data="btn_free_points")
    markup.add(btn_free_ruble)
    
    # 7. الدعم وتحويل الرصيد
    btn_support = types.InlineKeyboardButton("🕒 الدعم", url=f"https://t.me/{SUPPORT_USERNAME}")
    btn_transfer = types.InlineKeyboardButton("🔄 • تحويل الرصيد •", callback_data="btn_transfer_balance")
    markup.add(btn_support, btn_transfer)
    
    # 8. إحصائيات الشراء الناجح
    btn_stats = types.InlineKeyboardButton("✔️ • إحصائيات الشراء الناجح •", callback_data="btn_stats")
    markup.add(btn_stats)
    
    # 9. حسابي
    btn_account = types.InlineKeyboardButton("🪪 حسابي", callback_data="btn_my_account")
    markup.add(btn_account)
    
    # 10. خدمات ومميزات أخرى
    btn_extra = types.InlineKeyboardButton("🛸 • خدمات ومميزات أخرى •", callback_data="btn_extra_features")
    markup.add(btn_extra)
    
    # 11. زر لوحة الإدارة (يظهر فقط للأدمن)
    if str(user_id) == str(ADMIN_ID):
        btn_admin = types.InlineKeyboardButton("👑 • لوحة تحكم الإدارة (Admin) •", callback_data="btn_admin_panel")
        markup.add(btn_admin)
        
    return markup

# رسالة الترحيب والواجهة الرئيسية
def get_welcome_text(user):
    user_name = user.first_name if user.first_name else "صديقنا"
    user_id = user.id
    
    text = (
        f"╭━━━〔 **NUMBER SMS** 〕━━━╮\n"
        f"🛍️ أهلاً بك يا **{user_name}** في المتجر الأقوى للأرقام الوهمية والتفعيلات الفورية!\n\n"
        f"👤 • معرفك (ID): `{user_id}`\n"
        f"💵 • رصيدك الحالي: **0.00 {CURRENCY}**\n"
        f"⚡ • حالة السيرفرات: **جاهزة ونشطة 100%**\n"
        f"╰━━━━━━━━━━━━━━━━━╯\n\n"
        f"👇 **تفضل باختيار القسم المطلوب من القائمة أدناه:**"
    )
    return text

# ----------------- معالجة الأوامر من زر القائمة والشات -----------------

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    text = get_welcome_text(message.from_user)
    markup = build_main_keyboard(user_id)
    bot.reply_to(message, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['buy'])
def buy_command(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🟢 أرقام WhatsApp", callback_data="buy_srv_wa"),
        types.InlineKeyboardButton("🔵 أرقام Telegram", callback_data="buy_srv_tg")
    )
    markup.add(
        types.InlineKeyboardButton("🔴 Google / Gmail", callback_data="buy_srv_go"),
        types.InlineKeyboardButton("🎵 TikTok", callback_data="buy_srv_lf")
    )
    markup.add(types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_main"))
    bot.reply_to(message, "☎️ **قسم شراء الأرقام الافتراضية:**\nاختر التطبيق:", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['deposit'])
def deposit_command(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_main"))
    bot.reply_to(message, "🎳 **قسم شحن الرصيد:**\n\nطرق الدفع المتوفرة:\n• بنك الكريمي / ون كاش\n• بنك البسيري / جوالي\n• بايير (Payeer)\n• USDT / Binance Pay", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['account', 'balance'])
def account_command(message):
    user = message.from_user
    text = f"🪪 **معلومات حسابك الشخصي:**\n\n• الاسم: **{user.first_name}**\n• المعرف (ID): `{user.id}`\n• الرصيد الحالي: **0.00 {CURRENCY}**\n• إجمالي المشتريات: **0 رقم**"
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_main"))
    bot.reply_to(message, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['support'])
def support_command(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("💬 تواصل مع الدعم الفني", url=f"https://t.me/{SUPPORT_USERNAME}"))
    bot.reply_to(message, f"🕒 **الدعم الفني:**\nلأي استفسار أو مساعدة تواصل معنا مباشرة:", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['admin'])
def admin_command(message):
    user_id = message.from_user.id
    if str(user_id) != str(ADMIN_ID):
        bot.reply_to(message, "⛔ هذا الأمر خاص بإدارة البوت فقط!")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ شحن رصيد لمستخدم", callback_data="admin_add_balance"),
        types.InlineKeyboardButton("➖ خصم رصيد من مستخدم", callback_data="admin_deduct_balance")
    )
    markup.add(
        types.InlineKeyboardButton("📢 إذاعة رسالة للكل", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("📊 إحصائيات البوت", callback_data="admin_full_stats")
    )
    markup.add(
        types.InlineKeyboardButton("💳 فحص رصيد Hero SMS", callback_data="admin_check_provider")
    )
    markup.add(types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="back_to_main"))
    bot.reply_to(message, "👑 **أهلاً بك يا مدير البوت في لوحة التحكم الإدارية:**", reply_markup=markup, parse_mode="Markdown")

# ----------------- معالجة الضغط على أزرار الإنلاين -----------------

@bot.callback_query_handler(func=lambda call: True)
def main_callback_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
    
    # العودة للقائمة الرئيسية
    if data == "back_to_main":
        bot.answer_callback_query(call.id)
        text = get_welcome_text(call.from_user)
        markup = build_main_keyboard(user_id)
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 1. زر شراء رقم افتراضي
    elif data == "btn_buy_number":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🟢 أرقام WhatsApp", callback_data="buy_srv_wa"),
            types.InlineKeyboardButton("🔵 أرقام Telegram", callback_data="buy_srv_tg")
        )
        markup.add(
            types.InlineKeyboardButton("🔴 Google / Gmail", callback_data="buy_srv_go"),
            types.InlineKeyboardButton("🎵 TikTok", callback_data="buy_srv_lf")
        )
        markup.add(
            types.InlineKeyboardButton("📘 Facebook", callback_data="buy_srv_fb"),
            types.InlineKeyboardButton("🐦 Twitter / X", callback_data="buy_srv_tw")
        )
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="☎️ **قسم شراء الأرقام الافتراضية:**\n\nاختر التطبيق الذي تريد تفعيله:",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 2. عروض WhatsApp
    elif data == "btn_offers_wa":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="💬 **قسم عروض WhatsApp المميزة:**\n\nقريباً سيتم عرض أفضل السيرفرات المخفضة لواتساب!",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 3. جاهز Telegram
    elif data == "btn_ready_tg":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="✈️ **قسم حسابات وأرقام Telegram الجاهزة:**\n\nتوفير أرقام وحسابات تيليجرام بأعلى جودة وثبات.",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 4. السيرفرات الأكثر مبيعاً
    elif data == "btn_bestseller":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="📈 **السيرفرات الأكثر مبيعاً وطلباً:**\n\n1. 🇮🇩 إندونيسيا (WhatsApp & Telegram)\n2. 🇷🇺 روسيا (جميع التطبيقات)\n3. 🇰🇿 كازاخستان (Google & Telegram)\n4. 🇻🇳 فيتنام (TikTok & Facebook)",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 5. شحن الرصيد
    elif data == "btn_deposit":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="🎳 **قسم شحن الرصيد:**\n\nطرق الدفع المتوفرة:\n• بنك الكريمي / ون كاش\n• بنك البسيري / جوالي\n• بايير (Payeer)\n• USDT / Binance Pay",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 6. الأكثر توفراً
    elif data == "btn_most_available":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="🎲 **الدول الأكثر وفرة حالياً:**\n\n• إندونيسيا 🇮🇩\n• روسيا 🇷🇺\n• كازاخستان 🇰🇿\n• فيتنام 🇻🇳\n• البرازيل 🇧🇷",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 7. الرشق وشحن الألعاب والبرامج
    elif data == "btn_services_games":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="🔭 **خدمات الرشق وشحن الألعاب:**\n\n• رشق متابعين ومشاهدات (تيليجرام، تيك توك، إنستغرام)\n• شحن شدات ببجي وجواهر فري فاير\n• بطاقات رقمية واشتراكات",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 8. اربح رصيد مجاناً
    elif data == "btn_free_points":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"💎 **نظام الأرباح والمكافآت (الإحالة):**\n\nشارك رابط الإحالة الخاص بك مع أصدقائك:\n`https://t.me/{bot.get_me().username}?start={user_id}`\n\nواحصل على رصيد مجاني لكل صديق يقوم بالشحن والشراء!",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 9. تحويل الرصيد
    elif data == "btn_transfer_balance":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="🔄 **تحويل الرصيد بين المستخدمين:**\n\nيمكنك تحويل رصيد لأي مستخدم آخر عبر معرف حسابه (ID) مباشرة وبدون عمولة.",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 10. إحصائيات الشراء الناجح
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

    # 11. حسابي
    elif data == "btn_my_account":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"🪪 **معلومات حسابك الشخصي:**\n\n• الاسم: **{call.from_user.first_name}**\n• المعرف (ID): `{user_id}`\n• الرصيد الحالي: **0.00 {CURRENCY}**\n• إجمالي المشتريات: **0 رقم**",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 12. خدمات ومميزات أخرى
    elif data == "btn_extra_features":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="🛸 **خدمات ومميزات إضافية:**\n\n• تنبيهات توفر الأرقام الشحيحة\n• فحص الأرقام المتاحة لحظياً\n• قنوات التحديثات والشروحات",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # 13. لوحة تحكم الإدارة (خاصة بالأدمن فقط)
    elif data == "btn_admin_panel":
        if str(user_id) != str(ADMIN_ID):
            bot.answer_callback_query(call.id, "⛔ ليس لديك صلاحية الوصول لهذه اللوحة!", show_alert=True)
            return
            
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("➕ شحن رصيد لمستخدم", callback_data="admin_add_balance"),
            types.InlineKeyboardButton("➖ خصم رصيد من مستخدم", callback_data="admin_deduct_balance")
        )
        markup.add(
            types.InlineKeyboardButton("📢 إذاعة رسالة للكل", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("📊 إحصائيات البوت الكاملة", callback_data="admin_full_stats")
        )
        markup.add(
            types.InlineKeyboardButton("💳 فحص رصيد Hero SMS", callback_data="admin_check_provider")
        )
        markup.add(types.InlineKeyboardButton("🔙 العودة للواجهة الرئيسية", callback_data="back_to_main"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="👑 **أهلاً بك يا مدير البوت في لوحة التحكم الإدارية:**\n\nاختر الإجراء الذي ترغب في تنفيذه:",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    # فحص رصيد المزود من داخل لوحة الأدمن
    elif data == "admin_check_provider":
        if str(user_id) != str(ADMIN_ID):
            return
        bot.answer_callback_query(call.id, "جاري فحص رصيد Hero SMS...")
        try:
            res = requests.get(f"https://sms-hero.com/stubs/handler_api.php?api_key={API_KEY}&action=getBalance", timeout=10)
            if res.text.startswith("ACCESS_BALANCE:"):
                b = res.text.split(":")[1]
                bot.send_message(chat_id, f"💳 **رصيد حسابك في مزود Hero SMS هو:** `{b} $`", parse_mode="Markdown")
            else:
                bot.send_message(chat_id, f"⚠️ الرد: {res.text}")
        except Exception as e:
            bot.send_message(chat_id, f"❌ خطأ: {e}")

# ----------------- تشغيل البوت -----------------
if __name__ == "__main__":
    print("⏳ جاري تهيئة وضبط زر القائمة السفلية (Menu)...")
    time.sleep(2)
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass
    
    # تفعيل قائمة الأوامر المنبثقة
    setup_bot_menu_commands()
    
    print("🚀 البوت يعمل الآن بكامل الواجهات والقوائم...")
    bot.polling(non_stop=True, interval=1, timeout=30)