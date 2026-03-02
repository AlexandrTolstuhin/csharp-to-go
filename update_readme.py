"""
Обновляет README.md в разделах курса.

Секция <!-- AUTO: MATERIALS --> генерируется из содержания .md файлов раздела
(верхнеуровневые пункты doctoc-оглавления каждого файла).

Описание (## Описание) и навигация в конце — только вручную.

Использование:
  python update_readme.py                # обновить AUTO: MATERIALS во всех разделах
  python update_readme.py part2-advanced # обновить конкретный раздел
  python update_readme.py --init         # первичная инициализация: убрать лишние секции,
                                         # вставить маркеры (все разделы)
  python update_readme.py --init part1-basics  # то же для конкретного раздела
"""

import os
import re
import sys

START_MARKER = '<!-- AUTO: MATERIALS -->'
END_MARKER = '<!-- /AUTO: MATERIALS -->'


# ─── Утилиты ────────────────────────────────────────────────────────────────

def read_file(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def content_files(directory):
    """Все .md файлы кроме README.md, отсортированные."""
    result = []
    try:
        for name in sorted(os.listdir(directory)):
            if name.endswith('.md') and name.lower() != 'readme.md':
                result.append((name, os.path.join(directory, name)))
    except OSError:
        pass
    return result



# ─── Извлечение данных из файлов ────────────────────────────────────────────

def extract_title(content):
    """Первый # заголовок файла."""
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return m.group(1).strip() if m else None


def extract_toc_top_items(content):
    """Верхнеуровневые пункты doctoc-оглавления (строки вида '- [Текст](#...)')."""
    start = content.find('<!-- START doctoc')
    end = content.find('<!-- END doctoc')
    if start == -1 or end == -1:
        return []

    toc_block = content[start:end]
    items = []
    for line in toc_block.splitlines():
        m = re.match(r'^- \[([^\]]+)\]', line)
        if m:
            items.append(m.group(1))
    return items


# ─── Генерация блока Материалы ───────────────────────────────────────────────

def build_materials(part_dir):
    """Генерирует ## Материалы для раздела."""
    files = content_files(part_dir)
    if not files:
        return '## Материалы\n\n_Материалы в разработке._'

    lines = ['## Материалы', '']
    for i, (fname, fpath) in enumerate(files, 1):
        try:
            file_content = read_file(fpath)
        except OSError:
            continue

        title = re.sub(r'^\d+\.(\w+)?\s+', '', extract_title(file_content) or fname)
        toc_items = extract_toc_top_items(file_content)

        lines.append(f'### {i}. [{title}](./{fname})')
        lines.append('')
        for item in toc_items:
            lines.append(f'- {item}')
        lines.append('')

    while lines and lines[-1] == '':
        lines.pop()

    return '\n'.join(lines)




# ─── Работа с маркерами ─────────────────────────────────────────────────────

def replace_materials_block(content, new_body):
    """Заменяет содержимое между AUTO: MATERIALS маркерами."""
    pattern = re.compile(
        re.escape(START_MARKER) + r'.*?' + re.escape(END_MARKER),
        re.DOTALL
    )
    replacement = f'{START_MARKER}\n{new_body}\n{END_MARKER}'
    updated, n = pattern.subn(replacement, content)
    return updated, n > 0


# ─── Init: первичная перестройка файла ───────────────────────────────────────

def extract_description(content):
    """Извлекает секцию ## Описание целиком (до следующего ## или конца)."""
    m = re.search(r'(^## Описание\n[\s\S]*?)(?=\n## |\Z)', content, re.MULTILINE)
    return m.group(1).rstrip() if m else ''


def extract_navigation(content):
    """Извлекает блок навигации: последний '---' и строку(и) со ссылками."""
    m = re.search(r'(\n---\n\n\[[\s\S]+)$', content)
    return m.group(1) if m else ''


def init_readme(part_dir):
    """
    Первичная инициализация README.md:
    - оставляет заголовок, описание, навигацию
    - удаляет все остальные секции
    - вставляет AUTO: MATERIALS маркеры с контентом
    """
    readme_path = os.path.join(part_dir, 'README.md')
    if not os.path.exists(readme_path):
        print(f'  SKIP: {readme_path} не найден')
        return

    content = read_file(readme_path)

    if START_MARKER in content:
        print(f'  (маркеры уже есть, обновляю контент): {readme_path}')
        update_readme(part_dir)
        return

    # Заголовок
    title_m = re.match(r'^(# [^\n]+)\n', content)
    title_line = (title_m.group(1) + '\n') if title_m else ''

    # Описание
    description = extract_description(content)

    # Навигация
    navigation = extract_navigation(content)

    # Материалы
    materials = build_materials(part_dir)

    new_content = (
        title_line + '\n'
        + (description + '\n\n' if description else '')
        + f'{START_MARKER}\n{materials}\n{END_MARKER}\n'
        + navigation
    )

    write_file(readme_path, new_content)
    print(f'  Инициализирован: {readme_path}')


# ─── Update: обновить только AUTO блок ───────────────────────────────────────

def update_readme(part_dir):
    """Обновляет AUTO: MATERIALS блок в существующем README.md."""
    readme_path = os.path.join(part_dir, 'README.md')
    if not os.path.exists(readme_path):
        print(f'  SKIP: {readme_path} не найден')
        return

    content = read_file(readme_path)
    materials = build_materials(part_dir)
    new_content, found = replace_materials_block(content, materials)

    if not found:
        print(f'  WARN: маркеры не найдены в {readme_path} — запустите с --init')
        return

    write_file(readme_path, new_content)
    print(f'  Обновлён: {readme_path}')


# ─── Точка входа ─────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    init_mode = '--init' in args
    targets = [a for a in args if not a.startswith('--')]

    if not targets:
        targets = sorted(p for p in os.listdir('.') if p.startswith('part') and os.path.isdir(p))

    for part_dir in targets:
        print(f'{part_dir}:')
        if init_mode:
            init_readme(part_dir)
        else:
            update_readme(part_dir)


if __name__ == '__main__':
    main()
