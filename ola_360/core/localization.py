from __future__ import annotations


TEXT = {
    "en": {
        "home": "Home",
        "radar": "Radar",
        "meetings": "Meetings",
        "ai": "AI",
        "my_day": "My Day",
        "login": "Secure sign-in",
        "notifications": "Notifications",
        "language": "Language",
        "theme": "Theme",
    },
    "ar": {
        "home": "الرئيسية",
        "radar": "الرادار",
        "meetings": "الاجتماعات",
        "ai": "الذكاء",
        "my_day": "يومي",
        "login": "دخول آمن",
        "notifications": "الإشعارات",
        "language": "اللغة",
        "theme": "المظهر",
    },
}


def tr(key: str, language: str = "en") -> str:
    return TEXT.get(language, TEXT["en"]).get(key, key)


def is_rtl(language: str) -> bool:
    return language == "ar"
