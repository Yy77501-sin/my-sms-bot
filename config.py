import os

# -------------------------------------------------------------
# إعدادات البوت والمدير ومزود الخدمة
# -------------------------------------------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN", "8998307482:AAHlUFDu0E_0ltdVQVEGQ5z2pats24kK3rU").strip()
HERO_SMS_API_KEY = os.getenv("HERO_SMS_API_KEY", "67ef5b751b1A4f2bef57dAd7bA2A248c").strip()
ADMIN_ID = str(os.getenv("ADMIN_ID", "8097770003")).strip()
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "Yas_in7").strip()
CURRENCY = "$"

# -------------------------------------------------------------
# إعدادات القنوات الثلاث (يمكن وضع الـ ID أو اليوزرنيم مع @ أو رابط القناة)
# -------------------------------------------------------------

# 1. قناة البوت الرئيسية (للإعلانات والمنشورات)
MAIN_CHANNEL_ID = os.getenv("MAIN_CHANNEL_ID", "@YourMainChannel").strip()
MAIN_CHANNEL_URL = os.getenv("MAIN_CHANNEL_URL", "https://t.me/YourMainChannel").strip()

# 2. قناة التعليمات وشرح استخدام البوت
INSTRUCTIONS_CHANNEL_URL = os.getenv("INSTRUCTIONS_CHANNEL_URL", "https://t.me/YourInstructionsChannel").strip()

# 3. قناة التفعيلات (التي يرسل لها البوت سجل الأرقام والأكواد تلقائياً)
# يفضل وضع ID القناة الرقمي مثل: -1001234567890 أو يوزرنيم القناة مثل: @YourActivationChannel
ACTIVATION_CHANNEL_ID = os.getenv("ACTIVATION_CHANNEL_ID", "@YourActivationChannel").strip()