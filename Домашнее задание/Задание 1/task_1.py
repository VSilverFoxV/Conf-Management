import zipfile  
import sys  # Импорт модуля для работы с системными функциями и завершения программы
import json  
import argparse  # Импорт модуля для обработки аргументов командной строки
import calendar  # Импорт модуля для работы с календарями
import time  # Импорт модуля для работы с временем
from datetime import datetime  

class ShellEmulator:
    def __init__(self, zip_path, log_path, username, hostname, startup_script):
        # Инициализатор класса. Принимает путь к zip-архиву, лог-файлу, имя пользователя, имя компьютера и стартовый скрипт
        self.zip_path = zip_path  # Путь к zip-архиву файловой системы
        self.log_path = log_path  # Путь к лог-файлу
        self.username = username  # Имя пользователя
        self.hostname = hostname  # Имя компьютера (хоста)
        self.current_dir = ""  # Текущая директория, изначально корневая
        self.startup_script = startup_script  # Путь к стартовому скрипту внутри архива
        self.log_data = []  # Список для хранения логов действий пользователя
        self.files = {}  # Словарь для хранения файлов из архива: путь -> содержимое
        self.unzip_files()  # Вызов функции для распаковки файлов из архива
        self.load_startup_script()  # Вызов функции для выполнения команд из стартового скрипта

    def unzip_files(self):
        # Функция для распаковки файлов из zip-архива.
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:  # Открываем zip-архив для чтения
            for file_info in zip_ref.infolist():  # Проходим по всем файлам и директориям в архиве
                if not file_info.is_dir():  # Если это не директория
                    with zip_ref.open(file_info) as file:  # Открываем файл
                        self.files[file_info.filename] = file.read()  # Читаем содержимое файла и сохраняем в словарь
        return self.files  # Возвращаем распакованные файлы для проверки

    def log_action(self, command, output):
        # Функция для логирования действий пользователя
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Текущая дата и время
            'user': self.username,  # Имя пользователя
            'command': command,  # Выполненная команда
            'output': output   # Результат деятельности ф-ии
        }
        self.log_data.append(log_entry)  # Добавляем запись в список логов
        with open(self.log_path, 'w', encoding='utf-8') as log_file:  # Открываем лог-файл для записи
            json.dump(self.log_data, log_file, indent=4, ensure_ascii=False)  # Записываем логи в файл в формате JSON
        return log_entry  # Возвращаем запись лога для проверки

    def load_startup_script(self):
        # Функция для загрузки и выполнения команд из стартового скрипта
        results = []  # Список для хранения результатов выполнения команд
        if self.startup_script:  # Если путь к стартовому скрипту указан
            script_path = self.startup_script  # Запоминаем путь к скрипту
            if script_path in self.files:  # Если скрипт найден в архиве
                try:
                    script_content = self.files[script_path].decode('utf-8')  # Декодируем содержимое скрипта в строку
                    for line in script_content.splitlines():  # Разбиваем содержимое на строки
                        if line.strip():  # Пропускаем пустые строки
                            print(f"Выполнение команды из скрипта: {line.strip()}")  # Печатаем команду
                            result = self.execute_command(line.strip())  # Выполняем команду
                            results.append((line.strip(), result))  # Добавляем команду и результат в список
                            if result:  # Если есть результат выполнения команды
                                print(result)  # Печатаем результат
                except UnicodeDecodeError:
                    results.append((script_path, "Ошибка декодирования"))
                    print(f"Ошибка декодирования файла скрипта: {script_path}")  # Обрабатываем ошибку декодирования
            else:
                results.append((script_path, "Стартовый скрипт не найден в архиве."))
                print(f"Стартовый скрипт {script_path} не найден в архиве.")  # Если скрипт не найден в архиве
        return results  # Возвращаем результаты выполнения скрипта

    def execute_command(self, command):
        # Функция для выполнения команд, введенных пользователем
        if command.startswith("ls"):
            parts = command.split(" ", 1)
            if len(parts) > 1:
                result = self.ls(parts[1].strip())  # Передаем аргумент в ls
            else:
                result = self.ls()  # Вызываем без аргумента
        elif command.startswith("cd"):
            parts = command.split(" ", 1)
            if len(parts) > 1:
                directory = parts[1]  # Получаем директорию для команды 'cd'
                result = self.cd(directory)  # Выполняем команду 'cd'
            else:
                result = "Ошибка: не указана директория."  # Ошибка, если директория не указана
        elif command.startswith("cal"):
            result = self.cal()  # Выполняем команду 'cal'
        elif command.startswith("clear"):
            result = self.clear()  # Выполняем команду 'clear'
        elif command.startswith("who"):
            result = self.who()  # Выполняем команду 'who'
        elif command.startswith("exit"):
            result = self.exit()  # Выполняем команду 'exit'
        else:
            result = "Команда не найдена"  # Ошибка, если команда не распознана
        
        self.log_action(command, result)  # Логируем выполненную команду
        return result  # Возвращаем результат выполнения команды

    def ls(self, directory=None):
        # Функция для выполнения команды 'ls', выводит список файлов в текущей директории
        prefix = self.current_dir + '/' if self.current_dir else ''  # Префикс для текущей директории
        if directory:
            # Если передан аргумент directory, добавляем его к текущей директории
            prefix += directory + '/' if not directory.endswith('/') else directory
        items = set()  # Множество для хранения файлов и директорий
        for f in self.files:  # Проходим по всем файлам в архиве
            if f.startswith(prefix):  # Если файл находится в указанной директории
                remainder = f[len(prefix):]  # Оставшаяся часть пути
                if '/' in remainder:
                    items.add(remainder.split('/', 1)[0] + '/')  # Добавляем директории
                else:
                    items.add(remainder)  # Добавляем файлы
        return '\n'.join(sorted(items))  # Возвращаем отсортированный список файлов и директорий.

    def cd(self, directory):
        # Функция для выполнения команды 'cd', меняет текущую директорию
        if directory == "..":  # Если команда 'cd ..', переходим на уровень выше
            if self.current_dir:  # Если не находимся в корне
                self.current_dir = '/'.join(self.current_dir.split('/')[:-1])  # Переходим в родительскую директорию
            return f"Перешли в директорию: {self.current_dir if self.current_dir else '/'}"  # Возвращаем сообщение о переходе

        new_dir = f"{self.current_dir}/{directory}" if self.current_dir else directory  # Определяем новую директорию
        prefix = new_dir + '/'  # Префикс для проверки наличия директории
        if any(f.startswith(prefix) for f in self.files):  # Проверяем, существует ли директория
            self.current_dir = new_dir  # Меняем текущую директорию
            return f"Перешли в директорию: {self.current_dir}"  # Возвращаем сообщение о переходе
        else:
            return "Ошибка: Директория не найдена."  # Сообщение об ошибке, если директория не найдена

    def cal(self):
        # Функция для выполнения команды 'cal', выводит календарь текущего месяца
        current_year = time.localtime().tm_year  # Получаем текущий год
        current_month = time.localtime().tm_mon  # Получаем текущий месяц
        return calendar.month(current_year, current_month)  # Возвращаем календарь

    def clear(self):
        # Функция для выполнения команды 'clear', эмулирует очистку экрана
        return "\033[H\033[J"  # Возвращаем управляющие символы для очистки экрана в терминале

    def who(self):
        # Функция для выполнения команды 'who', выводит имя текущего пользователя
        return f"Текущий пользователь: {self.username}"  # Возвращаем имя пользователя

    def exit(self):
        # Функция для выполнения команды 'exit', завершает программу
        print("Выход из эмулятора.")  # Печатаем сообщение о выходе
        self.log_action("exit", "Выход из эмулятора.")  # Логируем команду выхода
        sys.exit()  # Завершаем выполнение программы

    def run(self):
        # Основная функция, которая запускает цикл обработки команд
        try:
            while True:
                prompt_dir = self.current_dir if self.current_dir else "/"  # Определяем строку с текущей директорией
                command = input(f"{self.username}@{self.hostname}:{prompt_dir}$ ")  # Получаем команду от пользователя
                output = self.execute_command(command)  # Выполняем команду
                if output:
                    print(output)  # Если есть результат, выводим его на экран
        except KeyboardInterrupt:
            print("\nВыход из эмулятора.")  # Обрабатываем прерывание программы (Ctrl+C)
            self.log_action("exit (Ctrl+C)", "Выход из эмулятора.")  # Логируем команду выхода (Ctrl+C)
            sys.exit()  # Завершаем выполнение программы

def main():
    # Функция для обработки аргументов командной строки и запуска эмулятора.
    parser = argparse.ArgumentParser(description='Shell Emulator')  # Создаем парсер аргументов командной строки
    parser.add_argument('--user', required=True, help='Имя пользователя')  # Аргумент для имени пользователя
    parser.add_argument('--host', required=True, help='Имя компьютера')  # Аргумент для имени компьютера
    parser.add_argument('--zip', required=True, help='Путь к архиву файловой системы')  # Аргумент для пути к zip-архиву
    parser.add_argument('--log', required=True, help='Путь к лог-файлу')  # Аргумент для пути к лог-файлу
    parser.add_argument('--script', required=False, help='Путь к стартовому скрипту внутри архива')  # Аргумент для пути к стартовому скрипту
    args = parser.parse_args()  # Парсим аргументы командной строки.
    emulator = ShellEmulator(args.zip, args.log, args.user, args.host, args.script)  # Создаем объект ShellEmulator
    emulator.run()  # Запускаем эмулятор

if __name__ == "__main__":
    main()  # Если скрипт запущен напрямую, вызываем функцию main()
