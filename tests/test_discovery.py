import unittest

from discovery import make_announcement, parse_announcement


class AnnouncementTest(unittest.TestCase):
    def test_make_and_parse(self):
        message = make_announcement("LAPTOP-SASHA")
        self.assertEqual(message, "sea-battle:5050:LAPTOP-SASHA")
        self.assertEqual(parse_announcement(message), "LAPTOP-SASHA")

    def test_name_with_colon(self):
        self.assertEqual(parse_announcement("sea-battle:5050:PC:1"), "PC:1")

    def test_empty_name(self):
        self.assertEqual(parse_announcement("sea-battle:5050:"), "Без имени")

    def test_foreign_message(self):
        self.assertIsNone(parse_announcement("hello"))
        self.assertIsNone(parse_announcement("other-game:5050:PC"))

    def test_wrong_port(self):
        self.assertIsNone(parse_announcement("sea-battle:6000:PC"))

    def test_old_format(self):
        self.assertIsNone(parse_announcement("sea-battle:5050"))


if __name__ == "__main__":
    unittest.main()
