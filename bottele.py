from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
import telegram.error
import logging

# تنظیمات لاگ‌گیری برای دیباگ بهتر
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# توکن ربات و اطلاعات کانال
TOKEN = "7506839682:AAGFvqSpQ-a9u16rainlBGljYXPggwNvQDg"
CHANNEL_ID = "@ariyahamrah_vpn"
CHANNEL_LINK = "https://t.me/ariyahamrah_vpn"
ADMIN_ID = 5664986825  # آیدی عددی مدیر
ADMIN_ID = 7443354922
# مراحل مکالمه
CHOOSING, TYPING_COMPLAINT, TYPING_SUGGESTION = range(3)


async def is_member(update: Update, context: CallbackContext) -> bool:
    """بررسی وضعیت عضویت کاربر در کانال."""
    user_id = update.effective_user.id
    try:
        chat_member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        if chat_member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except telegram.error.TelegramError as e:
        logging.warning(f"Error checking membership: {e}")
        return False


def membership_required(func):
    """دکوریتور برای اطمینان از عضویت کاربر در کانال."""
    async def wrapper(update: Update, context: CallbackContext):
        if not await is_member(update, context):
            keyboard = [[InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🌐 برای استفاده از این ربات ابتدا عضو کانال شوید.\n"
                "پس از عضویت، دوباره /start را بفرستید.",
                reply_markup=reply_markup,
            )
            return
        return await func(update, context)

    return wrapper


@membership_required
async def start(update: Update, context: CallbackContext):
    """پیام خوش‌آمدگویی ساده و توضیح دستورات ربات."""
    await update.message.reply_text(
        "👋 خوش آمدید!\n\n"
        "برای ارسال پیشنهاد یا شکایت، از دستورات زیر استفاده کنید:\n"
        "- /complaints_suggestions: ارسال شکایت یا پیشنهاد\n"
        "- /help: اطلاعات تماس با مدیر\n\n"
        "از قابلیت‌های ربات استفاده کنید و ما را از نظرات خود مطلع کنید. 😊"
    )


@membership_required
async def help_command(update: Update, context: CallbackContext):
    """نمایش اطلاعات تماس."""
    help_message = (
        "💬 اطلاعات تماس با مدیر:\n\n"
        "📬 آیدی تلگرام: @Ardalan_1377\n"
        "📧 ایمیل: ardalanshaban12345@gmail.com\n"
        "📱 شماره تلفن: 09128232615"
    )
    await update.message.reply_text(help_message)


@membership_required
async def membership_status(update: Update, context: CallbackContext):
    """بررسی وضعیت عضویت کاربر."""
    if await is_member(update, context):
        await update.message.reply_text("✅ شما عضو کانال هستید.")
    else:
        keyboard = [[InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ شما عضو کانال نیستید. برای عضویت روی دکمه زیر کلیک کنید:",
            reply_markup=reply_markup,
        )


@membership_required
async def complaints_suggestions(update: Update, context: CallbackContext):
    """نمایش منوی شکایت و پیشنهاد."""
    keyboard = [
        [InlineKeyboardButton("✍️ ارسال شکایت", callback_data="complaint")],
        [InlineKeyboardButton("💡 ارسال پیشنهاد", callback_data="suggestion")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=reply_markup
    )
    return CHOOSING


async def complaint(update: Update, context: CallbackContext):
    """دریافت شکایت کاربر."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✍️ لطفاً شکایت خود را بنویسید:")
    return TYPING_COMPLAINT


async def suggestion(update: Update, context: CallbackContext):
    """دریافت پیشنهاد کاربر."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("💡 لطفاً پیشنهاد خود را بنویسید:")
    return TYPING_SUGGESTION


async def send_complaint(update: Update, context: CallbackContext):
    """ارسال شکایت کاربر به مدیر."""
    user = update.message.from_user
    complaint_text = update.message.text

    message_to_admin = (
        f"📢 شکایت جدید:\n\n"
        f"👤 نام: {user.first_name}\n"
        f"🆔 آیدی عددی: {user.id}\n"
        f"🔗 نام کاربری: @{user.username or 'بدون نام کاربری'}\n\n"
        f"📝 شکایت: {complaint_text}"
    )

    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=message_to_admin)
        await update.message.reply_text("✅ شکایت شما ارسال شد. متشکریم!")
    except Exception as e:
        logging.error(f"Failed to send complaint: {e}")

    return ConversationHandler.END


async def send_suggestion(update: Update, context: CallbackContext):
    """ارسال پیشنهاد کاربر به مدیر."""
    user = update.message.from_user
    suggestion_text = update.message.text

    message_to_admin = (
        f"📢 پیشنهاد جدید:\n\n"
        f"👤 نام: {user.first_name}\n"
        f"🆔 آیدی عددی: {user.id}\n"
        f"🔗 نام کاربری: @{user.username or 'بدون نام کاربری'}\n\n"
        f"💡 پیشنهاد: {suggestion_text}"
    )

    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=message_to_admin)
        await update.message.reply_text("✅ پیشنهاد شما ارسال شد. متشکریم!")
    except Exception as e:
        logging.error(f"Failed to send suggestion: {e}")

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext):
    """لغو مکالمه."""
    await update.message.reply_text("مکالمه لغو شد. ❌")
    return ConversationHandler.END


def main():
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("complaints_suggestions", complaints_suggestions)],
        states={
            CHOOSING: [
                CallbackQueryHandler(complaint, pattern="^complaint$"),
                CallbackQueryHandler(suggestion, pattern="^suggestion$"),
            ],
            TYPING_COMPLAINT: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_complaint)],
            TYPING_SUGGESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_suggestion)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("membership", membership_status))

    application.run_polling()


if __name__ == "__main__":
    main()
