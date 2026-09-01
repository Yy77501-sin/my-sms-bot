import os

# -------------------------------------------------------------
# إعدادات البوت والمدير والعملة
# -------------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "8998307482:AAHlUFDu0E_0ltdVQVEGQ5z2pats24kK3rU").strip()
ADMIN_ID = str(os.getenv("ADMIN_ID", "8097770003")).strip()
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "Yas_in7").strip()
CURRENCY = "$"

# هامش ربحك المعتمد: 20% فوق سعر المزود بالضبط
PROFIT_MARGIN = 0.20  # +20%

# سعر الصرف: 1 دولار = 30 روبل
RUB_PER_USD = 30.0

# -------------------------------------------------------------
# مفاتيح مزودي الخدمات (Hero SMS & PLUS API)
# -------------------------------------------------------------
HERO_SMS_API_KEY = os.getenv("HERO_SMS_API_KEY", "67ef5b751b1A4f2bef57dAd7bA2A248c").strip()
PLUS_API_KEY = os.getenv("PLUS_API_KEY", "PLUS-6c3caa402169433bb15ae1a7").strip()
PLUS_API_URL = os.getenv("PLUS_API_URL", "https://sms-plus.net/api/v2").strip()

# -------------------------------------------------------------
# إعدادات القنوات الثلاث
# -------------------------------------------------------------
MAIN_CHANNEL_URL = os.getenv("MAIN_CHANNEL_URL", "https://t.me/Yas_in7").strip()
INSTRUCTIONS_CHANNEL_URL = os.getenv("INSTRUCTIONS_CHANNEL_URL", "https://t.me/Yas_in7").strip()
ACTIVATION_CHANNEL_ID = os.getenv("ACTIVATION_CHANNEL_ID", "").strip()