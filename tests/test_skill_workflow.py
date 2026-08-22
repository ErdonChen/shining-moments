import json
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL_PATH = SKILL_DIR / "SKILL.md"
CATALOG_PATH = SKILL_DIR / "references" / "reference-source-map.json"
README_PATH = SKILL_DIR / "README.md"
README_EN_PATH = SKILL_DIR / "README.en.md"


class SkillWorkflowTests(unittest.TestCase):
    def test_source_choice_and_manual_offer_precede_research_and_inventory(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")

        material_type = skill.index("**1. Topic:**")
        media_kinds = skill.index("**2. Media kinds:**")
        automatic_choice = skill.index("**3. Automatic calibration:**")
        manual_offer = skill.index("**Optional manual enhancement:**")
        automatic_research = skill.index("**Run automatic visual calibration:**")
        delivery = skill.index("**4. Delivery mode:**")
        inventory = skill.index("Inventory read-only")

        self.assertLess(material_type, media_kinds)
        self.assertLess(media_kinds, automatic_choice)
        self.assertLess(automatic_choice, manual_offer)
        self.assertLess(manual_offer, automatic_research)
        self.assertLess(automatic_research, delivery)
        self.assertLess(delivery, inventory)

    def test_catalog_has_only_approved_automatic_and_manual_pools(self):
        payload = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        automatic = {
            source["id"]
            for source in payload["sources"]
            if source["access_mode"] == "automatic"
        }
        challenge = {
            source["id"]
            for source in payload["sources"]
            if source["access_mode"] == "manual-challenge"
        }
        login = {
            source["id"]
            for source in payload["sources"]
            if source["access_mode"] == "manual-login"
        }

        self.assertEqual(
            automatic,
            {
                "wikimedia-commons",
                "flickr-public",
                "google-images",
                "google-videos",
            },
        )
        self.assertEqual(challenge, {"unsplash", "pexels"})
        self.assertEqual(
            login, {"youtube", "bilibili", "instagram", "xiaohongshu"}
        )
        self.assertNotIn("x", automatic | challenge | login)
        self.assertNotIn("vimeo", automatic | challenge | login)

    def test_photo_and_video_defaults_route_differently_by_material_type(self):
        payload = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

        def automatic_for(media_kind):
            return {
                source["id"]
                for source in payload["sources"]
                if source["access_mode"] == "automatic"
                and media_kind in source["media_kinds"]
            }

        self.assertEqual(
            automatic_for("photo"),
            {"wikimedia-commons", "flickr-public", "google-images"},
        )
        self.assertEqual(
            automatic_for("video"),
            {"wikimedia-commons", "google-videos"},
        )

    def test_conservative_culling_contract_remains_intact(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("Remove only confidently unusable material as `excluded`", skill)
        self.assertIn("Keep final choice with the user", skill)
        self.assertIn("Never move, overwrite, delete, or recommend deleting originals", skill)
        self.assertIn("10% primary and 25% review ratios are soft second-pass triggers", skill)
        self.assertIn("video ratios use duration, not file count", skill)
        self.assertIn("meaningful, high-quality, usable, and non-redundant", skill)

    def test_readmes_have_one_layered_reference_table_and_authentication_boundary(self):
        readme = README_PATH.read_text(encoding="utf-8")
        readme_en = README_EN_PATH.read_text(encoding="utf-8")

        self.assertEqual(readme.count("## 参考网站"), 1)
        self.assertEqual(readme.count("| 流程层级 | 照片来源 | 视频来源 | 用户操作与使用规则 |"), 1)
        self.assertNotIn("| 类型 | 参考站点 |", readme)
        self.assertIn("永不索取、接收、保存或处理", readme)
        self.assertIn("自动校准仍然继续", readme)
        self.assertIn("Pexels 的一次验证会连续用于照片与视频", readme)

        self.assertEqual(readme_en.count("## Reference sites"), 1)
        self.assertEqual(
            readme_en.count("| Flow layer | Photo sources | Video sources | User action and rule |"),
            1,
        )
        self.assertNotIn("| Category | References |", readme_en)
        self.assertIn("never asks for, receives, stores, or handles", readme_en)
        self.assertIn("automatic calibration still continues", readme_en)
        self.assertIn("One Pexels challenge can be reused for both photos and videos", readme_en)


if __name__ == "__main__":
    unittest.main()
