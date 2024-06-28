# main.py

from handlers import *
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler

def main() -> None:
    """Start the bot."""
    application = Application.builder().token("TOKEN FROM BOT FATHER").build()

    add_student_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_student", add_student_start)],
        states={
            STUDENT_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_data)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    delete_student_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("delete_student", delete_student_start)],
        states={
            DELETE_STUDENT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_student)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    upload_docx_handler = ConversationHandler(
        entry_points=[CommandHandler("upload_docx", upload_docx_start)],
        states={
            UPLOAD_DOCX: [MessageHandler(filters.Document.ALL, handle_docx_upload)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(add_student_conv_handler)
    application.add_handler(delete_student_conv_handler)
    application.add_handler(upload_docx_handler)
    application.add_handler(MessageHandler(filters.TEXT, student_detail))

    application.run_polling()

if __name__ == "__main__":
    main()
