import pytest
from task_1 import ShellEmulator
import zipfile
import calendar
import time

@pytest.fixture
def shell_emulator(tmpdir):
    # Фикстура для создания экземпляра ShellEmulator с тестовыми данными
    zip_path = str(tmpdir.join('test.zip'))
    log_path = str(tmpdir.join('test.log'))
    with zipfile.ZipFile(zip_path, 'w') as zip_ref:
        zip_ref.writestr('file1.txt', 'content of file1')
        zip_ref.writestr('folder/file2.txt', 'content of file2')
        zip_ref.writestr('startup.sh', 'ls\nwho\n')
    return ShellEmulator(zip_path, log_path, 'test_user', 'test_host', 'startup.sh')


# Тесты для unzip_files
def test_unzip_files(shell_emulator):
    files = shell_emulator.unzip_files()
    assert 'file1.txt' in files
    assert 'folder/file2.txt' in files
    assert 'startup.sh' in files


# Тесты для log_action
def test_log_action(shell_emulator):
    log_entry = shell_emulator.log_action('ls', 'file1.txt\nfolder/\nstartup.sh')
    assert log_entry['command'] == 'ls'
    assert log_entry['output'] == 'file1.txt\nfolder/\nstartup.sh'


# Тесты для load_startup_script
def test_load_startup_script(shell_emulator):
    result = shell_emulator.load_startup_script()
    assert ('ls', 'file1.txt\nfolder/\nstartup.sh') in result
    assert ('who', 'Текущий пользователь: test_user') in result

def test_load_startup_script_not_found(shell_emulator):
    shell_emulator.startup_script = 'not_found.sh'
    result = shell_emulator.load_startup_script()
    assert ('not_found.sh', 'Стартовый скрипт не найден в архиве.') in result


# Тесты для ls
def test_ls_current_directory(shell_emulator):
    result = shell_emulator.ls()
    assert 'file1.txt' in result
    assert 'folder/' in result

def test_ls_specified_directory(shell_emulator):
    result = shell_emulator.ls('folder')
    assert 'file2.txt' in result


# Тесты для cd
def test_cd_to_folder(shell_emulator):
    result = shell_emulator.cd('folder')
    assert result == "Перешли в директорию: folder"
    assert shell_emulator.current_dir == 'folder'

def test_cd_parent_directory(shell_emulator):
    shell_emulator.cd('folder')
    result = shell_emulator.cd('..')
    assert result == "Перешли в директорию: /"
    assert shell_emulator.current_dir == ''


# Тесты для cal
def test_cal(shell_emulator):
    result = shell_emulator.cal()
    assert calendar.month(time.localtime().tm_year, time.localtime().tm_mon) in result

def test_cal_format(shell_emulator):
    result = shell_emulator.cal()
    assert isinstance(result, str)
    assert len(result) > 0


# Тесты для who
def test_who(shell_emulator):
    result = shell_emulator.who()
    assert result == "Текущий пользователь: test_user"

def test_who_format(shell_emulator):
    result = shell_emulator.who()
    assert isinstance(result, str)


# Тест для exit
def test_exit(shell_emulator):
    with pytest.raises(SystemExit):
        shell_emulator.exit()
