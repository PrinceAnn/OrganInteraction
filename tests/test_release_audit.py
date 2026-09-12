import tempfile
import unittest
from pathlib import Path

from tools.audit_release import audit


class ReleaseAuditTests(unittest.TestCase):
    def test_blocks_data_file_types(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "private_table.csv").write_text("a,b\n1,2\n", encoding="utf-8")
            failures = audit(root, [])
            self.assertTrue(any("blocked file type" in failure for failure in failures))

    def test_blocks_runtime_supplied_token_in_content_and_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            token = "restricted_source_code"
            (root / "notes.md").write_text(f"source={token}\n", encoding="utf-8")
            self.assertTrue(audit(root, [token]))
            (root / "notes.md").unlink()
            (root / f"{token}_adapter.py").write_text("pass\n", encoding="utf-8")
            self.assertTrue(audit(root, [token]))


if __name__ == "__main__":
    unittest.main()
