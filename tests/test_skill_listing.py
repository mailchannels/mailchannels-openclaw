import re
import unittest
from pathlib import Path


def skill_description() -> str:
    content = Path("mailchannels-email-api/SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"^description: (.+)$", content, re.MULTILINE)
    assert match, "SKILL.md frontmatter has no description"
    return match.group(1)


class SkillListingTests(unittest.TestCase):
    def test_description_leads_with_sending_app_email(self) -> None:
        description = skill_description()
        self.assertTrue(description.startswith("Send your app's transactional email"))
        self.assertIn("signed delivery webhooks", description)
        # Agent Skills spec limit for the description field.
        self.assertLessEqual(len(description), 1024)

    def test_listing_text_claims_only_what_the_skill_does(self) -> None:
        texts = [skill_description(), Path("README.md").read_text(encoding="utf-8")]
        for text in texts:
            for claim in ("inbound", "idempotency", "sandbox", "test mode", "sub-account"):
                self.assertNotIn(claim, text.lower())

    def test_publish_script_targets_existing_clawhub_listing(self) -> None:
        script = Path("publish-skill.sh").read_text(encoding="utf-8")
        self.assertIn('SLUG="mailchannels"', script)


if __name__ == "__main__":
    unittest.main()
