"""CRO - Chief Risk Officer. Abogado del diablo. Paranoia es su valor."""

from skills.base_skill import BaseSkill


class CROSkill(BaseSkill):
    agent_name = "CRO"
    prompt_file = "CRO_prompt.md"
