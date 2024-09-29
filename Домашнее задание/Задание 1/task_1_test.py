import unittest
from task_1 import ShellEmulator

class TestShellEmulator(unittest.TestCase):

    def setUp(self):
        self.emulator = ShellEmulator("C:\\Users\\U\\Desktop\\Конфиг\\Conf-Management\\Домашнее задание\\Задание 1\\test.zip", 
                                       "log.json", "john", "mypc", None)

    def tearDown(self):
        try:
            with open('log.json', 'w') as log_file:
                log_file.write('')  # Очищаем файл
        except FileNotFoundError:
            pass

    # Тесты для команды ls
    def test_ls_directory(self):
        """Проверка ls в директории с файлами"""
        self.assertIn('Texts/file1.txt', self.emulator.ls())  # Проверяем наличие одного из файлов
        self.assertIn('Texts/file2.txt', self.emulator.ls())  # Проверяем наличие второго файла


    def test_ls_no_files(self):
        """Проверка ls в пустой директории"""
        self.emulator.current_dir = "temp_directory"  # Убедитесь, что это пустая директория
        self.assertEqual(self.emulator.ls(), [])  # Убедитесь, что метод ls возвращает пустой список

    # Тесты для команды cd
    def test_cd_existing_directory(self):
        """Проверка перехода в существующую директорию"""
        result = self.emulator.cd("Texts")
        self.assertIn("Перешли в директорию", result)

    def test_cd_non_existing_directory(self):
        """Проверка ошибки при переходе в несуществующую директорию"""
        result = self.emulator.cd("non_existent_dir")
        self.assertEqual(result, "Ошибка: Директория не найдена.")

    # Тесты для команды cal
    def test_cal_current_month(self):
        """Проверка вывода календаря текущего месяца"""
        result = self.emulator.cal()
        self.assertIn("September", result)  # Или замена на текущий месяц

    def test_cal_output_format(self):
        """Проверка формата вывода команды cal"""
        result = self.emulator.cal()
        self.assertIsInstance(result, str)
        self.assertIn("Mo Tu We Th Fr Sa Su", result)

    # Тесты для команды clear
    def test_clear_command(self):
        """Проверка команды clear"""
        result = self.emulator.clear()
        self.assertEqual(result, "\033[H\033[J")

    def test_clear_output_type(self):
        """Проверка типа данных, возвращаемых clear"""
        result = self.emulator.clear()
        self.assertIsInstance(result, str)

    # Тесты для команды who
    def test_who_command(self):
        """Проверка команды who для текущего пользователя"""
        result = self.emulator.who()
        self.assertEqual(result, "Текущий пользователь: john")

    def test_who_output_format(self):
        """Проверка формата вывода команды who"""
        result = self.emulator.who()
        self.assertIsInstance(result, str)

    # Тесты для команды exit
    def test_exit_command(self):
        """Проверка выхода из эмулятора"""
        with self.assertRaises(SystemExit):
            self.emulator.exit()

    def test_exit_logs_action(self):
        """Проверка, что команда exit логируется"""
        try:
            self.emulator.exit()
        except SystemExit:
            pass
        with open('log.json', 'r') as log_file:
            log_data = log_file.read()
            self.assertIn("exit", log_data)

if __name__ == '__main__':
    unittest.main()
