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

        material_type = skill.index("**Material type:**")
        automatic_choice = skill.index("**Show and select automatic public sources:**")
        manual_offer = skill.index("**Offer optional manual enhancement:**")
        automatic_research = skill.index("**Run automatic visual calibration:**")
        inventory = skill.index("Inventory read-only")

        self.assertLess(material_type, automatic_choice)
        self.assertLess(automatic_choice, manual_offer)
        self.assertLess(manual_offer, automatic_research)
        self.assertLess(automatic_research, inventory)

    def test_catalog_has_only_approved_automatic_and_manual_pools(self):
        payload = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        automatic = {
            source["id"]
            for source in payload["sources"]
            if source["access_mode"] == "automatic"
        }
        manual = {
            source["id"]
            for source in payload["sources"]
            if source["access_mode"] == "manual-enhancement"
        }

        self.assertEqual(
            automatic,
            {
                "unsplash",
                "pexels-photos",
                "flickr-public",
                "wikimedia-commons-photos",
                "pexels-videos",
                "pixabay-videos",
                "mixkit",
                "wikimedia-commons-videos",
            },
        )
        self.assertEqual(
            manual,
            {"youtube", "bilibili", "vimeo", "instagram", "xiaohongshu"},
        )
        self.assertNotIn("x", automatic | manual)

    def test_photo_and_video_defaults_route_differently_by_material_type(self):
        payload = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

        def defaults(material_type, media_kind):
            return {
                source["id"]
                for source in payload["sources"]
                if source["access_mode"] == "automatic"
                and media_kind in source["media_kinds"]
                and material_type in source.get("default_for", [])
            }

        self.assertEqual(
            defaults("documentary-culture", "photo"),
            {"pexels-photos", "flickr-public", "wikimedia-commons-photos"},
        )
        self.assertEqual(
            defaults("portrait", "photo"),
            {"unsplash", "pexels-photos", "flickr-public"},
        )
        self.assertEqual(
            defaults("documentary-culture", "video"),
            {"pexels-videos", "pixabay-videos", "wikimedia-commons-videos"},
        )

    def test_conservative_culling_contract_remains_intact(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("Remove only confidently unusable material as `excluded`", skill)
        self.assertIn("Keep final choice with the user", skill)
        self.assertIn("Never move, overwrite, delete, or recommend deleting originals", skill)

    def test_readmes_have_one_layered_reference_table_and_authentication_boundary(self):
        readme = README_PATH.read_text(encoding="utf-8")
        readme_en = README_EN_PATH.read_text(encoding="utf-8")

        self.assertEqual(readme.count("## 参考网站"), 1)
        self.assertEqual(readme.count("| 来源层级 | 照片网站 | 视频网站 | 使用规则 |"), 1)
        self.assertNotIn("| 类型 | 参考站点 |", readme)
        self.assertIn("永不索取、接收、保存或处理", readme)
        self.assertIn("流程会退回并继续使用自动公开来源", readme)

        self.assertEqual(readme_en.count("## Reference sites"), 1)
        self.assertEqual(
            readme_en.count("| Source layer | Photo sites | Video sites | Rule |"),
            1,
        )
        self.assertNotIn("| Category | References |", readme_en)
        self.assertIn("never asks for, receives, stores, or handles", readme_en)
        self.assertIn("continues with automatic public sources", readme_en)


if __name__ == "__main__":
    unittest.main()
