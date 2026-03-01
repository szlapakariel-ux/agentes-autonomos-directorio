"""CEO - Lider, tomador de decisiones, visión global"""

from skills.base_skill import BaseSkill


class CEOSkill(BaseSkill):
    agent_name = "CEO"
    prompt_file = "CEO_prompt.md"
