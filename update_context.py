"""
Обновляет автоматические секции .context-summary.md:
  - Дата в заголовке "## Текущее состояние"
  - Дерево файлов между <!-- AUTO: STRUCTURE --> ... <!-- /AUTO: STRUCTURE -->
  - Прогресс между <!-- AUTO: PROGRESS --> ... <!-- /AUTO: PROGRESS -->

При указании --version обновляет <!-- AUTO: VERSION --> во всех .md файлах проекта.

Ручные секции (детали разделов, история, текущая работа) не трогаются.

Использование:
  python update_context.py
  python update_context.py --version "0.9.0 (описание)"
"""

import argparse
import os
import re
from datetime import date

CONTEXT_FILE = '.context-summary.md'
MIN_DONE_SIZE_KB = 5  # файл < 5 KB считается незавершённым


# ─── Файловый анализ ────────────────────────────────────────────────────────

def size_kb(path):
    try:
        return os.path.getsize(path) / 1024
    except OSError:
        return 0


def is_done(path):
    return size_kb(path) >= MIN_DONE_SIZE_KB


def content_files(directory):
    """Все .md файлы в папке кроме README, отсортированные."""
    result = []
    try:
        for name in sorted(os.listdir(directory)):
            if name.endswith('.md') and name.lower() != 'readme.md':
                result.append(os.path.join(directory, name))
    except OSError:
        pass
    return result



# ─── Генерация дерева ───────────────────────────────────────────────────────

def build_tree():
    parts = sorted(
        p for p in os.listdir('.')
        if p.startswith('part') and os.path.isdir(p)
    )

    lines = ['```', 'csharp-to-go/']
    stats = {}  # part -> (count, label, total_kb)

    for part in parts:
        files = content_files(part)
        total_kb = sum(size_kb(f) for f in files)

        connector = '└──' if part == parts[-1] else '├──'
        lines.append(f'{connector} {part}/  # {len(files)} файлов, {total_kb:.0f} KB')
        child_connector = '    ' if part == parts[-1] else '│   '

        for f in files:
            fname = os.path.basename(f)
            kb = size_kb(f)
            st = '✅' if is_done(f) else '🔲'
            lines.append(f'{child_connector}├── {fname:<50} # {st} {kb:.0f} KB')

        stats[part] = (len(files), f'{len(files)} файлов', total_kb)

    lines.append('```')
    return '\n'.join(lines), stats


# ─── Генерация прогресса ────────────────────────────────────────────────────

def build_progress(stats):
    today = date.today().strftime('%Y-%m-%d')
    total_kb = sum(kb for _, _, kb in stats.values())

    lines = ['### Прогресс']
    for part in sorted(stats):
        count, label, kb = stats[part]
        lines.append(f'- **{part}**: {label}, {kb:.0f} KB')

    lines += [f'- **Итого**: {total_kb:.0f} KB', '', '---', '', f'**Последнее обновление**: {today}']
    return '\n'.join(lines)


# ─── Замена блока между маркерами ───────────────────────────────────────────

def replace_block(content, tag, new_body):
    start_tag = f'<!-- AUTO: {tag} -->'
    end_tag   = f'<!-- /AUTO: {tag} -->'
    pattern = re.compile(
        re.escape(start_tag) + r'.*?' + re.escape(end_tag),
        re.DOTALL
    )
    replacement = f'{start_tag}\n{new_body}\n{end_tag}'
    updated, n = pattern.subn(replacement, content)
    if n == 0:
        print(f'  WARN: маркеры <!-- AUTO: {tag} --> не найдены в файле')
    return updated


# ─── Обновление версии ──────────────────────────────────────────────────────

def collect_md_files():
    """Все .md файлы в проекте (рекурсивно), кроме .git."""
    result = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d != '.git']
        for name in files:
            if name.endswith('.md'):
                result.append(os.path.join(root, name))
    return result


def update_version(version_str):
    """Заменяет содержимое <!-- AUTO: VERSION --> во всех .md файлах проекта."""
    files = collect_md_files()
    updated = []
    for path in files:
        with open(path, encoding='utf-8') as f:
            content = f.read()
        if '<!-- AUTO: VERSION -->' not in content:
            continue
        new_content = replace_block(content, 'VERSION', f'**Версия**: {version_str}')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        updated.append(path)
    return updated


# ─── Точка входа ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Обновляет .context-summary.md и версию проекта')
    parser.add_argument('--version', metavar='STR',
                        help='Строка версии, например: "0.9.0 (описание)"')
    args = parser.parse_args()

    with open(CONTEXT_FILE, encoding='utf-8') as f:
        content = f.read()

    today = date.today().strftime('%Y-%m-%d')

    # 1. Обновить дату в заголовке
    content = re.sub(
        r'(## Текущее состояние \()\d{4}-\d{2}-\d{2}(\))',
        rf'\g<1>{today}\2',
        content
    )

    # 2. Обновить дерево файлов
    tree, stats = build_tree()
    content = replace_block(content, 'STRUCTURE', f'### Структура проекта\n{tree}')

    # 3. Обновить прогресс
    progress = build_progress(stats)
    content = replace_block(content, 'PROGRESS', progress)

    with open(CONTEXT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'Обновлён {CONTEXT_FILE} ({today})')
    for part in sorted(stats):
        count, label, kb = stats[part]
        print(f'  {part}: {label}, {kb:.0f} KB')

    # 4. Обновить версию во всех файлах (если передана)
    if args.version:
        updated = update_version(args.version)
        if updated:
            print(f'\nВерсия "{args.version}" обновлена в {len(updated)} файл(ах):')
            for path in updated:
                print(f'  {path}')
        else:
            print('\nWARN: файлы с <!-- AUTO: VERSION --> не найдены')


if __name__ == '__main__':
    main()
