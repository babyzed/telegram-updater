#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from datetime import datetime
import pytz

# تنظیمات تلگرام
BOT_TOKEN = "8571806080:AAGYnD6E81QasC4eyiHZXVuKhucd6Ji_gKY"
CHAT_ID = "@ZeNOxnews"
MESSAGE_ID = 3

def gregorian_to_jalali(gy, gm, gd):
    """تبدیل تاریخ میلادی به شمسی"""
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    jm = 1 + (days // 31) if days < 186 else 7 + ((days - 186) // 30)
    jd = 1 + (days % 31 if days < 186 else (days - 186) % 30)
    return jy, jm, jd

def get_persian_date_time():
    """دریافت تاریخ و ساعت فارسی"""
    # تایم زون تهران
    tehran_tz = pytz.timezone('Asia/Tehran')
    now = datetime.now(tehran_tz)
    
    # تبدیل به شمسی
    jy, jm, jd = gregorian_to_jalali(now.year, now.month, now.day)
    
    # نام ماه‌ها و روزها
    persian_months = ['', 'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 
                      'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    persian_days = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
    
    day_name = persian_days[now.weekday()]
    month_name = persian_months[jm]
    
    # فرمت تاریخ و ساعت
    date_str = f"{day_name} {jd} {month_name} {jy}"
    time_str = now.strftime("%H:%M")
    
    return date_str, time_str

def get_prices():
    """دریافت قیمت طلا و دلار"""
    try:
        response = requests.get("https://call.tgju.online/ajax.json", timeout=10)
        data = response.json()
        
        # قیمت دلار
        dollar_data = data.get('current', {}).get('price_dollar_rl', {})
        dollar_price = dollar_data.get('p', 'نامشخص')
        dollar_change = float(dollar_data.get('d', 0))
        
        # قیمت طلای 18 عیار
        gold_data = data.get('current', {}).get('geram18', {})
        gold_price = gold_data.get('p', 'نامشخص')
        gold_change = float(gold_data.get('d', 0))
        
        # فرمت اعداد
        if dollar_price != 'نامشخص':
            dollar_price = f"{int(float(dollar_price)):,}".replace(',', '،')
        if gold_price != 'نامشخص':
            gold_price = f"{int(float(gold_price)):,}".replace(',', '،')
        
        # تعیین ایموجی
        dollar_emoji = '📈' if dollar_change > 0 else ('📉' if dollar_change < 0 else '➖')
        gold_emoji = '📈' if gold_change > 0 else ('📉' if gold_change < 0 else '➖')
        
        return {
            'dollar_price': dollar_price,
            'dollar_emoji': dollar_emoji,
            'gold_price': gold_price,
            'gold_emoji': gold_emoji
        }
    except Exception as e:
        print(f"خطا در دریافت قیمت‌ها: {e}")
        return {
            'dollar_price': 'نامشخص',
            'dollar_emoji': '❓',
            'gold_price': 'نامشخص',
            'gold_emoji': '❓'
        }

def update_telegram_message():
    """بروزرسانی پیام تلگرام"""
    try:
        # دریافت تاریخ و ساعت
        date_str, time_str = get_persian_date_time()
        
        # دریافت قیمت‌ها
        prices = get_prices()
        
        # ساخت متن پیام
        message = f"""🕐 ساعت: {time_str}
📅 تاریخ: {date_str}

💰 قیمت‌های لحظه‌ای:

💵 دلار: {prices['dollar_price']} تومان {prices['dollar_emoji']}

🪙 طلای ۱۸ عیار: {prices['gold_price']} تومان {prices['gold_emoji']}

🔄 بروزرسانی خودکار هر دقیقه
@ZeNOxnews"""
        
        # ارسال به تلگرام
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
        payload = {
            "chat_id": CHAT_ID,
            "message_id": MESSAGE_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ پیام با موفقیت بروزرسانی شد - {time_str}")
        else:
            print(f"❌ خطا: {response.text}")
            
    except Exception as e:
        print(f"❌ خطای کلی: {e}")

if __name__ == "__main__":
    update_telegram_message()
