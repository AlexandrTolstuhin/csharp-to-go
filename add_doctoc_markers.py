"""
Добавляет doctoc-маркеры в .md файлы с разделом "## Содержание",
затем запускает doctoc для генерации TOC.

Использование:
  python add_doctoc_markers.py                   # весь проект
  python add_doctoc_markers.py part2-advanced/   # конкретная папка
  python add_doctoc_markers.py file.md           # конкретный файл
"""

import re
import os
import sys
import subprocess

SKIP_FILES = {'CLAUDE.md', '.context-summary.md'}

DOCTOC_MARKERS = (
    "<!-- START doctoc generated TOC please keep comment here to allow auto update -->\n"
    "<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->\n"
    "<!-- END doctoc generated TOC please keep comment here to allow auto update -->"
)


def add_markers(path):
    """Добавляет маркеры в файл если их ещё нет. Возвращает True если файл изменён."""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if '<!-- START doctoc' in content:
        return False  # уже есть маркеры

    if '## Содержание' not in content:
        return False

    # Заменяем ручной список после ## Содержание на маркеры
    pattern = r'(## Содержание\n)(\n?([ \t]*-[^\n]*\n|[ \t]+[^\n]*\n)*)'

    def replacer(m):
        return m.group(1) + '\n' + DOCTOC_MARKERS + '\n'

    new_content, count = re.subn(pattern, replacer, content)

    if count == 0:
        print(f'  WARN (нет списка после ## Содержание): {path}')
        return False

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f'  Добавлены маркеры: {path}')
    return True


def collect_files(target):
    """Собирает .md файлы из файла или директории."""
    if os.path.isfile(target):
        fname = os.path.basename(target)
        if fname in SKIP_FILES or not fname.endswith('.md'):
            return []
        return [target]

    result = []
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules'}]
        for fname in files:
            if not fname.endswith('.md'):
                continue
            if fname in SKIP_FILES:
                continue
            result.append(os.path.join(root, fname))
    return result


def run_doctoc(target):
    """Запускает npx doctoc на указанном пути."""
    print(f'\nЗапускаю doctoc для: {target}')
    result = subprocess.run(
        ['npx', 'doctoc', target, '--github', '--notitle', '--update-only'],
        capture_output=True, text=True
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else '.'

    print(f'Обрабатываю: {target}\n')
    files = collect_files(target)

    added = []
    for fpath in files:
        if add_markers(fpath):
            added.append(fpath)

    if added:
        print(f'\nМаркеры добавлены в {len(added)} файл(ов).')
    else:
        print('Новых файлов для добавления маркеров не найдено.')

    run_doctoc(target)


if __name__ == '__main__':
    main()
