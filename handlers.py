# handlers.py

import logging
import os
from telegram import ForceReply, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from student_db import StudentDB
from word_taker import process_file, insert_into_db  # Import functions from word_taker

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levellevel)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Define conversation states
STUDENT_DATA, DELETE_STUDENT_ID, UPLOAD_DOCX = range(3)

# Define admin IDs
ADMIN_IDS = [1111111 , 22222222 , 3333333]  # Replace with actual admin IDs

def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("دسترسی به این دستوری مختص ادمین ها می باشد.")
            return ConversationHandler.END
        return await func(update, context, *args, **kwargs)
    return wrapper

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf'''
        سلام 
        تو این ربات میتونی نمراتت رو ببینی.
        شماره دانشجوییت رو با اعداد انگلیسی وارد کن
        ''',
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("میتونید از کامند /add_student استفاده کنید تا اطلاعات یوزر جدیدی رو وارد کنید. و میتونید شماره دانشجویی موردنظرتون رو ارسال کنید تا اطلاعات براتون فرستاده بشه.")

async def student_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    student_detail = StudentDB().get_student_data(update.message.text)
    if student_detail is None:
        await update.message.reply_text("همچین شماره دانشجویی‌ای وجود نداره.")
    else:
        await update.message.reply_text(f"یادداشت: {student_detail['student_note']}")

@admin_only
async def add_student_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the add student conversation."""
    await update.message.reply_text("لطفا شماره دانشجویی و متن را وارد بکنید (هر دانشجو در یک خط جداگانه):")
    return STUDENT_DATA

@admin_only
async def add_student_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the student data and end the conversation."""
    student_data_lines = update.message.text.split('\n')
    added_students = []

    for line in student_data_lines:
        try:
            student_id, student_note = line.split(':', 1)
            student_id = student_id.strip()
            student_note = student_note.strip()
            StudentDB().add_student(student_id, student_note)
            added_students.append(student_id)
        except Exception as e:
            await update.message.reply_text(f"مشکلی پیش اومده در خط: {line} - {e}")

    if added_students:
        await update.message.reply_text(f"دانشجویان اضافه شده: {', '.join(added_students)}", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("هیچ دانشجویی اضافه نشد.", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

@admin_only
async def delete_student_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the delete student conversation."""
    await update.message.reply_text("لطفا شماره دانشجویی که می خواهید حذف کنید را وارد کنید:")
    return DELETE_STUDENT_ID

@admin_only
async def delete_student(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete the student and end the conversation."""
    student_id = update.message.text
    if StudentDB().delete_student(student_id):
        await update.message.reply_text("دانشجو با موفقیت حذف شد.", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("شماره دانشجویی وجود ندارد.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

@admin_only
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel"""
    await update.message.reply_text("عملیات لغو شد.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

@admin_only
async def upload_docx_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the process of uploading a DOCX file."""
    await update.message.reply_text("لطفا فایل داکس مدنظر را ارسال کنید")
    return UPLOAD_DOCX

@admin_only
async def handle_docx_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the DOCX file upload."""
    if update.message.document:
        file = update.message.document
        if file.mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            file_id = file.file_id
            new_file = await context.bot.get_file(file_id)
            file_path = f"downloads/{file.file_unique_id}.docx"  # Use file_unique_id to ensure unique filename
            
            # Create directory if not exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            new_file_path = await new_file.download_to_drive(file_path)
            records = process_file(new_file_path)
            inserted_records = insert_into_db(records)
            
            if inserted_records:
                await update.message.reply_text("Data inserted successfully. Inserted records:")
                for student_id, note in inserted_records:
                    await update.message.reply_text(f"Student ID: {student_id}, Student Note: {note}")
            else:
                await update.message.reply_text("No data was inserted.")
            
            # Clean up the downloaded file
            os.remove(new_file_path)
        else:
            await update.message.reply_text("فایل داکس واردی معتبر نمیباشد")
    else:
        await update.message.reply_text("No file received. Please try again.")
    
    return ConversationHandler.END
