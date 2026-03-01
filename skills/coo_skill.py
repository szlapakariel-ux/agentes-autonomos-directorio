"""COO - Chief Operating Officer. Traduce ideas en pasos accionables."""

from skills.base_skill import BaseSkill


class COOSkill(BaseSkill):
    agent_name = "COO"
    prompt_file = "COO_prompt.md"
