# ==========================================
# كتالوج التطبيقات والدول والمشغلين في 5SIM
# ==========================================

# 1. قائمة التطبيقات المعتمدة في 5SIM
SERVICES = {
    "wa": {
        "name": "🟢 واتساب (WhatsApp)",
        "code": "wa",
        "icon": "💬"
    },
    "tg": {
        "name": "🔵 تيليجرام (Telegram)",
        "code": "tg",
        "icon": "✈️"
    },
    "go": {
        "name": "🔴 جوجل / جيميل / يوتيوب",
        "code": "go",
        "icon": "📧"
    },
    "lf": {
        "name": "🎵 تيك توك (TikTok)",
        "code": "lf",
        "icon": "🎬"
    },
    "fb": {
        "name": "📘 فيسبوك (Facebook)",
        "code": "fb",
        "icon": "👥"
    },
    "tw": {
        "name": "🐦 إكس (تويتر)",
        "code": "tw",
        "icon": "🐦"
    },
    "ig": {
        "name": "📸 إنستغرام (Instagram)",
        "code": "ig",
        "icon": "📷"
    },
    "vi": {
        "name": "🟣 فايبر (Viber)",
        "code": "vi",
        "icon": "📞"
    },
    "ot": {
        "name": "🌐 أي تطبيق آخر (Any Other)",
        "code": "ot",
        "icon": "🔑"
    }
}

# 2. كتالوج الدول الأكثر وفرة مع المشغلين المعتمدين (Operators)
COUNTRIES = {
    "indonesia": {
        "name": "🇮🇩 إندونيسيا",
        "code": "indonesia",
        "operators": ["any", "axis", "indosat", "three", "telkomsel", "smartfren"]
    },
    "russia": {
        "name": "🇷🇺 روسيا",
        "code": "russia",
        "operators": ["any", "tele2", "beeline", "megafon", "mts", "rostelecom"]
    },
    "kazakhstan": {
        "name": "🇰🇿 كازاخستان",
        "code": "kazakhstan",
        "operators": ["any", "tele2", "beeline", "altel", "kcell"]
    },
    "vietnam": {
        "name": "🇻🇳 فيتنام",
        "code": "vietnam",
        "operators": ["any", "viettel", "vinaphone", "vietnamobile", "mobifone"]
    },
    "philippines": {
        "name": "🇵🇭 الفلبين",
        "code": "philippines",
        "operators": ["any", "globe", "smart", "dito"]
    },
    "kenya": {
        "name": "🇰🇪 كينيا",
        "code": "kenya",
        "operators": ["any", "safaricom", "airtel"]
    },
    "england": {
        "name": "🇬🇧 بريطانيا",
        "code": "england",
        "operators": ["any", "ee", "vodafone", "o2", "three"]
    },
    "brazil": {
        "name": "🇧🇷 البرازيل",
        "code": "brazil",
        "operators": ["any", "claro", "tim", "vivo"]
    },
    "colombia": {
        "name": "🇨🇴 كولومبيا",
        "code": "colombia",
        "operators": ["any", "claro", "tigo", "movistar"]
    },
    "egypt": {
        "name": "🇪🇬 مصر",
        "code": "egypt",
        "operators": ["any", "vodafone", "orange", "we", "etisalat"]
    }
}