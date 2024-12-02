import tempfile
import os
import json
from flask import Flask, request, jsonify, Response
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
import smtplib
from email.mime.text import MIMEText

# Проверяем наличие модели
if not os.path.exists("model"):
    print("Пожалуйста, загрузите модель с https://alphacephei.com/vosk/models и распакуйте как 'model' в текущую папку (нужно скачать model-small-ru).")
    exit(1)

# Устанавливаем Frame Rate
FRAME_RATE = 16000
CHANNELS = 1

model = Model("model")
app = Flask(__name__)

def convert_mp3_to_wav(mp3_file):
    """Конвертируем MP3 в WAV и возвращаем путь к WAV файлу."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as wav_file:
        audio = AudioSegment.from_file(mp3_file, format='mp3')
        audio = audio.set_channels(CHANNELS)
        audio = audio.set_frame_rate(FRAME_RATE)
        audio.export(wav_file.name, format="wav")
        return wav_file.name

def recognize_audio(wav_file):
    """Распознаем текст из WAV файла и возвращаем результаты."""
    rec = KaldiRecognizer(model, FRAME_RATE)
    audio = AudioSegment.from_wav(wav_file)
    results = []
    total_duration = len(audio) / 1000  # Длительность в секундах

    for chunk in audio[::4000]:  # Обрабатываем по 4 секунды
        rec.AcceptWaveform(chunk.raw_data)
        result = rec.Result()
        if result:
            results.append(json.loads(result))

    final_result = rec.FinalResult()
    if final_result:
        results.append(json.loads(final_result))

    return results, total_duration


@app.route('/asr', methods=['POST'])
def asr():
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({"error": "Файл не предоставлен"}), 400

    audio_file = request.files['file']
    wav_file = convert_mp3_to_wav(audio_file)
    results, total_duration = recognize_audio(wav_file)

    # Обработка результата
    dialog = []
    result_duration = {"receiver": 0, "transmitter": 0}

    for index, item in enumerate(results):
        if 'text' in item:
            speaker = 'receiver' if index % 2 == 0 else 'transmitter'
            text = item['text']
            duration = len(text.split())  # Примерная длительность на основе количества слов

            dialog.append({
                "source": speaker,
                "text": text,
                "duration": duration,
                "raised_voice": "!" in text,
                "gender": "male" if speaker == 'receiver' else "female"
            })
            result_duration[speaker] += duration

    response = {
        "dialog": dialog,
        "result_duration": result_duration
    }

    # Удаляем временный WAV файл
    os.remove(wav_file)


    return Response(json.dumps(response, ensure_ascii=False, indent=4), mimetype='application/json; charset=utf-8')

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
