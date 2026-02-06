import unittest
from pathlib import Path


class SkillHeaderComplianceTests(unittest.TestCase):
    def test_skill_requires_ai_bot_header(self) -> None:
        content = Path("mailchannels-email-api/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("headers.X-AI-Bot", content)
        self.assertIn('"X-AI-Bot": "openclaw-2026.2.4"', content)

    def test_skill_requires_list_unsubscribe_header(self) -> None:
        content = Path("mailchannels-email-api/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("headers.List-Unsubscribe", content)
        self.assertIn('"List-Unsubscribe": "<mailto:unsubscribe@example.com>"', content)

    def test_skill_blocks_send_when_headers_missing(self) -> None:
        content = Path("mailchannels-email-api/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("If either header is missing, do not send", content)


if __name__ == "__main__":
    unittest.main()
