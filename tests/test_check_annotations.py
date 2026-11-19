import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CheckAnnotationTests(unittest.TestCase):
    def run_fixture(self, body, actions=True):
        env = dict(os.environ, GITHUB_ACTIONS='true' if actions else 'false')
        return subprocess.run([sys.executable, 'scripts/annotated_check.py', sys.executable, '-c', body],
                              cwd=ROOT, env=env, capture_output=True, text=True)

    def test_failure_exit_and_useful_diagnostic_are_preserved(self):
        result = self.run_fixture("print('fixture failure: 100% expected'); raise SystemExit(7)")
        self.assertEqual(7, result.returncode)
        self.assertIn('fixture failure: 100% expected', result.stdout)
        self.assertIn('::error title=Verification command failed::', result.stdout)
        self.assertIn('100%25 expected%0A', result.stdout)

    def test_success_never_creates_a_failure_annotation(self):
        result = self.run_fixture("print('fixture success')")
        self.assertEqual(0, result.returncode)
        self.assertNotIn('::error', result.stdout)

    def test_local_failure_retains_status_without_workflow_syntax(self):
        result = self.run_fixture('raise SystemExit(2)', actions=False)
        self.assertEqual(2, result.returncode)
        self.assertNotIn('::error', result.stdout)


if __name__ == '__main__':
    unittest.main()
