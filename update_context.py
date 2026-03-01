"""
Обновляет автоматические секции .context-summary.md:
  - Дата в заголовке "## Текущее состояние"
  - Дерево файлов между <!-- AUTO: STRUCTURE --> ... <!-- /AUTO: STRUCTURE -->
  - Прогресс между <!-- AUTO: PROGRESS --> ... <!-- /AUTO: PROGRESS -->

Ручные секции (детали разделов, история, текущая работа) не трогаются.

Использование:
  python update_context.py
"""

import os
import re
from datetime import date

CONTEXT_FILE = '.context-summary.md'
MIN_DONE_SIZE_KB = 5  # файл < 5 KB считается незавершённым

PART_NAMES = {
    'part1-basics':         'Часть 1: Основы Go',
    'part2-advanced':       'Часть 2: Продвинутые темы',
    'part3-web-api':        'Часть 3: Web & API',
    'part4-infrastructure': 'Часть 4: Инфраструктура',
    'part5-projects':       'Часть 5: Практические проекты',
    'part6-best-practices': 'Часть 6: Best Practices',
    'part7-interview':      'Часть 7: Лайфкодинг',
}

# Ожидаемое число контент-файлов (без README)
PART_EXPECTED = {
    'part1-basics':         5,
    'part2-advanced':       8,  # 07 + 02a_memory_allocator
    'part3-web-api':        5,
    'part4-infrastructure': 7,
    'part6-best-practices': 4,
    'part7-interview':      5,
}


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


def project_dirs(part5):
    """Папки project* внутри part5-projects."""
    result = []
    try:
        for name in sorted(os.listdir(part5)):
            path = os.path.join(part5, name)
            if os.path.isdir(path) and name.startswith('project'):
                result.append((name, path))
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
    stats = {}  # part -> (pct, label)

    for part in parts:
        expected = PART_EXPECTED.get(part)

        if part == 'part5-projects':
            projects = project_dirs(part)
            done = sum(
                1 for _, ppath in projects
                if all(is_done(f) for f in content_files(ppath))
                   and is_done(os.path.join(ppath, 'README.md'))
            )
            total = len(projects)
            pct = int(done / total * 100) if total else 0
            mark = '✅ 100%' if pct == 100 else f'🚧 {pct}% ({done}/{total} проектов)'
            lines.append(f'├── {part}/  # {mark}')

            for pname, ppath in projects:
                files = content_files(ppath)
                readme = os.path.join(ppath, 'README.md')
                all_ok = all(is_done(f) for f in files) and is_done(readme)
                total_kb = sum(size_kb(f) for f in files) + size_kb(readme)
                st = '✅' if all_ok else '🚧'
                lines.append(f'│   ├── {pname}/  {st} ({total_kb:.0f} KB, {len(files) + 1} файлов)')

            stats[part] = (pct, f'{done}/{total} проектов')

        else:
            files = content_files(part)
            done_files = [f for f in files if is_done(f)]
            total = expected or len(files)
            done = len(done_files)
            pct = int(done / total * 100) if total else 0
            mark = '✅ 100%' if pct == 100 else f'🚧 {pct}% ({done}/{total})'

            connector = '└──' if part == parts[-1] else '├──'
            lines.append(f'{connector} {part}/  # {mark}')
            child_connector = '    ' if part == parts[-1] else '│   '

            for f in files:
                fname = os.path.basename(f)
                kb = size_kb(f)
                st = '✅' if is_done(f) else '🔲'
                lines.append(f'{child_connector}├── {fname:<50} # {st} {kb:.0f} KB')

            stats[part] = (pct, f'{done}/{total}')

    lines.append('```')
    return '\n'.join(lines), stats


# ─── Генерация прогресса ────────────────────────────────────────────────────

def build_progress(stats):
    parts_done = sum(1 for pct, _ in stats.values() if pct == 100)
    total_parts = len(stats)
    overall = int(parts_done / total_parts * 100) if total_parts else 0
    today = date.today().strftime('%Y-%m-%d')

    lines = ['### Прогресс', f'- Общий прогресс курса: ~{overall}%']
    for part in sorted(stats):
        name = PART_NAMES.get(part, part)
        pct, label = stats[part]
        mark = '✅' if pct == 100 else '🚧'
        lines.append(f'- **{name}: {pct}%** {mark} ({label})')

    lines += ['', '---', '', f'**Последнее обновление**: {today}']
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


# ─── Точка входа ────────────────────────────────────────────────────────────

def main():
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
        pct, label = stats[part]
        name = PART_NAMES.get(part, part)
        print(f'  {name}: {pct}% ({label})')


if __name__ == '__main__':
    main()
