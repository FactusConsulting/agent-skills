import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validate_notes import validate


NOTE = '''---
schema: 1
type: session
title: "Example"
status: paused
created: "2026-11-11"
updated: "2026-11-11T09:40:19+01:00"
tags: [notes, experiment]
summary: "Evidence recorded."
next: "Read the result."
related: []
---

# Current state / Next action

Paused.
'''


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.note = self.root / 'session.md'

    def check(self, text):
        self.note.write_text(text)
        return validate(self.note)

    def test_valid_legacy_date_and_offset_timestamp(self):
        self.assertEqual(self.check(NOTE), [])

    def test_invalid_metadata(self):
        for old, new, expected in [
            ('status: paused', 'status: finished', 'invalid status'),
            ('schema: 1', 'schema: true', 'schema must'),
            ('tags: [notes, experiment]', 'tags: [notes]', 'tags must'),
            ('2026-11-11T09:40:19+01:00', '2026-11-11T09:40:19', 'UTC offset'),
            ('2026-11-11T09:40:19+01:00', '2026-13-11', 'ISO date'),
            ('summary: "Evidence recorded."', 'summary: "' + 'x' * 181 + '"', '180 characters'),
            ('status: paused', 'status: paused\nstatus: complete', 'duplicate'),
        ]:
            with self.subTest(expected=expected):
                self.assertTrue(any(expected in e for e in self.check(NOTE.replace(old, new))))

    def test_missing_and_late_frontmatter(self):
        self.assertTrue(self.check('# No metadata'))
        self.assertTrue(self.check(NOTE.replace('schema: 1', '\n' * 24 + 'schema: 1')))

    def test_relative_links_and_fenced_examples(self):
        (self.root / 'evidence.md').write_text('Evidence')
        self.assertEqual(self.check(NOTE + '\n[Evidence](evidence.md#result)\n```md\n[Example](not-real.md)\n```\n'), [])
        self.assertTrue(any('missing local link' in e for e in self.check(NOTE + '[Missing](missing.md)')))
        self.assertTrue(any('missing local link' in e for e in self.check(NOTE.replace('related: []', 'related: [missing.md]'))))

    def test_index_handoff_must_exist_and_be_visible(self):
        (self.root / 'handoff.md').write_text(NOTE)
        index = NOTE.replace('type: session', 'type: index').replace('related: []', 'related: []\ncurrent: [handoff.md]')
        self.assertTrue(any('visible inline link' in e for e in self.check(index)))
        self.assertEqual(self.check(index + '\n[Current](handoff.md)'), [])

    def test_cli_returns_failure_for_invalid_note(self):
        self.note.write_text(NOTE.replace('status: paused', 'status: unknown'))
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('validate_notes.py')), str(self.note)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('invalid status', result.stderr)


if __name__ == '__main__':
    unittest.main()
