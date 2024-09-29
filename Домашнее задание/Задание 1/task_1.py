import zipfile
import sys
import json
import argparse
import calendar
import time
from datetime import datetime

class ShellEmulator:
    def __init__(self, zip_path, log_path, username, hostname, startup_script):
        self.zip_path = zip_path
        self.log_path = log_path
        self.username = username
        self.hostname = hostname
        self.current_dir = ""  # Начинаем в корне архива
        self.startup_script = startup_script
        self.log_data = []
        self.files = {}  # Словарь файлов: путь -> содержимое
        self.unzip_files()
        self.load_startup_script()

    def unzip_files(self):
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if not file_info.is_dir():
                    with zip_ref.open(file_info) as file:
                        self.files[file_info.filename] = file.read()

    def log_action(self, command):
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'user': self.username,
            'command': command
        }
        self.log_data.append(log_entry)
        with open(self.log_path, 'w', encoding='utf-8') as log_file:
            json.dump(self.log_data, log_file, indent=4, ensure_ascii=False)

    def load_startup_script(self):
        if self.startup_script:
            script_path = self.startup_script
            if script_path in self.files:
                try:
                    script_content = self.files[script_path].decode('utf-8')
                    for line in script_content.splitlines():
                        if line.strip():  # Пропускаем пустые строки
                            print(f"Выполнение команды из скрипта: {line.strip()}")
                            result = self.execute_command(line.strip())
                            if result:  # Выводим результат выполнения команды
                                print(result)
                except UnicodeDecodeError:
                    print(f"Ошибка декодирования файла скрипта: {script_path}")
            else:
                print(f"Стартовый скрипт {script_path} не найден в архиве.")


    def execute_command(self, command):
        if command.startswith("ls"):
            result = self.ls()
        elif command.startswith("cd"):
            parts = command.split(" ", 1)
            if len(parts) > 1:
                directory = parts[1]
                result = self.cd(directory)
            else:
                result = "Ошибка: не указана директория."
        elif command.startswith("cal"):
            result = self.cal()
        elif command.startswith("clear"):
            result = self.clear()
        elif command.startswith("who"):
            result = self.who()
        elif command.startswith("exit"):
            result = self.exit()
        else:
            result = "Команда не найдена"
        
        self.log_action(command)
        return result

    def ls(self):
        # Возвращаем список файлов и директорий в текущей директории
        prefix = self.current_dir + '/' if self.current_dir else ''
        items = set()
        for f in self.files:
            if f.startswith(prefix):
                remainder = f[len(prefix):]
                if '/' in remainder:
                    items.add(remainder.split('/', 1)[0] + '/')
                else:
                    items.add(remainder)
        return '\n'.join(sorted(items))

    def cd(self, directory):
        if directory == "..":
            if self.current_dir:
                self.current_dir = '/'.join(self.current_dir.split('/')[:-1])
            return f"Перешли в директорию: {self.current_dir if self.current_dir else '/'}"

        new_dir = f"{self.current_dir}/{directory}" if self.current_dir else directory
        prefix = new_dir + '/'
        if any(f.startswith(prefix) for f in self.files):
            self.current_dir = new_dir
            return f"Перешли в директорию: {self.current_dir}"
        else:
            return "Ошибка: Директория не найдена."
    

    def cal(self):
        current_year = time.localtime().tm_year
        current_month = time.localtime().tm_mon
        return calendar.month(current_year, current_month)

    def clear(self):
        # Эмуляция очистки экрана
        return "\033[H\033[J"

    def who(self):
        return f"Текущий пользователь: {self.username}"

    def exit(self):
        print("Выход из эмулятора.")
        self.log_action("exit")
        sys.exit()

    def run(self):
        try:
            while True:
                prompt_dir = self.current_dir if self.current_dir else "/"
                command = input(f"{self.username}@{self.hostname}:{prompt_dir}$ ")
                output = self.execute_command(command)
                if output:
                    print(output)
        except KeyboardInterrupt:
            print("\nВыход из эмулятора.")
            sys.exit()

def main():
    parser = argparse.ArgumentParser(description='Shell Emulator')
    parser.add_argument('--user', required=True, help='Имя пользователя')
    parser.add_argument('--host', required=True, help='Имя компьютера')
    parser.add_argument('--zip', required=True, help='Путь к архиву файловой системы')
    parser.add_argument('--log', required=True, help='Путь к лог-файлу')
    parser.add_argument('--script', required=False, help='Путь к стартовому скрипту внутри архива')

    args = parser.parse_args()
    emulator = ShellEmulator(args.zip, args.log, args.user, args.host, args.script)
    emulator.run()

if __name__ == "__main__":
    main()
