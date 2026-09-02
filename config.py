import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8998307482:AAFBU5NU02OH-LaVEpvJqtJUQ1XjKPg6bEY").strip()
ADMIN_ID = str(os.getenv("ADMIN_ID", "8097770003")).strip()
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "Yas_in7").strip()
CURRENCY = "$"

# هامش الربح المعتمد: 30% فوق سعر المزود تلقائياً
PROFIT_MARGIN = 0.30

# سعر الصرف: 1 دولار = 30 روبل
RUB_PER_USD = 30.0

# مفاتيح مزودي الأرقام والسيرفرات
FIVESIM_JWT_TOKEN = os.getenv("FIVESIM_JWT_TOKEN", "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9...").strip()
GRIZZLY_API_KEY = os.getenv("GRIZZLY_API_KEY", "15a9f459b5a5e02cc330ae0d66399e2b").strip()
HERO_SMS_API_KEY = os.getenv("HERO_SMS_API_KEY", "67ef5b751b1A4f2bef57dAd7bA2A248c").strip()
PLUS_API_KEY = os.getenv("PLUS_API_KEY", "PLUS-6c3caa402169433bb15ae1a7").strip()
PLUS_API_URL = os.getenv("PLUS_API_URL", "https://sms-plus.net/stubs/handler_api.php").strip()

MAIN_CHANNEL_URL = os.getenv("MAIN_CHANNEL_URL", "https://t.me/Yas_in7").strip()
INSTRUCTIONS_CHANNEL_URL = os.getenv("INSTRUCTIONS_CHANNEL_URL", "https://t.me/Yas_in7").strip()
ACTIVATION_CHANNEL_ID = os.getenv("ACTIVATION_CHANNEL_ID", "").strip()
