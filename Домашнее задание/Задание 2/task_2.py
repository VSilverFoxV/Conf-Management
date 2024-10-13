import sys
import requests
from bs4 import BeautifulSoup

def fetch_apk_dependencies(package_name: str):
    """Получение зависимостей пакета из Alpine Linux."""
    deps = []
    base_url = 'https://pkgs.alpinelinux.org/package/edge/main/x86_64/' + package_name
    html = requests.get(base_url)
    bs = BeautifulSoup(html.text, 'html.parser')
    
    details = bs.find('details')
    if not details:
        return deps

    for a in details.find_all('a'):
        next_package = a.text.strip()
        if next_package and next_package != "None":
            link = (package_name, next_package)
            deps.append(link)
            deps += fetch_apk_dependencies(next_package)  # Рекурсивный вызов для получения транзитивных зависимостей
    
    return deps

def build_graphviz(deps):
    """Формирование Graphviz диаграммы."""
    graphviz_code = 'digraph G {\n'
    added_links = set()
    
    for src, dest in deps:
        link = f'"{src}" -> "{dest}"'
        if link not in added_links:
            graphviz_code += f'  {link};\n'
            added_links.add(link)
    
    graphviz_code += '}\n'
    return graphviz_code

def main():
    if len(sys.argv) != 3:
        print("Использование: python task_2.py <package_name> <output_path>")
        sys.exit(1)
    
    package_name = sys.argv[1]  # Имя пакета
    output_path = sys.argv[2]  # Путь к файлу для записи результатов
    
    # Получаем зависимости для указанного пакета
    dependencies = fetch_apk_dependencies(package_name)
    
    if not dependencies:
        print(f"Не удалось найти зависимости для пакета {package_name}")
        sys.exit(1)
    
    # Строим Graphviz диаграмму
    graphviz_code = build_graphviz(dependencies)
    
    # Сохраняем результат в указанный файл
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(graphviz_code)

    print(f"Graphviz код сохранён в {output_path}")
    print(graphviz_code)

if __name__ == "__main__":
    main()
