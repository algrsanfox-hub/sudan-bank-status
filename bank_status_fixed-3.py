import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import time
import socket
import os
from datetime import datetime


# =========================================================
# الإعدادات
# =========================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    import getpass
    BOT_TOKEN = getpass.getpass("أدخل رمز بوت Telegram: ").strip()
if not BOT_TOKEN:
    raise RuntimeError("لم يتم توفير BOT_TOKEN")

CHANNEL = "@ourplanetx"

URL = "https://status.sd/"

IMAGE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "bank_status.png"
)

# 10 دقائق
INTERVAL = 600

# العنوان الذي يعمل مع status.sd عندك
WORKING_IP = "172.67.202.215"


# =========================================================
# إجبار status.sd على الاتصال عبر IPv4
# =========================================================

_original_getaddrinfo = socket.getaddrinfo


def custom_getaddrinfo(
    host,
    port,
    family=0,
    type=0,
    proto=0,
    flags=0
):

    if host == "status.sd":

        return [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                (WORKING_IP, port)
            )
        ]

    return _original_getaddrinfo(
        host,
        port,
        family,
        type,
        proto,
        flags
    )


socket.getaddrinfo = custom_getaddrinfo


# =========================================================
# الخطوط
# =========================================================

# مسارات الخطوط تختلف بين Android (Termux) وLinux (GitHub Actions).
ARABIC_REGULAR_CANDIDATES = [
    "/system/fonts/NotoNaskhArabic-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoNaskhArabicUI-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
ARABIC_BOLD_CANDIDATES = [
    "/system/fonts/NotoNaskhArabic-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoNaskhArabicUI-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
LATIN_CANDIDATES = [
    "/system/fonts/DroidSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def load_first_font(paths, size):
    for path in paths:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except (OSError, IOError):
                pass
    raise RuntimeError(
        "لم يتم العثور على خط مناسب. ثبّت fonts-noto-core على Linux "
        "أو استخدم خطوط Noto في Android."
    )


def get_arabic_font(size, bold=False):
    paths = ARABIC_BOLD_CANDIDATES if bold else ARABIC_REGULAR_CANDIDATES
    return load_first_font(paths, size)


def get_latin_font(size):
    return load_first_font(LATIN_CANDIDATES, size)


# =========================================================
# معالجة النص العربي
# =========================================================

def ar(text):

    if text is None:
        return ""

    text = str(text)

    reshaped = arabic_reshaper.reshape(
        text
    )

    return get_display(
        reshaped
    )


# =========================================================
# تنظيف الاسم
# =========================================================

def clean_name(name):

    if not name:
        return ""

    name = str(name).strip()

    # إزالة الرموز التي كانت تظهر كمربعات
    for ch in [
        "□",
        "▪",
        "•",
        "■",
        "◆",
        "◇",
        "▢",
        "▣"
    ]:
        name = name.replace(ch, "")

    # إزالة الفواصل والشرطات
    name = name.replace("—", " ")
    name = name.replace("–", " ")
    name = name.replace("-", " ")
    name = name.replace("|", " ")

    # مسافات متكررة
    name = " ".join(
        name.split()
    )

    return name.strip()


# =========================================================
# رسم النص العربي بمحاذاة اليمين
# =========================================================

def draw_arabic_right(
    draw,
    text,
    right_x,
    y,
    font,
    fill
):

    visual = ar(text)

    bbox = draw.textbbox(
        (0, 0),
        visual,
        font=font
    )

    width = bbox[2] - bbox[0]

    draw.text(
        (
            right_x - width,
            y
        ),
        visual,
        font=font,
        fill=fill
    )


# =========================================================
# رسم اسم البنك
# =========================================================

def draw_bank_name(
    draw,
    original_name,
    right_x,
    y,
    title_font,
    subtitle_font,
    latin_font
):

    name = clean_name(
        original_name
    )

    # -----------------------------------------------------
    # بنكك
    # -----------------------------------------------------

    if (
        "بنكك" in name
        and "الخرطوم" in name
    ):

        draw_arabic_right(
            draw,
            "بنكك",
            right_x,
            y,
            title_font,
            (15, 15, 15)
        )

        draw_arabic_right(
            draw,
            "بنك الخرطوم",
            right_x,
            y + 47,
            subtitle_font,
            (85, 85, 85)
        )

        return


    # -----------------------------------------------------
    # فوري
    # -----------------------------------------------------

    if (
        "فوري" in name
        and "فيصل" in name
    ):

        draw_arabic_right(
            draw,
            "فوري",
            right_x,
            y,
            title_font,
            (15, 15, 15)
        )

        draw_arabic_right(
            draw,
            "بنك فيصل",
            right_x,
            y + 47,
            subtitle_font,
            (85, 85, 85)
        )

        return


    # -----------------------------------------------------
    # أوكاش
    # -----------------------------------------------------

    if (
        "أوكاش" in name
        and "أمدرمان" in name
    ):

        draw_arabic_right(
            draw,
            "أوكاش",
            right_x,
            y,
            title_font,
            (15, 15, 15)
        )

        draw_arabic_right(
            draw,
            "بنك أمدرمان الوطني",
            right_x,
            y + 47,
            subtitle_font,
            (85, 85, 85)
        )

        return


    # -----------------------------------------------------
    # البركة
    # -----------------------------------------------------

    if "البركة" in name:

        draw_arabic_right(
            draw,
            "البركة",
            right_x,
            y,
            title_font,
            (15, 15, 15)
        )

        return


    # -----------------------------------------------------
    # ماي كاشي
    # -----------------------------------------------------

    if "ماي كاشي" in name:

        draw_arabic_right(
            draw,
            "ماي كاشي",
            right_x,
            y,
            title_font,
            (15, 15, 15)
        )

        # Cashi باللغة الإنجليزية
        draw.text(
            (
                right_x,
                y + 48
            ),
            "Cashi",
            font=latin_font,
            fill=(85, 85, 85),
            anchor="ra"
        )

        return


    # -----------------------------------------------------
    # مصرف النيل الأزرق
    # -----------------------------------------------------

    if (
        "النيل الأزرق" in name
        or "النيل الازرق" in name
    ):

        draw_arabic_right(
            draw,
            "مصرف النيل الأزرق",
            right_x,
            y + 20,
            title_font,
            (15, 15, 15)
        )

        return


    # -----------------------------------------------------
    # البنك الإسلامي السوداني
    # -----------------------------------------------------

    if "الإسلامي السوداني" in name:

        draw_arabic_right(
            draw,
            "البنك الإسلامي السوداني",
            right_x,
            y + 20,
            title_font,
            (15, 15, 15)
        )

        return


    # -----------------------------------------------------
    # أي بنك آخر
    # -----------------------------------------------------

    draw_arabic_right(
        draw,
        name,
        right_x,
        y + 20,
        title_font,
        (15, 15, 15)
    )


# =========================================================
# توحيد حالة الخدمة
# =========================================================

def normalize_status(status):

    if not status:
        return "غير معروف"

    status = str(status).strip()

    if "متذبذب" in status:
        return "متذبذب"

    if "متوقف" in status:
        return "متوقف"

    if "يعمل" in status:
        return "يعمل"

    if "متاح" in status:
        return "يعمل"

    return "غير معروف"


# =========================================================
# لون الحالة
# =========================================================

def get_status_color(status):

    status = normalize_status(
        status
    )

    if status == "يعمل":
        return (35, 175, 85)

    if status == "متذبذب":
        return (235, 170, 20)

    if status == "متوقف":
        return (220, 60, 60)

    return (140, 140, 140)


# =========================================================
# رسم حالة Android / iPhone
# =========================================================

def draw_status(
    draw,
    label,
    status,
    right_x,
    y,
    font
):

    status = normalize_status(
        status
    )

    color = get_status_color(
        status
    )

    text = (
        label
        + ": "
        + status
    )

    visual = ar(text)

    bbox = draw.textbbox(
        (0, 0),
        visual,
        font=font
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    # النص
    text_x = (
        right_x
        - text_width
        - 24
    )

    draw.text(
        (
            text_x,
            y
        ),
        visual,
        font=font,
        fill=(50, 50, 50)
    )

    # الدائرة الملونة
    center_x = (
        text_x
        + text_width
        + 10
    )

    center_y = (
        y + 17
    )

    radius = 9

    draw.ellipse(
        (
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius
        ),
        fill=color
    )


# =========================================================
# تحميل الصفحة
# =========================================================

def get_page():

    headers = {
        "User-Agent":
            "Mozilla/5.0 "
            "(Linux; Android 13) "
            "AppleWebKit/537.36 "
            "Chrome/120.0 Mobile Safari/537.36"
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.text


# =========================================================
# استخراج بيانات البنوك
# =========================================================

def extract_banks(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    banks = []

    cards = soup.select(
        "article.bank-card"
    )

    for card in cards:

        title = card.select_one(
            "h3"
        )

        if not title:
            continue

        bank_name = title.get_text(
            " ",
            strip=True
        )

        android = "غير معروف"
        iphone = "غير معروف"

        rows = card.select(
            "li.service-row"
        )

        for row in rows:

            service_element = row.select_one(
                "span.min-w-0.flex-1"
            )

            status_element = row.select_one(
                "span.sr-only"
            )

            if not service_element:
                continue

            service_name = service_element.get_text(
                " ",
                strip=True
            )

            status = "غير معروف"

            if status_element:

                status = status_element.get_text(
                    " ",
                    strip=True
                )

            if "أندرويد" in service_name:

                android = normalize_status(
                    status
                )

            elif "آيفون" in service_name:

                iphone = normalize_status(
                    status
                )

        banks.append(
            {
                "name": bank_name,
                "android": android,
                "iphone": iphone
            }
        )

    return banks


# =========================================================
# إنشاء الصورة
# =========================================================

def create_image(banks):

    width = 1080

    # البطاقة أصبحت أطول لمنع التداخل
    card_height = 180

    top_space = 255

    bottom_space = 105

    height = (
        top_space
        + len(banks) * card_height
        + bottom_space
    )

    image = Image.new(
        "RGB",
        (
            width,
            height
        ),
        "white"
    )

    draw = ImageDraw.Draw(
        image
    )


    # -----------------------------------------------------
    # الخطوط
    # -----------------------------------------------------

    title_font = get_arabic_font(
        58,
        True
    )

    bank_title_font = get_arabic_font(
        40,
        True
    )

    bank_subtitle_font = get_arabic_font(
        28,
        False
    )

    status_font = get_arabic_font(
        28,
        False
    )

    source_font = get_arabic_font(
        27,
        False
    )

    footer_font = get_arabic_font(
        25,
        False
    )

    latin_font = get_latin_font(
        27
    )


    # -----------------------------------------------------
    # العنوان
    # -----------------------------------------------------

    title = "حالة الخدمات المصرفية في السودان"

    title_visual = ar(title)

    bbox = draw.textbbox(
        (0, 0),
        title_visual,
        font=title_font
    )

    title_width = (
        bbox[2] - bbox[0]
    )

    draw.text(
        (
            (width - title_width) // 2,
            18
        ),
        title_visual,
        font=title_font,
        fill=(15, 15, 15)
    )


    # -----------------------------------------------------
    # المصدر
    # -----------------------------------------------------

    source_ar = "المصدر:"

    source_visual = ar(
        source_ar
    )

    bbox = draw.textbbox(
        (0, 0),
        source_visual,
        font=source_font
    )

    source_width = (
        bbox[2] - bbox[0]
    )

    source_en = "status.sd"

    bbox2 = draw.textbbox(
        (0, 0),
        source_en,
        font=latin_font
    )

    source_en_width = (
        bbox2[2] - bbox2[0]
    )

    total_source_width = (
        source_width
        + source_en_width
        + 15
    )

    source_x = (
        width - total_source_width
    ) // 2

    draw.text(
        (
            source_x,
            92
        ),
        source_visual,
        font=source_font,
        fill=(105, 105, 105)
    )

    draw.text(
        (
            source_x
            + source_width
            + 15,
            96
        ),
        source_en,
        font=latin_font,
        fill=(105, 105, 105)
    )


    # -----------------------------------------------------
    # وقت التحديث
    # -----------------------------------------------------

    current_time = datetime.now().strftime(
        "%H:%M"
    )

    update_text = (
        "آخر تحديث: "
        + current_time
    )

    draw_arabic_right(
        draw,
        update_text,
        width - 40,
        135,
        source_font,
        (120, 120, 120)
    )


    # -----------------------------------------------------
    # الخط الفاصل
    # -----------------------------------------------------

    draw.line(
        (
            40,
            180,
            width - 40,
            180
        ),
        fill=(205, 205, 205),
        width=3
    )


    # -----------------------------------------------------
    # البطاقات
    # -----------------------------------------------------

    y = 200

    for bank in banks:

        left = 35
        right = width - 35

        top = y
        bottom = y + 155


        # البطاقة
        draw.rounded_rectangle(
            (
                left,
                top,
                right,
                bottom
            ),
            radius=22,
            fill=(249, 249, 249),
            outline=(205, 205, 205),
            width=3
        )


        # -----------------------------------------------
        # اسم البنك
        # -----------------------------------------------

        draw_bank_name(
            draw,
            bank["name"],
            width - 65,
            y + 12,
            bank_title_font,
            bank_subtitle_font,
            latin_font
        )


        # -----------------------------------------------
        # Android
        # -----------------------------------------------

        draw_status(
            draw,
            "أندرويد",
            bank["android"],
            width - 65,
            y + 110,
            status_font
        )


        # -----------------------------------------------
        # iPhone
        # -----------------------------------------------

        draw_status(
            draw,
            "آيفون",
            bank["iphone"],
            545,
            y + 110,
            status_font
        )


        y += card_height


    # -----------------------------------------------------
    # أسفل الصورة
    # -----------------------------------------------------

    footer = (
        "يتم تحديث الحالة تلقائيًا كل 10 دقائق"
    )

    footer_visual = ar(
        footer
    )

    bbox = draw.textbbox(
        (0, 0),
        footer_visual,
        font=footer_font
    )

    footer_width = (
        bbox[2] - bbox[0]
    )

    draw.text(
        (
            (width - footer_width) // 2,
            height - 65
        ),
        footer_visual,
        font=footer_font,
        fill=(110, 110, 110)
    )


    # -----------------------------------------------------
    # حفظ الصورة
    # -----------------------------------------------------

    image.save(
        IMAGE,
        "PNG"
    )

    print(
        "🖼️ تم إنشاء الصورة:",
        IMAGE
    )


# =========================================================
# إرسال الصورة إلى Telegram
# =========================================================

def send_photo():

    api_url = (
        "https://api.telegram.org/bot"
        + BOT_TOKEN
        + "/sendPhoto"
    )

    try:

        with open(
            IMAGE,
            "rb"
        ) as photo:

            response = requests.post(
                api_url,
                data={
                    "chat_id": CHANNEL,
                    "caption":
                        "تحديث حالة الخدمات المصرفية في السودان"
                },
                files={
                    "photo": photo
                },
                timeout=60
            )

        result = response.json()

        if result.get("ok"):

            print(
                "✅ تم إرسال الصورة إلى Telegram"
            )

        else:

            print(
                "❌ خطأ Telegram:"
            )

            print(result)

    except Exception as e:

        print(
            "❌ خطأ أثناء إرسال الصورة:"
        )

        print(e)


# =========================================================
# البرنامج الرئيسي
# =========================================================

def main():

    print(
        "========================================"
    )

    print(
        "       Sudan Banks Status Bot"
    )

    print(
        "========================================"
    )

    while True:

        try:

            print()
            print(
                "🔎 فحص status.sd ..."
            )

            html = get_page()

            banks = extract_banks(
                html
            )

            print(
                f"✅ تم العثور على {len(banks)} بنوك"
            )

            for bank in banks:

                print(
                    bank["name"],
                    "| Android:",
                    bank["android"],
                    "| iPhone:",
                    bank["iphone"]
                )

            if banks:

                create_image(
                    banks
                )

                send_photo()

        except Exception as e:

            print()
            print(
                "❌ حدث خطأ:"
            )

            print(e)

        print()
        print(
            "⏳ الانتظار 10 دقائق..."
        )

        time.sleep(
            INTERVAL
        )


# =========================================================
# بدء التشغيل
# =========================================================

if __name__ == "__main__":
    main()
