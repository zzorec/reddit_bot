import unittest
from datetime import date

from reddit_bot.util.date_util import format_time, format_date, get_active_season


class TestFormattingUtil(unittest.TestCase):

    def setUp(self):
        self.date_string = "2024-02-07T12:00:00"

    def test_format_date_short_include_year(self):
        # Test formatting date with short format and including year.
        expected_output = "07 Feb 2024"
        self.assertEqual(format_date(self.date_string, True, True), expected_output)

    def test_format_date_short_exclude_year(self):
        # Test formatting date with short format and excluding year.
        expected_output = "07 Feb"
        self.assertEqual(format_date(self.date_string, True, False), expected_output)

    def test_format_date_long_include_year(self):
        # Test formatting date with long format and including year.
        expected_output = "Wednesday, 07 February 2024"
        self.assertEqual(format_date(self.date_string, False, True), expected_output)

    def test_format_date_long_exclude_year(self):
        # Test formatting date with long format and excluding year.
        expected_output = "Wednesday, 07 February"
        self.assertEqual(format_date(self.date_string, False, False), expected_output)

    def test_format_time(self):
        # Test formatting time.
        expected_output = "12:00"
        self.assertEqual(format_time(self.date_string), expected_output)

    def test_active_season(self):
        self.assertEqual(get_active_season(date(2024, 10, 31)), 2024)
        self.assertEqual(get_active_season(date(2025, 3, 31)), 2024)
        self.assertEqual(get_active_season(date(2025, 10, 31)), 2025)


if __name__ == "__main__":
    unittest.main()
