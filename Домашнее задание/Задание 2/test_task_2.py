import pytest
import requests_mock
from task_2 import fetch_apk_dependencies, build_graphviz

# Тестируем fetch_apk_dependencies
@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as m:
        yield m

def test_fetch_apk_dependencies_single_dependency(mock_requests):
    # Мокируем HTML для одного пакета с одной зависимостью
    package_name = "example-package"
    base_url = f'https://pkgs.alpinelinux.org/package/edge/main/x86_64/{package_name}'
    
    mock_html = '''
    <html>
      <body>
        <details>
          <a href="#">dependency1</a>
        </details>
      </body>
    </html>
    '''
    
    mock_requests.get(base_url, text=mock_html)

    # Мокируем запрос для зависимости 'dependency1'
    mock_html_dependency = '''
    <html>
      <body>
        <details>
        </details>
      </body>
    </html>
    '''
    mock_requests.get(f'https://pkgs.alpinelinux.org/package/edge/main/x86_64/dependency1', text=mock_html_dependency)
    
    # Проверяем, что функция возвращает правильные зависимости
    result = fetch_apk_dependencies(package_name)
    expected = [("example-package", "dependency1")]
    assert result == expected

def test_fetch_apk_dependencies_multiple_dependencies(mock_requests):
    # Мокируем HTML для пакета с несколькими зависимостями
    package_name = "example-package"
    base_url = f'https://pkgs.alpinelinux.org/package/edge/main/x86_64/{package_name}'
    
    mock_html = '''
    <html>
      <body>
        <details>
          <a href="#">dependency1</a>
          <a href="#">dependency2</a>
        </details>
      </body>
    </html>
    '''
    
    mock_requests.get(base_url, text=mock_html)

    # Мокируем запросы для зависимостей 'dependency1' и 'dependency2'
    mock_html_dependency1 = '''
    <html>
      <body>
        <details></details>
      </body>
    </html>
    '''
    mock_requests.get(f'https://pkgs.alpinelinux.org/package/edge/main/x86_64/dependency1', text=mock_html_dependency1)

    mock_html_dependency2 = '''
    <html>
      <body>
        <details></details>
      </body>
    </html>
    '''
    mock_requests.get(f'https://pkgs.alpinelinux.org/package/edge/main/x86_64/dependency2', text=mock_html_dependency2)

    # Проверяем, что функция возвращает правильные зависимости
    result = fetch_apk_dependencies(package_name)
    expected = [("example-package", "dependency1"), ("example-package", "dependency2")]
    assert result == expected

def test_fetch_apk_dependencies_no_dependencies(mock_requests):
    # Мокируем HTML для пакета без зависимостей
    package_name = "example-package"
    base_url = f'https://pkgs.alpinelinux.org/package/edge/main/x86_64/{package_name}'
    
    mock_html = '''
    <html>
      <body>
        <details></details>
      </body>
    </html>
    '''
    
    mock_requests.get(base_url, text=mock_html)
    
    # Проверяем, что функция возвращает пустой список
    result = fetch_apk_dependencies(package_name)
    assert result == []

def test_fetch_apk_dependencies_no_details(mock_requests):
    # Мокируем HTML, где нет элемента <details>
    package_name = "example-package"
    base_url = f'https://pkgs.alpinelinux.org/package/edge/main/x86_64/{package_name}'
    
    mock_html = '''
    <html>
      <body>
      </body>
    </html>
    '''
    
    mock_requests.get(base_url, text=mock_html)
    
    # Проверяем, что функция возвращает пустой список
    result = fetch_apk_dependencies(package_name)
    assert result == []


# Тестируем build_graphviz
def test_build_graphviz_single_dependency():
    deps = [("example-package", "dependency1")]
    result = build_graphviz(deps)
    expected = 'digraph G {\n  "example-package" -> "dependency1";\n}\n'
    assert result == expected

def test_build_graphviz_multiple_dependencies():
    deps = [("example-package", "dependency1"), ("example-package", "dependency2")]
    result = build_graphviz(deps)
    expected = 'digraph G {\n  "example-package" -> "dependency1";\n  "example-package" -> "dependency2";\n}\n'
    assert result == expected

def test_build_graphviz_no_dependencies():
    deps = []
    result = build_graphviz(deps)
    expected = 'digraph G {\n}\n'
    assert result == expected

def test_build_graphviz_duplicate_dependencies():
    deps = [("example-package", "dependency1"), ("example-package", "dependency1")]
    result = build_graphviz(deps)
    expected = 'digraph G {\n  "example-package" -> "dependency1";\n}\n'
    assert result == expected
