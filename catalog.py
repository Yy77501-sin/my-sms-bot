# ==========================================
# كتالوج الخدمات والتطبيقات المدعومة
# ==========================================

SERVICES = {
    "wa": {"name": "واتساب WhatsApp", "code": "wa", "short": "WhatsApp"},
    "tg": {"name": "تيليجرام Telegram", "code": "tg", "short": "Telegram"},
    "ig": {"name": "إنستغرام Instagram", "code": "ig", "short": "Instagram"},
    "fb": {"name": "فيسبوك Facebook", "code": "fb", "short": "Facebook"},
    "tw": {"name": "تويتر / X", "code": "tw", "short": "Twitter (X)"},
    "lf": {"name": "تيك توك TikTok", "code": "lf", "short": "TikTok"},
    "go": {"name": "جوجل Google / Gmail", "code": "go", "short": "Google"},
    "sn": {"name": "سناب شات Snapchat", "code": "fu", "short": "Snapchat"},
    "hj": {"name": "حراج Haraj", "code": "au", "short": "Haraj"},
    "im": {"name": "إيمو IMO", "code": "im", "short": "IMO"},
    "pp": {"name": "بايبال PayPal", "code": "ts", "short": "PayPal"},
    "vi": {"name": "فايبر Viber", "code": "vi", "short": "Viber"},
    "ot": {"name": "أي تطبيق آخر", "code": "ot", "short": "Any Other"}
}

# ==========================================
# السيرفرات الثلاثة المميزة
# ==========================================

SERVERS = {
    "s1": {
        "title": "🌟 السيرفر الملكي VIP (أعلى جودة وسرعة)",
        "multiplier": 1.25,
        "badge": "VIP"
    },
    "s2": {
        "title": "⚡ السيرفر السريع الاقتصادي (أفضل سعر)",
        "multiplier": 1.0,
        "badge": "ECO"
    },
    "s3": {
        "title": "🎯 السيرفر الاحتياطي الشامل (أكثر توفراً)",
        "multiplier": 1.15,
        "badge": "PRO"
    }
}

# ==========================================
# قاعدة بيانات شاملة لكافة دول العالم
# ==========================================

COUNTRIES = {
    "73": {"name": "brazil", "title": "البرازيل", "flag": "🇧🇷", "prefix": "+55", "base_usd": 1.20},
    "0": {"name": "russia", "title": "روسيا", "flag": "🇷🇺", "prefix": "+7", "base_usd": 0.50},
    "6": {"name": "indonesia", "title": "إندونيسيا", "flag": "🇮🇩", "prefix": "+62", "base_usd": 0.45},
    "2": {"name": "kazakhstan", "title": "كازاخستان", "flag": "🇰🇿", "prefix": "+77", "base_usd": 0.65},
    "187": {"name": "usa", "title": "أمريكا", "flag": "🇺🇸", "prefix": "+1", "base_usd": 1.00},
    "16": {"name": "england", "title": "بريطانيا", "flag": "🇬🇧", "prefix": "+44", "base_usd": 0.95},
    "21": {"name": "egypt", "title": "مصر", "flag": "🇪🇬", "prefix": "+20", "base_usd": 0.80},
    "22": {"name": "india", "title": "الهند", "flag": "🇮🇳", "prefix": "+91", "base_usd": 0.35},
    "15": {"name": "poland", "title": "بولندا", "flag": "🇵🇱", "prefix": "+48", "base_usd": 0.85},
    "36": {"name": "canada", "title": "كندا", "flag": "🇨🇦", "prefix": "+1", "base_usd": 1.10},
    "56": {"name": "spain", "title": "إسبانيا", "flag": "🇪🇸", "prefix": "+34", "base_usd": 1.05},
    "32": {"name": "romania", "title": "رومانيا", "flag": "🇷🇴", "prefix": "+40", "base_usd": 0.75},
    "48": {"name": "netherlands", "title": "هولندا", "flag": "🇳🇱", "prefix": "+31", "base_usd": 1.20},
    "13": {"name": "germany", "title": "ألمانيا", "flag": "🇩🇪", "prefix": "+49", "base_usd": 1.30},
    "86": {"name": "italy", "title": "إيطاليا", "flag": "🇮🇹", "prefix": "+39", "base_usd": 1.15},
    "78": {"name": "france", "title": "فرنسا", "flag": "🇫🇷", "prefix": "+33", "base_usd": 1.25},
    "60": {"name": "turkey", "title": "تركيا", "flag": "🇹🇷", "prefix": "+90", "base_usd": 0.95},
    "53": {"name": "saudi", "title": "السعودية", "flag": "🇸🇦", "prefix": "+966", "base_usd": 1.50},
    "54": {"name": "yemen", "title": "اليمن", "flag": "🇾🇪", "prefix": "+967", "base_usd": 1.40},
    "95": {"name": "uae", "title": "الإمارات", "flag": "🇦🇪", "prefix": "+971", "base_usd": 1.60},
    "52": {"name": "iraq", "title": "العراق", "flag": "🇮🇶", "prefix": "+964", "base_usd": 0.90},
    "116": {"name": "jordan", "title": "الأردن", "flag": "🇯🇴", "prefix": "+962", "base_usd": 1.10},
    "117": {"name": "kuwait", "title": "الكويت", "flag": "🇰🇼", "prefix": "+965", "base_usd": 1.55},
    "102": {"name": "morocco", "title": "المغرب", "flag": "🇲🇦", "prefix": "+212", "base_usd": 0.85},
    "58": {"name": "algeria", "title": "الجزائر", "flag": "🇩🇿", "prefix": "+213", "base_usd": 0.80},
    "89": {"name": "tunisia", "title": "تونس", "flag": "🇹🇳", "prefix": "+216", "base_usd": 0.85},
    "148": {"name": "oman", "title": "عمان", "flag": "🇴🇲", "prefix": "+968", "base_usd": 1.45},
    "145": {"name": "bahrain", "title": "البحرين", "flag": "🇧🇭", "prefix": "+973", "base_usd": 1.40},
    "111": {"name": "qatar", "title": "قطر", "flag": "🇶🇦", "prefix": "+974", "base_usd": 1.65},
    "110": {"name": "syria", "title": "سوريا", "flag": "🇸🇾", "prefix": "+963", "base_usd": 1.20},
    "107": {"name": "lebanon", "title": "لبنان", "flag": "🇱🇧", "prefix": "+961", "base_usd": 1.15},
    "114": {"name": "sudan", "title": "السودان", "flag": "🇸🇩", "prefix": "+249", "base_usd": 0.90},
    "108": {"name": "libya", "title": "ليبيا", "flag": "🇱🇾", "prefix": "+218", "base_usd": 1.00},
    "146": {"name": "palestine", "title": "فلسطين", "flag": "🇵🇸", "prefix": "+970", "base_usd": 1.30},
    "1": {"name": "ukraine", "title": "أوكرانيا", "flag": "🇺🇦", "prefix": "+380", "base_usd": 0.60},
    "4": {"name": "philippines", "title": "الفلبين", "flag": "🇵🇭", "prefix": "+63", "base_usd": 0.50},
    "5": {"name": "myanmar", "title": "ميانمار", "flag": "🇲🇲", "prefix": "+95", "base_usd": 0.45},
    "7": {"name": "malaysia", "title": "ماليزيا", "flag": "🇲🇾", "prefix": "+60", "base_usd": 0.70},
    "10": {"name": "vietnam", "title": "فيتنام", "flag": "🇻🇳", "prefix": "+84", "base_usd": 0.55},
    "11": {"name": "kyrgyzstan", "title": "قيرغيزستان", "flag": "🇰🇬", "prefix": "+996", "base_usd": 0.60},
    "14": {"name": "israel", "title": "إسرائيل", "flag": "🇮🇱", "prefix": "+972", "base_usd": 1.10},
    "17": {"name": "nigeria", "title": "نيجيريا", "flag": "🇳🇬", "prefix": "+234", "base_usd": 0.40},
    "19": {"name": "uzbekistan", "title": "أوزبكستان", "flag": "🇺🇿", "prefix": "+998", "base_usd": 0.65},
    "24": {"name": "cambodia", "title": "كمبوديا", "flag": "🇰🇭", "prefix": "+855", "base_usd": 0.50},
    "31": {"name": "southafrica", "title": "جنوب إفريقيا", "flag": "🇿🇦", "prefix": "+27", "base_usd": 0.75},
    "33": {"name": "colombia", "title": "كولومبيا", "flag": "🇨🇴", "prefix": "+57", "base_usd": 0.70},
    "38": {"name": "pakistan", "title": "باكستان", "flag": "🇵🇰", "prefix": "+92", "base_usd": 0.55},
    "40": {"name": "bangladesh", "title": "بنغلاديش", "flag": "🇧🇩", "prefix": "+880", "base_usd": 0.40},
    "43": {"name": "czech", "title": "التشيك", "flag": "🇨🇿", "prefix": "+420", "base_usd": 0.85},
    "44": {"name": "srilanka", "title": "سريلانكا", "flag": "🇱🇰", "prefix": "+94", "base_usd": 0.50},
    "46": {"name": "sweden", "title": "السويد", "flag": "🇸🇪", "prefix": "+46", "base_usd": 1.20},
    "51": {"name": "thailand", "title": "تايلاند", "flag": "🇹🇭", "prefix": "+66", "base_usd": 0.65},
    "55": {"name": "mexico", "title": "المكسيك", "flag": "🇲🇽", "prefix": "+52", "base_usd": 0.90},
    "62": {"name": "peru", "title": "بيرو", "flag": "🇵🇪", "prefix": "+51", "base_usd": 0.75},
    "67": {"name": "argentina", "title": "الأرجنتين", "flag": "🇦🇷", "prefix": "+54", "base_usd": 0.85},
    "77": {"name": "austria", "title": "النمسا", "flag": "🇦🇹", "prefix": "+43", "base_usd": 1.25},
    "80": {"name": "switzerland", "title": "سويسرا", "flag": "🇨🇭", "prefix": "+41", "base_usd": 1.50},
    "82": {"name": "belgium", "title": "بلجيكا", "flag": "🇧🇪", "prefix": "+32", "base_usd": 1.20},
    "83": {"name": "bulgaria", "title": "بلغاريا", "flag": "🇧🇬", "prefix": "+359", "base_usd": 0.80},
    "84": {"name": "hungary", "title": "المجر", "flag": "🇭🇺", "prefix": "+36", "base_usd": 0.85},
    "87": {"name": "chile", "title": "تشيلي", "flag": "🇨🇱", "prefix": "+56", "base_usd": 0.90},
    "90": {"name": "portugal", "title": "البرتغال", "flag": "🇵🇹", "prefix": "+351", "base_usd": 1.05},
    "94": {"name": "georgia", "title": "جورجيا", "flag": "🇬🇪", "prefix": "+995", "base_usd": 0.80},
    "100": {"name": "greece", "title": "اليونان", "flag": "🇬🇷", "prefix": "+30", "base_usd": 1.10}
}