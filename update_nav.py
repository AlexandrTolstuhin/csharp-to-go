"""
Обновляет <!-- AUTO: NAV --> блоки во всех файлах курса.

Строит глобальную линейную цепочку файлов и для каждого файла
с маркером генерирует стандартизированную навигацию.

Цепочка:
  part1/README → part1/01 → ... → part1/NN
  → part2/README → part2/01 → ... → part2/NN
  → ...
  → part5/README → part5/project1/README → part5/project1/01 → ...
  → part5/project2/README → part5/project2/01 → ...
  → part6/README → ... → part7/README → ... → part7/NN

Форматы навигации:
  part*/README.md   — [← Назад к оглавлению] | [Предыдущая часть] | [Следующая часть →]
  project*/README   — [← Назад: ...] | [Вперёд: ... →]
  content files     — GitHub-ссылка + [← Назад: ...] | [Вперёд: ... →]

Использование:
  python update_nav.py        # обновить все файлы с маркерами
  python update_nav.py --dry  # вывести результат без записи
"""

import os
import re
import sys

GITHUB_ISSUES = 'https://github.com/AlexandrTolstuhin/csharp-to-go/issues'

START_MARKER = '<!-- AUTO: NAV -->'
END_MARKER   = '<!-- /AUTO: NAV -->'


# ─── Node ─────────────────────────────────────────────────────────────────────

class Node:
    """Узел глобальной цепочки файлов."""
    __slots__ = ('path', 'kind', 'prev', 'next')

    def __init__(self, path, kind):
        # path: нормализованный forward-slash путь относительно корня проекта
        # kind: 'part_readme' | 'content'
        self.path = path.replace('\\', '/')
        self.kind = kind
        self.prev = None
        self.next = None

    def __repr__(self):
        return f'Node({self.path!r}, {self.kind!r})'


# ─── Helpers ──────────────────────────────────────────────────────────────────

def sorted_parts():
    """Отсортированный список директорий part* в корне проекта."""
    return sorted(
        p for p in os.listdir('.')
        if p.startswith('part') and os.path.isdir(p)
    )


def extract_part_name(part):
    """Читает заголовок H1 из README.md части."""
    readme = f'{part}/README.md'
    try:
        m = re.search(r'^#\s+(.+)$', read_file(readme), re.MULTILINE)
        if m:
            return m.group(1).strip()
    except OSError:
        pass
    return part


# ─── Chain builder ────────────────────────────────────────────────────────────

def md_files_in(directory):
    """Все .md файлы кроме README.md, отсортированные по имени."""
    result = []
    try:
        for name in sorted(os.listdir(directory)):
            if name.endswith('.md') and name.lower() != 'readme.md':
                result.append(os.path.join(directory, name).replace('\\', '/'))
    except OSError:
        pass
    return result


def build_chain():
    """Строит полную линейную цепочку всех файлов курса."""
    nodes = []

    for part in sorted_parts():
        # Part README — всегда первый в секции части
        readme = f'{part}/README.md'
        if os.path.exists(readme):
            nodes.append(Node(readme, 'part_readme'))

        for f in md_files_in(part):
            nodes.append(Node(f, 'content'))

    # Связать prev/next
    for i, node in enumerate(nodes):
        node.prev = nodes[i - 1] if i > 0 else None
        node.next = nodes[i + 1] if i < len(nodes) - 1 else None

    return nodes


# ─── File I/O & titles ────────────────────────────────────────────────────────

def read_file(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def extract_short_title(path):
    """Заголовок файла без числового префикса вида '1.2 ' или '2.2a '."""
    try:
        m = re.search(r'^#\s+(.+)$', read_file(path), re.MULTILINE)
        if m:
            return re.sub(r'^\d+\.\w+\s+', '', m.group(1).strip())
    except OSError:
        pass
    return os.path.basename(path)


def rel(from_file, to_path):
    """
    Относительный путь от from_file до to_path.
    Если to_path оканчивается на '/' — это ссылка на директорию (сохраняется).
    """
    from_file = from_file.replace('\\', '/')
    to_path   = to_path.replace('\\', '/')
    is_dir    = to_path.endswith('/')
    to_clean  = to_path.rstrip('/')

    from_dir = os.path.dirname(from_file)
    r = os.path.relpath(to_clean, from_dir).replace('\\', '/')
    if not r.startswith('..'):
        r = './' + r
    return r + ('/' if is_dir else '')


def node_link(node, from_file):
    """
    Возвращает (rel_path, display_title) для ссылки на node из from_file.
    part_readme → directory link + H1 из README.md части
    content     → явный путь к файлу + короткий заголовок
    """
    if node.kind == 'part_readme':
        part = node.path.split('/')[0]
        return rel(from_file, f'{part}/'), extract_part_name(part)
    else:
        return rel(from_file, node.path), extract_short_title(node.path)


# ─── Navigation generators ────────────────────────────────────────────────────

def gen_part_readme_nav(node):
    """
    Навигация для part*/README.md.
    Формат: [← Назад к оглавлению] | [Предыдущая часть: ...] | [Следующая часть: ... →]
    """
    part  = node.path.split('/')[0]
    parts = sorted_parts()
    idx   = parts.index(part)
    links = ['[← Назад к оглавлению](../README.md)']

    if idx > 0:
        prev_part = parts[idx - 1]
        links.append(f'[Предыдущая часть: {extract_part_name(prev_part)}](../{prev_part}/)')

    if idx < len(parts) - 1:
        next_part = parts[idx + 1]
        links.append(f'[Следующая часть: {extract_part_name(next_part)} →](../{next_part}/)')

    return ' | '.join(links)


def gen_content_nav(node):
    """
    Навигация для content-файлов.
    GitHub-ссылка + [← Назад: ...] | [Вперёд: ... →]
    """
    path  = node.path
    links = []

    # ── PREV ──────────────────────────────────────────────────────────────────
    if node.prev is None:
        # Первый файл в курсе — не должно быть, но на всякий случай
        links.append('[← Назад к оглавлению](../README.md)')
    elif node.prev.kind == 'part_readme':
        prev_rel = rel(path, node.prev.path)
        links.append(f'[← Назад к оглавлению]({prev_rel})')
    else:
        prev_rel, prev_title = node_link(node.prev, path)
        links.append(f'[← Назад: {prev_title}]({prev_rel})')

    # ── NEXT ──────────────────────────────────────────────────────────────────
    if node.next is None:
        # Последний файл курса — ссылка на оглавление своей части
        part = path.split('/')[0]
        part_readme_rel = rel(path, f'{part}/README.md')
        links.append(f'[К оглавлению части]({part_readme_rel})')
    else:
        next_rel, next_title = node_link(node.next, path)
        links.append(f'[Вперёд: {next_title} →]({next_rel})')

    nav_line = ' | '.join(links)

    github = f'**Вопросы?** Открой issue на [GitHub]({GITHUB_ISSUES})'
    return f'{github}\n\n{nav_line}'


def generate_nav(node):
    if node.kind == 'part_readme':
        return gen_part_readme_nav(node)
    else:
        return gen_content_nav(node)


# ─── Marker replacement ───────────────────────────────────────────────────────

def replace_nav_block(content, new_body):
    pattern = re.compile(
        re.escape(START_MARKER) + r'.*?' + re.escape(END_MARKER),
        re.DOTALL
    )
    replacement = f'{START_MARKER}\n{new_body}\n{END_MARKER}'
    updated, n = pattern.subn(replacement, content)
    return updated, n > 0


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    dry = '--dry' in sys.argv
    if dry:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    nodes = build_chain()

    if '--print-chain' in sys.argv:
        for n in nodes:
            print(f'  {n.kind:<16} {n.path}')
        return

    updated = skipped = warned = 0

    for node in nodes:
        path = node.path
        if not os.path.exists(path):
            continue

        try:
            content = read_file(path)
        except OSError as e:
            print(f'  ERR: {path}: {e}')
            continue

        if START_MARKER not in content:
            skipped += 1
            continue

        nav = generate_nav(node)
        new_content, found = replace_nav_block(content, nav)

        if not found:
            print(f'  WARN: маркер не заменён в {path}')
            warned += 1
            continue

        if new_content == content:
            skipped += 1
            continue

        if dry:
            print(f'--- {path} ---')
            print(nav)
            print()
        else:
            write_file(path, new_content)
            print(f'  Обновлён: {path}')
            updated += 1

    action = 'Покажет' if dry else 'Итого'
    print(f'\n{action}: обновлено {updated}, без изменений {skipped}, предупреждений {warned}')


if __name__ == '__main__':
    main()
