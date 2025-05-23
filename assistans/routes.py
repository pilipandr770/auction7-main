import os
import logging
import tempfile
from flask import Blueprint, request, jsonify, session, current_app as app
from openai import OpenAI
from app.utils.voice import synthesize
from .whisper_service import transcribe

assistant_bp = Blueprint('assistant', __name__)

# Ініціалізація OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Fix: Get ASSISTANT_ID from environment variable, or use a default if not set
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID", "asst_default_id_replace_me")
# Log a warning if the assistant ID is using the default value
if ASSISTANT_ID == "asst_default_id_replace_me":
    print("WARNING: Using default assistant ID. Please set OPENAI_ASSISTANT_ID in your .env file.")

client = OpenAI(api_key=OPENAI_API_KEY)

logger = logging.getLogger(__name__)

@assistant_bp.route('/voice', methods=['POST'])
def voice_message():
    """Handle voice message uploads and process them through Whisper"""
    try:
        # Check if an audio file was uploaded
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No audio file selected"}), 400
        
        # Get additional parameters
        page = request.form.get("page", "")
        lang = request.form.get("lang", "uk")
        
        logger.info(f"[VOICE] Received audio file: {audio_file.filename} [PAGE] {page} [LANG] {lang}")
        
        # Save the uploaded audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            audio_file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe audio using Whisper
            with open(temp_file_path, 'rb') as audio_data:
                transcribed_text = transcribe(audio_data)
            
            logger.info(f"[WHISPER] Transcribed: {transcribed_text}")
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            if not transcribed_text:
                error_messages = {
                    'en': "Could not understand the audio. Please try again.",
                    'de': "Konnte das Audio nicht verstehen. Bitte versuchen Sie es erneut.", 
                    'uk': "Не вдалося розпізнати аудіо. Будь ласка, спробуйте ще раз."
                }
                return jsonify({"error": error_messages.get(lang, error_messages['uk'])}), 400
            
            # Now process the transcribed text through the assistant
            # Create a JSON payload similar to the text ask route
            assistant_data = {
                "message": transcribed_text,
                "page": page,
                "lang": lang,
                "isVoiceInput": True
            }
            
            # Process through the same logic as the text route
            return process_assistant_message(assistant_data)
            
        except Exception as e:
            # Clean up temporary file if it exists
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise e
            
    except Exception as e:
        logger.exception(f"[VOICE ERROR] {str(e)}")
        
        error_messages = {
            'en': "Sorry, I couldn't process your voice message. Please try again.",
            'de': "Entschuldigung, ich konnte Ihre Sprachnachricht nicht verarbeiten. Bitte versuchen Sie es erneut.",
            'uk': "Вибачте, не вдалося обробити ваше голосове повідомлення. Будь ласка, спробуйте ще раз."
        }
        
        lang = request.form.get("lang", "uk")
        error_message = error_messages.get(lang, error_messages['uk'])
        return jsonify({"error": error_message}), 500


def process_assistant_message(data):
    """Shared logic for processing messages through the assistant"""
    message = data.get("message")
    page = data.get("page", "")
    lang = data.get("lang", "uk")
    is_voice_input = data.get("isVoiceInput", False)
    
    logger.info(f"[USER] {message} [PAGE] {page} [LANG] {lang} [VOICE] {is_voice_input}")

    if not message:
        logger.error("Пусте повідомлення")
        return jsonify({"error": "Пусте повідомлення"}), 400

    try:
        # Check if we have a valid assistant ID and API key
        if OPENAI_API_KEY and ASSISTANT_ID != "asst_default_id_replace_me":
            # Формуємо prompt для асистента з урахуванням сторінки, мови та джерела повідомлення
            system_prompt = (
                f"User language: {lang}\n"
                f"Current page: {page}\n"
                f"Input method: {'voice' if is_voice_input else 'text'}\n"
                f"User message: {message}"
            )

            # Створюємо новий thread для кожної сесії
            thread = client.beta.threads.create()
            logger.info(f"[THREAD] created: {thread.id}")

            # Відправляємо повідомлення у thread
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=system_prompt
            )
            logger.info(f"[THREAD] message sent: {system_prompt}")

            # Запускаємо run
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=ASSISTANT_ID
            )
            
            logger.info(f"[RUN] started: {run.id}")

            # Чекаємо завершення run
            import time
            while True:
                run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                logger.info(f"[RUN] status: {run_status.status}")
                if run_status.status in ["completed", "failed", "cancelled"]:
                    break
                time.sleep(1)

            if run_status.status != "completed":
                logger.error(f"[RUN] not completed: {run_status.status}")
                return jsonify({"error": "Асистент не відповів"}), 500

            # Отримуємо повідомлення асистента
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            logger.info(f"[MESSAGES] count: {len(messages.data)}")
            reply = next(
                (m.content[0].text.value for m in messages.data if m.role == "assistant"),
                "Вибачте, не вдалося отримати відповідь."
            )
            logger.info(f"[ASSISTANT] {reply}")

        else:
            # Fallback to simple response if OpenAI Assistant is not configured
            logger.warning("OpenAI Assistant not configured. Using fallback response.")
            
            # Add information about voice input to the response
            voice_info = " (Received from voice input)" if is_voice_input else ""
            
            # Generate a simple response based on the user's message and page
            if lang == 'de':
                reply = f"Hallo!{voice_info} Dies ist eine Fallback-Antwort, da der OpenAI-Assistent nicht konfiguriert ist. Ihre Nachricht war: '{message}'"
            elif lang == 'en':
                reply = f"Hello!{voice_info} This is a fallback response since the OpenAI Assistant is not configured. Your message was: '{message}'"
            else:  # Ukrainian default
                reply = f"Привіт!{voice_info} Це резервна відповідь, оскільки асистент OpenAI не налаштований. Ваше повідомлення: '{message}'"

        # Генеруємо аудіо-відповідь (TTS)
        audio_path = synthesize(reply, lang=lang)
        logger.info(f"[AUDIO] {audio_path}")

        # Переміщаємо аудіо у статичну папку для доступу з фронта
        if audio_path:
            from pathlib import Path
            import shutil
            audio_dir = Path('app/static/audio')
            audio_dir.mkdir(parents=True, exist_ok=True)
            new_audio_path = audio_dir / os.path.basename(audio_path)
            shutil.move(audio_path, new_audio_path)
            return jsonify({
                "response": reply,
                "audio": f"/static/audio/{new_audio_path.name}",
                "transcribed_text": message if is_voice_input else None
            })
        else:
            return jsonify({
                "response": reply,
                "transcribed_text": message if is_voice_input else None
            })
        
    except Exception as e:
        logger.exception(f"[ERROR] {str(e)}")
        
        # Provide a more user-friendly error message based on language
        error_messages = {
            'en': "Sorry, I'm having trouble connecting to the assistant. Please try again later.",
            'de': "Entschuldigung, ich habe Schwierigkeiten, mich mit dem Assistenten zu verbinden. Bitte versuchen Sie es später erneut.",
            'uk': "Вибачте, у мене виникли проблеми з підключенням до асистента. Будь ласка, спробуйте пізніше."
        }
        
        error_message = error_messages.get(lang, error_messages['uk'])
        return jsonify({"error": error_message}), 500


@assistant_bp.route('/ask', methods=['POST'])
def ask():
    """Handle text-based messages"""
    data = request.json
    return process_assistant_message(data)
