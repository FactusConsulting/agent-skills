#!/usr/bin/env python3
"""Validate note metadata and local inline links; not agent behavior or evidence truth.

Requires Python 3.10+ and PyYAML. Usage: python3 validate_notes.py NOTES_DIRECTORY
"""
import argparse
from datetime import date, datetime
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml


class NoteLoader(yaml.SafeLoader):
    pass


def mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in result:
            raise ValueError(f'non-string or duplicate metadata key: {key!r}')
        result[key] = loader.construct_object(value_node)
    return result


NoteLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
REQUIRED = {'schema', 'type', 'title', 'status', 'created', 'updated', 'tags',
            'summary', 'next', 'related'}


def validate(path):
    errors = []
    def fail(message):
        errors.append(f'{path}: {message}')
    try:
        text = path.read_text(encoding='utf-8')
        lines = text.splitlines()
        end = lines.index('---', 1) if lines and lines[0] == '---' else -1
        if end < 1 or end >= 24:
            fail('frontmatter must start at line 1 and close within line 24')
            return errors
        data = yaml.load('\n'.join(lines[1:end]), Loader=NoteLoader)
        if not isinstance(data, dict):
            fail('frontmatter must be a mapping')
            return errors
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        fail(str(exc))
        return errors
    missing = REQUIRED - data.keys()
    if missing:
        fail(f'missing fields: {", ".join(sorted(missing))}')
    if type(data.get('schema')) is not int or data['schema'] != 1:
        fail('schema must be integer 1')
    if data.get('type') not in ('index', 'session', 'experiment'):
        fail('invalid type')
    if data.get('status') not in ('active', 'paused', 'blocked', 'complete'):
        fail('invalid status')
    for field in ('title', 'summary', 'next'):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip() or '\n' in value:
            fail(f'{field} must be nonblank single-line text')
        elif field != 'title' and len(value) > 180:
            fail(f'{field} exceeds 180 characters')
    for field in ('created', 'updated'):
        value = data.get(field)
        try:
            if isinstance(value, (date, datetime)):
                value = value.isoformat()
            if not isinstance(value, str):
                raise ValueError()
            if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                date.fromisoformat(value)
            else:
                parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
                if 'T' not in value or parsed.utcoffset() is None:
                    raise ValueError()
        except ValueError:
            fail(f'{field} must be an ISO date or timestamp with UTC offset')
    tags = data.get('tags')
    if (not isinstance(tags, list) or not 2 <= len(tags) <= 5
            or any(not isinstance(t, str) or not t.strip() for t in tags)):
        fail('tags must contain 2–5 nonblank strings')
    # Fenced examples are not live links. Only inline Markdown links are checked.
    body = re.sub(r'^(`{3,}|~{3,}).*?^\1\s*$', '',
                  '\n'.join(lines[end + 1:]), flags=re.M | re.S)
    links = re.findall(r'\]\(([^\s)]+)\)', body)
    for field in ('related', 'current'):
        if field == 'current' and data.get('type') != 'index':
            continue
        values = data.get(field)
        if not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values):
            fail(f'{field} must be a list of nonblank relative paths')
            continue
        for value in values:
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc or Path(parsed.path).is_absolute():
                fail(f'{field} must use relative paths: {value}')
            if field == 'current' and value not in links:
                fail(f'current handoff lacks a visible inline link: {value}')
        links.extend(values)
    for target in set(links):
        parsed = urlsplit(target.strip('<>'))
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        if not (path.parent / unquote(parsed.path)).exists():
            fail(f'missing local link target: {target}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    paths = sorted(args.path.rglob('*.md')) if args.path.is_dir() else [args.path]
    if not paths:
        parser.error('no Markdown notes found')
    errors = [error for path in paths for error in validate(path)]
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'PASS: {len(paths)} note(s); metadata and local inline links only.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
