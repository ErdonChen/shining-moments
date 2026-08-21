import unittest
from pathlib import Path


SKILL_PATH = Path(__file__).resolve().parents[1] / "SKILL.md"


class SkillWorkflowTests(unittest.TestCase):
    def test_material_type_routes_sources_before_connectivity_and_inventory(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")

        material_type = skill.index("**Material type:**")
        source_routing = skill.index("Route the reference sources")
        connectivity = skill.index("**Connectivity check and live references**")
        inventory = skill.index("Inventory read-only")

        self.assertLess(material_type, source_routing)
        self.assertLess(source_routing, connectivity)
        self.assertLess(connectivity, inventory)


if __name__ == "__main__":
    unittest.main()
