"""
Обновляет <!-- AUTO: STRUCTURE --> блок в корневом README.md.

Строит секцию "## Структура курса" на основе README.md каждой части:
- заголовок раздела из первого # heading
- список файлов из AUTO: MATERIALS блока
  - обычные части: плоский список файлов
  - part5-projects: проекты со списком файлов

Использование:
  python update_root_readme.py        # обновить README.md
  python update_root_readme.py --dry  # вывести результат без записи
"""

import os
import re
import sys

PARTS_ORDER = [
    'part1-basics',
    'part2-advanced',
    'part3-web-api',
    'part4-infrastructure',
    'part5-project1-url-shortener',
    'part5-project2-ecommerce',
    'part6-best-practices',
    'part7-interview',
]

START_MARKER = '<!-- AUTO: STRUCTURE -->'
END_MARKER   = '<!-- /AUTO: STRUCTURE -->'

MAT_START = '<!-- AUTO: MATERIALS -->'
MAT_END   = '<!-- /AUTO: MATERIALS -->'


# ─── Helpers ──────────────────────────────────────────────────────────────────

def read_file(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def extract_title(content):
    """Первый заголовок # в файле."""
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return m.group(1).strip() if m else ''


def extract_materials_content(content):
    """Содержимое между AUTO: MATERIALS маркерами."""
    m = re.search(
        re.escape(MAT_START) + r'(.*?)' + re.escape(MAT_END),
        content, re.DOTALL
    )
    return m.group(1).strip() if m else ''


def prefix_path(part, rel_path):
    """
    Преобразует путь, относительный к директории части,
    в путь относительно корня проекта.
    ./01_file.md → ./part1-basics/01_file.md
    ./project1/  → ./part5-projects/project1/
    """
    stripped = rel_path.lstrip('.').lstrip('/')
    return f'./{part}/{stripped}'


# ─── Parsers ──────────────────────────────────────────────────────────────────

def parse_top_entries(materials_content):
    """
    Парсит заголовки ### N. [Title](./path) из блока MATERIALS.
    Возвращает список (title, path).
    """
    pattern = re.compile(
        r'^###\s+\d+\.\s+\[([^\]]+)\]\(([^)]+)\)',
        re.MULTILINE
    )
    return [(m.group(1), m.group(2)) for m in pattern.finditer(materials_content)]



# ─── Section builders ─────────────────────────────────────────────────────────

def build_section_regular(part, title, materials_content):
    """Секция для обычной части: заголовок + плоский список файлов."""
    entries = parse_top_entries(materials_content)
    lines = [f'### [{title}](./{part}/)']
    lines.append('')
    for file_title, rel_path in entries:
        full_path = prefix_path(part, rel_path)
        lines.append(f'- [{file_title}]({full_path})')
    return '\n'.join(lines)



# ─── Main builder ─────────────────────────────────────────────────────────────

def build_structure():
    """Строит полное содержимое блока STRUCTURE."""
    sections = []

    for part in PARTS_ORDER:
        readme_path = f'{part}/README.md'
        if not os.path.exists(readme_path):
            continue

        content = read_file(readme_path)
        title   = extract_title(content)
        mats    = extract_materials_content(content)

        if not mats:
            sections.append(f'### [{title}](./{part}/)')
            continue

        section = build_section_regular(part, title, mats)

        sections.append(section)

    return '\n\n---\n\n'.join(sections)


def replace_structure_block(content, new_body):
    pattern = re.compile(
        re.escape(START_MARKER) + r'.*?' + re.escape(END_MARKER),
        re.DOTALL
    )
    replacement = f'{START_MARKER}\n{new_body}\n{END_MARKER}'
    updated, n = pattern.subn(replacement, content)
    return updated, n > 0


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    dry = '--dry' in sys.argv
    if dry:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    readme_path = 'README.md'
    content = read_file(readme_path)

    if START_MARKER not in content:
        print(f'WARN: маркер {START_MARKER!r} не найден в {readme_path}')
        print('Добавьте маркеры вручную и повторите запуск.')
        return

    structure = build_structure()
    new_content, found = replace_structure_block(content, structure)

    if not found:
        print(f'WARN: маркер не заменён в {readme_path}')
        return

    if dry:
        print(structure)
    else:
        if new_content == content:
            print('Без изменений.')
        else:
            write_file(readme_path, new_content)
            print(f'Обновлён: {readme_path}')


if __name__ == '__main__':
    main()
