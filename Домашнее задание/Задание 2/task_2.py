import sys  
import requests  # Импортируем модуль requests для выполнения HTTP-запросов к веб-сайтам.
from bs4 import BeautifulSoup  # Импортируем BeautifulSoup из библиотеки bs4 для парсинга HTML-страниц.

def fetch_apk_dependencies(package_name: str):
    """Получение зависимостей пакета из Alpine Linux."""
    deps = []  
    base_url = 'https://pkgs.alpinelinux.org/package/edge/main/x86_64/' + package_name
    
    
    html = requests.get(base_url)  # Выполняем HTTP-запрос к сформированному URL.
    bs = BeautifulSoup(html.text, 'html.parser')  
    # Парсим HTML-страницу с помощью BeautifulSoup
    
    details = bs.find('details')  
    
    
    if not details:  
        return deps

    for a in details.find_all('a'):  
        # Ищем все ссылки (<a>) внутри элемента <details>, которые указывают на зависимости.
        
        next_package = a.text.strip()  
        # Получаем текст ссылки (название следующего пакета), убирая пробелы по краям.
        
        if next_package and next_package != "None":  
            # Проверяем, что пакет действительно существует и не равен строке "None".
            
            link = (package_name, next_package)  
            # Создаём пару (текущий пакет, следующий пакет) для графа зависимостей.
            
            deps.append(link)  
            # Добавляем пару в список зависимостей.
            
            deps += fetch_apk_dependencies(next_package)  
            # Рекурсивно вызываем функцию для следующего пакета, чтобы получить его транзитивные зависимости.
    
    return deps

def build_graphviz(deps):
    """Формирование Graphviz диаграммы."""
    graphviz_code = 'digraph G {\n'  
    # Инициализируем строку с началом графа в формате Graphviz (ориентированный граф).
    
    added_links = set()  
    # Создаём множество для хранения добавленных связей, чтобы избежать дублирования.

    for src, dest in deps:  
        # Проходим по каждой паре зависимостей (источник, назначение).
        
        link = f'"{src}" -> "{dest}"'  
        # Формируем строку для Graphviz, представляющую связь между двумя пакетами.
        
        if link not in added_links:  
            # Проверяем, была ли уже добавлена эта связь в граф.
            
            graphviz_code += f'  {link};\n'  
            # Если нет, добавляем её в код графа.
            
            added_links.add(link)  
            # Добавляем связь в множество, чтобы избежать её повторного добавления.
    
    graphviz_code += '}\n'  
    # Закрываем описание графа.
    
    return graphviz_code  # Возвращаем строку с кодом Graphviz.

def main():
    if len(sys.argv) != 3:  
        # Проверяем, что было передано ровно два аргумента: имя пакета и путь к файлу.
        
        print("Использование: python task_2.py <package_name> <output_path>")  
        
        sys.exit(1)  
        # Завершаем выполнение программы с ошибкой.

    package_name = sys.argv[1]  # Первый аргумент — это имя пакета.
    output_path = sys.argv[2]  # Второй аргумент — это путь к файлу для записи результатов.

    # Получаем зависимости для указанного пакета
    dependencies = fetch_apk_dependencies(package_name)  
    # Вызываем функцию fetch_apk_dependencies для получения всех зависимостей пакета.

    if not dependencies:  
        # Если зависимости не найдены, выводим сообщение и завершаем выполнение программы.
        
        print(f"Не удалось найти зависимости для пакета {package_name}")
        sys.exit(1)

    # Строим Graphviz диаграмму
    graphviz_code = build_graphviz(dependencies)  
    

    # Сохраняем результат в указанный файл
    with open(output_path, 'w', encoding='utf-8') as file:  
        # Открываем файл для записи с указанным путём и кодировкой UTF-8.
        
        file.write(graphviz_code)  
        # Записываем код Graphviz в файл.

    print(f"Graphviz код сохранён в {output_path}")  
    # Выводим сообщение о том, что код сохранён.
    
    print(graphviz_code)  
   

if __name__ == "__main__":
    main()  
    
