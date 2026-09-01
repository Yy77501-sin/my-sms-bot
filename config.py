import os

# -------------------------------------------------------------
# إعدادات البوت ومزود الخدمة (Hero SMS)
# -------------------------------------------------------------

# توكن البوت الجديد
BOT_TOKEN = os.getenv("BOT_TOKEN", "8998307482:AAHlUFDu0E_0ltdVQVEGQ5z2pats24kK3rU").strip()

# مفتاح مزود الخدمة Hero SMS الجديد
HERO_SMS_API_KEY = os.getenv("HERO_SMS_API_KEY", "67ef5b751b1A4f2bef57dAd7bA2A248c").strip()

# معرف المدير (ID)
ADMIN_ID = str(os.getenv("ADMIN_ID", "8097770003")).strip()

# معرف حساب الدعم الفني
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "Yas_in7").strip()

# العملة الافتراضية
CURRENCY = "$"