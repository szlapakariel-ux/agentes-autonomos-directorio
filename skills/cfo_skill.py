"""CFO - Chief Financial Officer. Cuida la billetera. ROI. Números."""

from skills.base_skill import BaseSkill


class CFOSkill(BaseSkill):
    agent_name = "CFO"
    prompt_file = "CFO_prompt.md"
