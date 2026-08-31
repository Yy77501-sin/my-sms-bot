import os
import telebot
from telebot import types

# قراءة التوكن من متغيرات بيئة السيرفر (أو وضعه مباشرة مؤقتاً)
BOT_TOKEN = os.getenv("BOT_TOKEN", "ضع_التوكن_الخاص_بك_هنا")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn_buy = types.InlineKeyboardButton("📱 شراء رقم جديد", callback_data="buy_number")
    btn_balance = types.InlineKeyboardButton("💳 رصيدي والحساب", callback_data="my_balance")
    btn_deposit = types.InlineKeyboardButton("💰 شحن الرصيد", callback_data="deposit")
    btn_help = types.InlineKeyboardButton("ℹ️ المساعدة والدعم", callback_data="help")
    
    markup.add(btn_buy)
    markup.add(btn_balance, btn_deposit)
    markup.add(btn_help)
    
    welcome_text = f"مرحباً بك يا {user_name} في بوت تفعيل الأرقام! 🌟\n(البوت يعمل الآن على خوادم Render 🚀)"
    bot.reply_to(message, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if call.data == "buy_number":
        bot.answer_callback_query(call.id, "جاري فتح قسم الأرقام...")
        bot.send_message(call.message.chat.id, "📋 الخدمات المتاحة:\n1️⃣ واتساب\n2️⃣ تيليجرام\n3️⃣ جوجل\n(سنربط الـ API في الخطوة التالية)")
    elif call.data == "my_balance":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💰 رصيدك الحالي: 0.00$")
    elif call.data == "deposit":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💳 للشحن، يرجى التواصل مع الدعم.")
    elif call.data == "help":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📌 تعليمات الاستخدام:\n- اختر التطبيق والدولة.\n- مهلة الكود 15 دقيقة.")

if __name__ == "__main__":
    print("🚀 البوت بدأ العمل بنجاح على Render...")
    bot.infinity_polling()
