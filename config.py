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
# مفاتيح مزودي الخدمات (5SIM, Grizzly, Hero, Plus)
# -------------------------------------------------------------
FIVESIM_JWT_TOKEN = os.getenv("FIVESIM_JWT_TOKEN", "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MTk4MTcyOTksImlhdCI6MTc4ODI4MTI5OSwicmF5IjoiYmJlMjZmZGFkZGMzM2FiMzFlNDBhM2JmYjNmMTJkMDciLCJzdWIiOjQ0NzgxNTN9.QBAYyUjtp1JdDHdTu50ErRkFP2_BCfvK3O6Htnd6lQkRnD_WEtIPAzvObmpPrINpkx8UUB3h6OT3-rWUGGITU38ZQ5HgOXK6CCRPNuPFMasrHeFFnX9CSOoqa4Lz86NsxF4w3dcBLurR60D-S6cI4Jsk-dPQwXU8OgOamwe37NdM4D2QB5blx9VJgbHVg9jIoeVXMiNaeKdZYHFSHSL8wULCS9ug6EnwzlIDgyreFmFghzLPh20FCysZR0r7I_jcElmmUZAwU8uc94bNxOZ4udBKIZ08JgU1crusM-PWaBsH1TnEYsXKrQlQGQg0LD-pBW97X1iXeAPmWRR0PboNzQ").strip()
GRIZZLY_API_KEY = os.getenv("GRIZZLY_API_KEY", "15a9f459b5a5e02cc330ae0d66399e2b").strip()
HERO_SMS_API_KEY = os.getenv("HERO_SMS_API_KEY", "67ef5b751b1A4f2bef57dAd7bA2A248c").strip()
PLUS_API_KEY = os.getenv("PLUS_API_KEY", "PLUS-6c3caa402169433bb15ae1a7").strip()
PLUS_API_URL = os.getenv("PLUS_API_URL", "https://sms-plus.net/stubs/handler_api.php").strip()

# -------------------------------------------------------------
# إعدادات القنوات
# -------------------------------------------------------------
MAIN_CHANNEL_URL = os.getenv("MAIN_CHANNEL_URL", "https://t.me/Yas_in7").strip()
INSTRUCTIONS_CHANNEL_URL = os.getenv("INSTRUCTIONS_CHANNEL_URL", "https://t.me/Yas_in7").strip()
ACTIVATION_CHANNEL_ID = os.getenv("ACTIVATION_CHANNEL_ID", "").strip()