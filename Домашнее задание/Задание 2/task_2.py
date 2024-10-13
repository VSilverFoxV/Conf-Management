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

