import unittest

from mini_claude_code import __version__
from mini_claude_code.cli import main


class BaselineSmokeTest(unittest.TestCase):
    def test_package_has_baseline_version(self) -> None:
        self.assertEqual(__version__, "0.0.0")

    def test_cli_entry_point_runs(self) -> None:
        main()


if __name__ == "__main__":
    unittest.main()

