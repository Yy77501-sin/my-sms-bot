# ==========================================
# كتالوج الخدمات والتطبيقات المدعومة
# ==========================================

SERVICES = {
    "wa": {"name": "واتساب WhatsApp", "code": "wa", "fivesim_code": "whatsapp", "short": "WhatsApp"},
    "tg": {"name": "تيليجرام Telegram", "code": "tg", "fivesim_code": "telegram", "short": "Telegram"},
    "ig": {"name": "إنستغرام Instagram", "code": "ig", "fivesim_code": "instagram", "short": "Instagram"},
    "fb": {"name": "فيسبوك Facebook", "code": "fb", "fivesim_code": "facebook", "short": "Facebook"},
    "tw": {"name": "تويتر / X", "code": "tw", "fivesim_code": "twitter", "short": "Twitter (X)"},
    "lf": {"name": "تيك توك TikTok", "code": "lf", "fivesim_code": "tiktok", "short": "TikTok"},
    "go": {"name": "جوجل Google / Gmail", "code": "go", "fivesim_code": "google", "short": "Google"},
    "sn": {"name": "سناب شات Snapchat", "code": "fu", "fivesim_code": "snapchat", "short": "Snapchat"},
    "hj": {"name": "حراج Haraj", "code": "au", "fivesim_code": "haraj", "short": "Haraj"},
    "im": {"name": "إيمو IMO", "code": "im", "fivesim_code": "imo", "short": "IMO"},
    "pp": {"name": "بايبال PayPal", "code": "ts", "fivesim_code": "paypal", "short": "PayPal"},
    "vi": {"name": "فايبر Viber", "code": "vi", "fivesim_code": "viber", "short": "Viber"},
    "ot": {"name": "أي تطبيق آخر", "code": "ot", "fivesim_code": "other", "short": "Any Other"}
}

# ==========================================
# السيرفرات الأربعة المعتمدة
# ==========================================

SERVERS = {
    "s1": {
        "title": "⚡ السيرفر (1) 5SIM العالمي (الأرخص)",
        "provider": "fivesim",
        "badge": "5SIM"
    },
    "s2": {
        "title": "🐻 السيرفر (2) Grizzly SMS (أسرع وصول)",
        "provider": "grizzly",
        "badge": "GRIZZLY"
    },
    "s3": {
        "title": "🌟 السيرفر (3) Hero SMS (الأكثر تنوعاً)",
        "provider": "hero",
        "badge": "HERO"
    },
    "s4": {
        "title": "💎 السيرفر (4) Plus SMS (الاقتصادي)",
        "provider": "plus",
        "badge": "PLUS"
    }
}

# ==========================================
# قاعدة بيانات الدول الشاملة
# ==========================================

COUNTRIES = {
    "54": {"name": "yemen", "title": "اليمن", "flag": "🇾🇪", "prefix": "967", "default_rub": 35.0},
    "53": {"name": "saudi", "title": "السعودية", "flag": "🇸🇦", "prefix": "966", "default_rub": 40.0},
    "21": {"name": "egypt", "title": "مصر", "flag": "🇪🇬", "prefix": "20", "default_rub": 20.0},
    "73": {"name": "brazil", "title": "البرازيل", "flag": "🇧🇷", "prefix": "55", "default_rub": 30.0},
    "0": {"name": "russia", "title": "روسيا", "flag": "🇷🇺", "prefix": "7", "default_rub": 15.0},
    "187": {"name": "usa", "title": "أمريكا", "flag": "🇺🇸", "prefix": "1", "default_rub": 25.0},
    "16": {"name": "england", "title": "بريطانيا", "flag": "🇬🇧", "prefix": "44", "default_rub": 22.0},
    "6": {"name": "indonesia", "title": "إندونيسيا", "flag": "🇮🇩", "prefix": "62", "default_rub": 12.0},
    "2": {"name": "kazakhstan", "title": "كازاخستان", "flag": "🇰🇿", "prefix": "77", "default_rub": 18.0},
    "95": {"name": "uae", "title": "الإمارات", "flag": "🇦🇪", "prefix": "971", "default_rub": 40.0},
    "52": {"name": "iraq", "title": "العراق", "flag": "🇮🇶", "prefix": "964", "default_rub": 22.0},
    "116": {"name": "jordan", "title": "الأردن", "flag": "🇯🇴", "prefix": "962", "default_rub": 25.0},
    "117": {"name": "kuwait", "title": "الكويت", "flag": "🇰🇼", "prefix": "965", "default_rub": 38.0},
    "102": {"name": "morocco", "title": "المغرب", "flag": "🇲🇦", "prefix": "212", "default_rub": 20.0},
    "58": {"name": "algeria", "title": "الجزائر", "flag": "🇩🇿", "prefix": "213", "default_rub": 18.0},
    "89": {"name": "tunisia", "title": "تونس", "flag": "🇹🇳", "prefix": "216", "default_rub": 20.0},
    "148": {"name": "oman", "title": "عمان", "flag": "🇴🇲", "prefix": "968", "default_rub": 35.0},
    "145": {"name": "bahrain", "title": "البحرين", "flag": "🇧🇭", "prefix": "973", "default_rub": 35.0},
    "111": {"name": "qatar", "title": "قطر", "flag": "🇶🇦", "prefix": "974", "default_rub": 40.0},
    "110": {"name": "syria", "title": "سوريا", "flag": "🇸🇾", "prefix": "963", "default_rub": 28.0},
    "107": {"name": "lebanon", "title": "لبنان", "flag": "🇱🇧", "prefix": "961", "default_rub": 26.0},
    "114": {"name": "sudan", "title": "السودان", "flag": "🇸🇩", "prefix": "249", "default_rub": 20.0},
    "108": {"name": "libya", "title": "ليبيا", "flag": "🇱🇾", "prefix": "218", "default_rub": 24.0},
    "146": {"name": "palestine", "title": "فلسطين", "flag": "🇵🇸", "prefix": "970", "default_rub": 30.0},
    "22": {"name": "india", "title": "الهند", "flag": "🇮🇳", "prefix": "91", "default_rub": 10.0},
    "15": {"name": "poland", "title": "بولندا", "flag": "🇵🇱", "prefix": "48", "default_rub": 22.0},
    "36": {"name": "canada", "title": "كندا", "flag": "🇨🇦", "prefix": "1", "default_rub": 28.0},
    "56": {"name": "spain", "title": "إسبانيا", "flag": "🇪🇸", "prefix": "34", "default_rub": 25.0},
    "32": {"name": "romania", "title": "رومانيا", "flag": "🇷🇴", "prefix": "40", "default_rub": 18.0},
    "48": {"name": "netherlands", "title": "هولندا", "flag": "🇳🇱", "prefix": "31", "default_rub": 30.0},
    "13": {"name": "germany", "title": "ألمانيا", "flag": "🇩🇪", "prefix": "49", "default_rub": 32.0},
    "86": {"name": "italy", "title": "إيطاليا", "flag": "🇮🇹", "prefix": "39", "default_rub": 28.0},
    "78": {"name": "france", "title": "فرنسا", "flag": "🇫🇷", "prefix": "33", "default_rub": 30.0},
    "60": {"name": "turkey", "title": "تركيا", "flag": "🇹🇷", "prefix": "90", "default_rub": 24.0},
    "1": {"name": "ukraine", "title": "أوكرانيا", "flag": "🇺🇦", "prefix": "380", "default_rub": 16.0},
    "4": {"name": "philippines", "title": "الفلبين", "flag": "🇵🇭", "prefix": "63", "default_rub": 14.0},
    "5": {"name": "myanmar", "title": "ميانمار", "flag": "🇲🇲", "prefix": "95", "default_rub": 12.0},
    "7": {"name": "malaysia", "title": "ماليزيا", "flag": "🇲🇾", "prefix": "60", "default_rub": 18.0},
    "10": {"name": "vietnam", "title": "فيتنام", "flag": "🇻🇳", "prefix": "84", "default_rub": 14.0},
    "11": {"name": "kyrgyzstan", "title": "قيرغيزستان", "flag": "🇰🇬", "prefix": "996", "default_rub": 16.0},
    "17": {"name": "nigeria", "title": "نيجيريا", "flag": "🇳🇬", "prefix": "234", "default_rub": 12.0},
    "19": {"name": "uzbekistan", "title": "أوزبكستان", "flag": "🇺🇿", "prefix": "998", "default_rub": 18.0},
    "24": {"name": "cambodia", "title": "كمبوديا", "flag": "🇰🇭", "prefix": "855", "default_rub": 14.0},
    "31": {"name": "southafrica", "title": "جنوب إفريقيا", "flag": "🇿🇦", "prefix": "27", "default_rub": 18.0},
    "33": {"name": "colombia", "title": "كولومبيا", "flag": "🇨🇴", "prefix": "57", "default_rub": 18.0},
    "38": {"name": "pakistan", "title": "باكستان", "flag": "🇵🇰", "prefix": "92", "default_rub": 14.0},
    "40": {"name": "bangladesh", "title": "بنغلاديش", "flag": "🇧🇩", "prefix": "880", "default_rub": 12.0},
    "43": {"name": "czech", "title": "التشيك", "flag": "🇨🇿", "prefix": "420", "default_rub": 22.0},
    "44": {"name": "srilanka", "title": "سريلانكا", "flag": "🇱🇰", "prefix": "94", "default_rub": 14.0},
    "46": {"name": "sweden", "title": "السويد", "flag": "🇸🇪", "prefix": "46", "default_rub": 30.0},
    "51": {"name": "thailand", "title": "تايلاند", "flag": "🇹🇭", "prefix": "66", "default_rub": 16.0},
    "55": {"name": "mexico", "title": "المكسيك", "flag": "🇲🇽", "prefix": "52", "default_rub": 24.0},
    "62": {"name": "peru", "title": "بيرو", "flag": "🇵🇪", "prefix": "51", "default_rub": 18.0},
    "67": {"name": "argentina", "title": "الأرجنتين", "flag": "🇦🇷", "prefix": "54", "default_rub": 20.0},
    "77": {"name": "austria", "title": "النمسا", "flag": "🇦🇹", "prefix": "43", "default_rub": 30.0},
    "80": {"name": "switzerland", "title": "سويسرا", "flag": "🇨🇭", "prefix": "41", "default_rub": 35.0},
    "82": {"name": "belgium", "title": "بلجيكا", "flag": "🇧🇪", "prefix": "32", "default_rub": 28.0},
    "83": {"name": "bulgaria", "title": "بلغاريا", "flag": "🇧🇬", "prefix": "359", "default_rub": 18.0},
    "84": {"name": "hungary", "title": "المجر", "flag": "🇭🇺", "prefix": "36", "default_rub": 20.0},
    "87": {"name": "chile", "title": "تشيلي", "flag": "🇨🇱", "prefix": "56", "default_rub": 22.0},
    "90": {"name": "portugal", "title": "البرتغال", "flag": "🇵🇹", "prefix": "351", "default_rub": 26.0},
    "94": {"name": "georgia", "title": "جورجيا", "flag": "🇬🇪", "prefix": "995", "default_rub": 18.0},
    "100": {"name": "greece", "title": "اليونان", "flag": "🇬🇷", "prefix": "30", "default_rub": 26.0}
}

# ==========================================
# خدمات الرشق وشحن الألعاب
# ==========================================

SMM_SERVICES = {
    "tg_members": {
        "title": "✈️ أعضاء قنوات ومجموعات تليجرام (1000 عضو)",
        "cost_usd": 1.20,
        "cost_rub": 36.0,
        "desc": "أعضاء حقيقيين وسريعين لرفع قناة أو مجموعة التليجرام."
    },
    "tg_views": {
        "title": "👁️ مشاهدات منشورات تليجرام (1000 مشاهدة)",
        "cost_usd": 0.20,
        "cost_rub": 6.0,
        "desc": "مشاهدات فورية وسريعة لآخر المنشورات."
    },
    "ig_followers": {
        "title": "📸 متابعين إنستغرام ضمان 30 يوم (1000 متابع)",
        "cost_usd": 1.50,
        "cost_rub": 45.0,
        "desc": "متابعين حسابات مميزة مع ضمان تعويض النقص."
    },
    "ig_likes": {
        "title": "❤️ لايكات إنستغرام سريعة (1000 لايك)",
        "cost_usd": 0.40,
        "cost_rub": 12.0,
        "desc": "لايكات فورية لجميع منشوراتك وصورك."
    },
    "tk_followers": {
        "title": "🎥 متابعين تيك توك فوري (1000 متابع)",
        "cost_usd": 2.00,
        "cost_rub": 60.0,
        "desc": "لفتح البث المباشر وزيادة تفاعل الحساب."
    },
    "tk_views": {
        "title": "🔥 مشاهدات تيك توك سريعة (5000 مشاهدة)",
        "cost_usd": 0.30,
        "cost_rub": 9.0,
        "desc": "لدخول مقاطعك إلى إكسبلور."
    },
    "pubg_60": {
        "title": "🎮 شدات ببجي PUBG (60 UC)",
        "cost_usd": 1.10,
        "cost_rub": 33.0,
        "desc": "شحن مباشر وسريع عبر الآيدي ID."
    },
    "pubg_325": {
        "title": "🎮 شدات ببجي PUBG (325 UC + هدية)",
        "cost_usd": 5.20,
        "cost_rub": 156.0,
        "desc": "شحن رويال باس والمواسم عبر الآيدي."
    },
    "ff_100": {
        "title": "💎 جواهر فري فاير Free Fire (110 جوهرة)",
        "cost_usd": 1.15,
        "cost_rub": 34.5,
        "desc": "شحن فوري ومباشر بالمعرف Player ID."
    }
}