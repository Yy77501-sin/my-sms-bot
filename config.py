import os

# -------------------------------------------------------------
# الإعدادات الأساسية للبوت والمتجر
# -------------------------------------------------------------

# توكن البوت الجديد الآمن
BOT_TOKEN = os.getenv("BOT_TOKEN", "8998307482:AAHlUFDu0E_0ltdVQVEGQ5z2pats24kK3rU")

# مفتاح مزود الأرقام (Hero SMS)
HERO_SMS_API_KEY = os.getenv("HERO_SMS_API_KEY", "b3040375cf393b48dfce23793c4efb2d")

# معرف المدير (ID)
ADMIN_ID = os.getenv("ADMIN_ID", "8097770003")

# معرف حساب الدعم الفني على تيليجرام
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "Yas_in7")

# العملة الافتراضية
CURRENCY = "$"