# ==========================================
# كتالوج التطبيقات والدول بهامش ربح 10% فقط
# ==========================================

SERVICES = {
    "wa": {"name": "🛍️ WHATSAPP - واتس اب", "short": "WhatsApp", "code": "wa", "icon": "🛍️"},
    "tg": {"name": "🎲 TELEGRAM - تليجرام", "short": "Telegram", "code": "tg", "icon": "🎲"},
    "ig": {"name": "🎳 LNSTAGRAM - انستغرام", "short": "Instagram", "code": "ig", "icon": "🎳"},
    "fb": {"name": "🎯 FACEBOOK - فيسبوك", "short": "Facebook", "code": "fb", "icon": "🎯"},
    "tw": {"name": "🐤 TWITTER - تويتر", "short": "Twitter", "code": "tw", "icon": "🐤"},
    "lf": {"name": "🎥 TIKTOK - تيك توك", "short": "TikTok", "code": "lf", "icon": "🎥"},
    "go": {"name": "☂️ Google - جوجل", "short": "Google", "code": "go", "icon": "☂️"},
    "sn": {"name": "♣️ SNAP - سناب شات", "short": "Snapchat", "code": "fu", "icon": "♣️"},
    "hj": {"name": "🪗 HARAJ - حراج", "short": "Haraj", "code": "au", "icon": "🪗"},
    "im": {"name": "💎 IMO - ايمو", "short": "Imo", "code": "im", "icon": "💎"},
    "ot": {"name": "🤖 السيرفر العام", "short": "Other", "code": "ot", "icon": "🤖"},
    "pp": {"name": "🏐 PAYPAL - بايبال", "short": "PayPal", "code": "ts", "icon": "🏐"},
    "vi": {"name": "📳 Viber - فايبر", "short": "Viber", "code": "vi", "icon": "📳"}
}

# أسعار البيع محسوبة بإضافة 10% فقط على سعر الشراء
COUNTRIES = {
    "21": {"id": "21", "name": "مصر 🇪🇬", "flag": "🇪🇬", "title": "مصر", "prefix": "+20", "cost_rub": 3.3, "cost_usd": 0.055},
    "6": {"id": "6", "name": "إندونيسيا 🇮🇩", "flag": "🇮🇩", "title": "إندونيسيا", "prefix": "+62", "cost_rub": 4.4, "cost_usd": 0.066},
    "0": {"id": "0", "name": "روسيا 🇷🇺", "flag": "🇷🇺", "title": "روسيا", "prefix": "+7", "cost_rub": 5.5, "cost_usd": 0.088},
    "2": {"id": "2", "name": "كازاخستان 🇰🇿", "flag": "🇰🇿", "title": "كازاخستان", "prefix": "+7", "cost_rub": 4.4, "cost_usd": 0.066},
    "10": {"id": "10", "name": "فيتنام 🇻🇳", "flag": "🇻🇳", "title": "فيتنام", "prefix": "+84", "cost_rub": 4.4, "cost_usd": 0.066},
    "73": {"id": "73", "name": "البرازيل 🇧🇷", "flag": "🇧🇷", "title": "البرازيل", "prefix": "+55", "cost_rub": 5.5, "cost_usd": 0.088},
    "8": {"id": "8", "name": "كينيا 🇰🇪", "flag": "🇰🇪", "title": "كينيا", "prefix": "+254", "cost_rub": 3.3, "cost_usd": 0.055},
    "187": {"id": "187", "name": "أمريكا 🇺🇸", "flag": "🇺🇸", "title": "أمريكا", "prefix": "+1", "cost_rub": 7.7, "cost_usd": 0.110},
    "16": {"id": "16", "name": "بريطانيا 🇬🇧", "flag": "🇬🇧", "title": "بريطانيا", "prefix": "+44", "cost_rub": 8.8, "cost_usd": 0.132},
    "4": {"id": "4", "name": "الفلبين 🇵🇭", "flag": "🇵🇭", "title": "الفلبين", "prefix": "+63", "cost_rub": 4.4, "cost_usd": 0.066},
    "36": {"id": "36", "name": "كندا 🇨🇦", "flag": "🇨🇦", "title": "كندا", "prefix": "+1", "cost_rub": 7.7, "cost_usd": 0.110},
    "95": {"id": "95", "name": "الإمارات 🇦🇪", "flag": "🇦🇪", "title": "الإمارات", "prefix": "+971", "cost_rub": 11.0, "cost_usd": 0.165},
    "53": {"id": "53", "name": "السعودية 🇸🇦", "flag": "🇸🇦", "title": "السعودية", "prefix": "+966", "cost_rub": 13.2, "cost_usd": 0.198},
    "116": {"id": "116", "name": "عُمان 🇴🇲", "flag": "🇴🇲", "title": "عُمان", "prefix": "+968", "cost_rub": 11.0, "cost_usd": 0.165},
    "117": {"id": "117", "name": "الأردن 🇯🇴", "flag": "🇯🇴", "title": "الأردن", "prefix": "+962", "cost_rub": 8.8, "cost_usd": 0.132},
    "15": {"id": "15", "name": "بولندا 🇵🇱", "flag": "🇵🇱", "title": "بولندا", "prefix": "+48", "cost_rub": 6.6, "cost_usd": 0.099},
    "78": {"id": "78", "name": "فرنسا 🇫🇷", "flag": "🇫🇷", "title": "فرنسا", "prefix": "+33", "cost_rub": 8.8, "cost_usd": 0.132},
    "62": {"id": "62", "name": "تركيا 🇹🇷", "flag": "🇹🇷", "title": "تركيا", "prefix": "+90", "cost_rub": 9.9, "cost_usd": 0.154},
    "43": {"id": "43", "name": "ألمانيا 🇩🇪", "flag": "🇩🇪", "title": "ألمانيا", "prefix": "+49", "cost_rub": 9.9, "cost_usd": 0.154},
    "1": {"id": "1", "name": "أوكرانيا 🇺🇦", "flag": "🇺🇦", "title": "أوكرانيا", "prefix": "+380", "cost_rub": 5.5, "cost_usd": 0.088},
    "48": {"id": "48", "name": "هولندا 🇳🇱", "flag": "🇳🇱", "title": "هولندا", "prefix": "+31", "cost_rub": 8.8, "cost_usd": 0.132},
    "54": {"id": "54", "name": "المكسيك 🇲🇽", "flag": "🇲🇽", "title": "المكسيك", "prefix": "+52", "cost_rub": 6.6, "cost_usd": 0.099},
    "66": {"id": "66", "name": "باكستان 🇵🇰", "flag": "🇵🇰", "title": "باكستان", "prefix": "+92", "cost_rub": 4.4, "cost_usd": 0.066},
    "33": {"id": "33", "name": "كولومبيا 🇨🇴", "flag": "🇨🇴", "title": "كولومبيا", "prefix": "+57", "cost_rub": 5.5, "cost_usd": 0.088},
    "151": {"id": "151", "name": "تشيلي 🇨🇱", "flag": "🇨🇱", "title": "تشيلي", "prefix": "+56", "cost_rub": 6.6, "cost_usd": 0.099},
    "52": {"id": "52", "name": "تايلاند 🇹🇭", "flag": "🇹🇭", "title": "تايلاند", "prefix": "+66", "cost_rub": 5.5, "cost_usd": 0.088},
    "7": {"id": "7", "name": "ماليزيا 🇲🇾", "flag": "🇲🇾", "title": "ماليزيا", "prefix": "+60", "cost_rub": 5.5, "cost_usd": 0.088},
    "19": {"id": "19", "name": "نيجيريا 🇳🇬", "flag": "🇳🇬", "title": "نيجيريا", "prefix": "+234", "cost_rub": 3.3, "cost_usd": 0.055},
    "31": {"id": "31", "name": "جنوب أفريقيا 🇿🇦", "flag": "🇿🇦", "title": "ج أفريقيا", "prefix": "+27", "cost_rub": 4.4, "cost_usd": 0.066}
}