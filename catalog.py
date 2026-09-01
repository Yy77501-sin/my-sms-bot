# catalog.py - كتالوج الخدمات والسيرفرات والدول

SERVICES = {
    "wa": {"code": "wa", "name": "WhatsApp - واتساب", "short": "WhatsApp"},
    "tg": {"code": "tg", "name": "Telegram - تيليجرام", "short": "Telegram"},
    "ig": {"code": "ig", "name": "Instagram - انستغرام", "short": "Instagram"},
    "fb": {"code": "fb", "name": "Facebook - فيسبوك", "short": "Facebook"},
    "tw": {"code": "tw", "name": "Twitter / X - تويتر", "short": "Twitter"},
    "lf": {"code": "lf", "name": "TikTok - تيك توك", "short": "TikTok"},
    "go": {"code": "go", "name": "Google / Gmail - جوجل", "short": "Google"},
    "sn": {"code": "sn", "name": "Snapchat - سناب شات", "short": "Snapchat"},
    "hj": {"code": "hj", "name": "Haraj - حراج", "short": "Haraj"},
    "im": {"code": "im", "name": "IMO - ايمو", "short": "IMO"},
    "ot": {"code": "ot", "name": "سيرفر عام (Any Other)", "short": "Any Other"},
    "pp": {"code": "pp", "name": "PayPal - بايبال", "short": "PayPal"},
    "vi": {"code": "vi", "name": "Viber - فايبر", "short": "Viber"}
}

SERVERS = {
    "s1": {"title": "🌟 السيرفر VIP الملكي", "badge": "VIP 👑", "multiplier": 1.20},
    "s2": {"title": "⚡ السيرفر السريع الاقتصادي", "badge": "Fast ⚡", "multiplier": 1.00},
    "s3": {"title": "🎯 السيرفر الاحتياطي الشامل", "badge": "Pro 🎯", "multiplier": 1.10}
}

COUNTRIES = {
    "73": {"name": "Yemen", "title": "اليمن", "flag": "🇾🇪", "prefix": "967", "base_usd": 0.50},
    "53": {"name": "Saudi Arabia", "title": "السعودية", "flag": "🇸🇦", "prefix": "966", "base_usd": 0.65},
    "21": {"name": "Egypt", "title": "مصر", "flag": "🇪🇬", "prefix": "20", "base_usd": 0.35},
    "95": {"name": "UAE", "title": "الإمارات", "flag": "🇦🇪", "prefix": "971", "base_usd": 0.70},
    "47": {"name": "Jordan", "title": "الأردن", "flag": "🇯🇴", "prefix": "962", "base_usd": 0.45},
    "48": {"name": "Iraq", "title": "العراق", "flag": "🇮🇶", "prefix": "964", "base_usd": 0.40},
    "187": {"name": "USA", "title": "أمريكا", "flag": "🇺🇸", "prefix": "1", "base_usd": 0.30},
    "16": {"name": "UK", "title": "بريطانيا", "flag": "🇬🇧", "prefix": "44", "base_usd": 0.40},
    "7": {"name": "Brazil", "title": "البرازيل", "flag": "🇧🇷", "prefix": "55", "base_usd": 0.25},
    "22": {"name": "India", "title": "الهند", "flag": "🇮🇳", "prefix": "91", "base_usd": 0.20},
    "6": {"name": "Indonesia", "title": "إندونيسيا", "flag": "🇮🇩", "prefix": "62", "base_usd": 0.25},
    "78": {"name": "France", "title": "فرنسا", "flag": "🇫🇷", "prefix": "33", "base_usd": 0.55},
    "43": {"name": "Germany", "title": "ألمانيا", "flag": "🇩🇪", "prefix": "49", "base_usd": 0.55},
    "86": {"name": "Turkey", "title": "تركيا", "flag": "🇹🇷", "prefix": "90", "base_usd": 0.45},
    "10": {"name": "Algeria", "title": "الجزائر", "flag": "🇩🇿", "prefix": "213", "base_usd": 0.40},
    "89": {"name": "Morocco", "title": "المغرب", "flag": "🇲🇦", "prefix": "212", "base_usd": 0.40}
}