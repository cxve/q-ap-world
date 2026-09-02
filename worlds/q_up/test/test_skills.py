from .bases import QUPtestBase
from ..Data import upgradable_skill_names_flat, skill_names_flat

class TestFixedSkillNum(QUPtestBase):
    def test_fixed_skill_num(self) -> None:
        """fixed skill number should match the option"""
        fixed_skills = [fixed_skill for fixed_skill in self.multiworld.get_items() if fixed_skill.name in upgradable_skill_names_flat]
        self.assertEqual(len(fixed_skills), self.options["itemPoolFixedSkillNum"])

    def test_skill_num(self) -> None:
        """skill number should match the option"""
        skills = [skill for skill in self.multiworld.get_items() if skill.name in skill_names_flat]
        self.assertEqual(len(skills), self.options["itemPoolTotalSkillNum"])