import unittest
from app import app  # Импортируйте ваше Flask приложение


class ASRTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()  # Создайте тестовый клиент
        self.app.testing = True  # Включите режим тестирования

    def test_asr_with_file(self):
        with open('/home/pai9maker/vosk_mp3_to_json/audio.mp3', 'rb') as audio_file:
            response = self.app.post('/asr', data={'file': audio_file})
            self.assertEqual(response.status_code, 200)  # Проверьте, что статус ответа 200

            # Получите данные из ответа
            response_data = response.get_json()

            # Сохраните результат в файл
            with open('/home/pai9maker/vosk_mp3_to_json/result.txt', 'w') as result_file:
                result_file.write(str(response_data))  # Запишите данные в файл

    def test_asr_without_file(self):
        response = self.app.post('/asr', data={})  # Отправьте пустые данные
        self.assertEqual(response.status_code, 400)  # Проверьте статус ответа
        response_data = response.get_json()
        self.assertEqual(response_data["error"], "Файл не предоставлен")  # Проверьте сообщение об ошибке


if __name__ == '__main__':
    unittest.main()
