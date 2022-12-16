import json
from datetime import datetime
from pathlib import Path

from ..dto.Dress import (
    Dress,
    BaseInfo,
    Stat,
    Skill,
    ActiveSkill,
    PassiveSkill,
    EntrySkill,
    UnitSkill,
    FinishSkill
)
from ..config import (ELEMENT, ATTACK_TYPE, ATTRIBUTES, ROLE, LOCALE)


class Formatter:
    @staticmethod
    async def dto2dict(dress: Dress, summary=True) -> dict:
        if summary:
            return {
                "basic_info": dress.basic_info.dict(include={
                    "name": True,
                    "rarity": True,
                    "release_date": True
                }),
                "stats": dress.stat.dict(exclude={
                    "role_index": True,
                    "accessories": True,
                    "remake": True,
                    "fix_stat": True
                })
            }
        else:
            return {"TODO": "TODO"}

    @staticmethod
    async def json2dto(filename: Path) -> Dress:
        with open(filename, "r") as f:
            raw = json.load(f)

            raw_basicInfo = raw["basicInfo"]
            raw_base = raw["base"]
            raw_other = raw["other"]
            raw_stat = raw["stat"]
            raw_statRemake = raw["statRemake"]
            raw_acts = raw["act"]
            raw_skills = raw["skills"]
            raw_entrySkill = raw["entrySkill"]
            raw_groupSkills = raw["groupSkills"]

            basic_info = BaseInfo(
                id=raw_basicInfo["cardID"],
                name=raw_basicInfo["name"],
                rarity=raw_basicInfo["rarity"],
                profile=raw_basicInfo["profile"],
                message=raw_basicInfo["message"],
                description=raw_basicInfo["description"],
                release_date=raw_basicInfo["released"]["ja"]
            )

            stat = Stat(
                element=raw_base["attribute"],
                attack_type=raw_base["attackType"],
                role=raw_base["roleIndex"]["role"],
                role_index=raw_base["roleIndex"]["index"],
                cost=raw_base["cost"],
                accessories=raw_base["accessories"],
                remake=raw_base["remake"],
                normal_stat=raw_stat,
                remake_stat=raw_statRemake,
                fix_stat={"crit_chance": raw_other["dex"], "crit_damage": raw_other["cri"], "eva": raw_other["eva"]}
            )

            active_skill = []
            for (_, raw_act) in raw_acts.items():
                skillNormal = raw_act["skillNormal"]
                skillChange = raw_act["skillChange"]

                current_skill = {}

                skillNoramlParams = skillNormal["params"]
                normal_skill = ActiveSkill(
                    id=skillNormal["id"],
                    name=skillNormal["name"],
                    element=skillNormal["attribute"],
                    cost=skillNormal["cost"],
                    multiple=skillNormal["multiple"],
                    icon=skillNormal["icon"],
                    params=[Skill(
                        icon=skillParam["icon"],
                        skill_type=skillParam["type"],
                        hits=skillParam.get("hits", None),
                        accuracy=skillParam.get("accuracy", None),
                        duration=skillParam.get("duration", None),
                        target=skillParam["target"],
                        description=skillParam["description"],
                        description_extra=skillParam["descriptionExtra"],
                        name=skillParam.get("name", None)
                    ) for skillParam in skillNoramlParams]
                )

                current_skill["normal_skill"] = normal_skill

                if skillChange is None:
                    current_skill["change_skill"] = None
                else:
                    skillChangeParams = skillChange["params"]
                    change_skill = ActiveSkill(
                        id=skillChange["id"],
                        name=skillChange["name"],
                        element=skillChange["attribute"],
                        cost=skillChange["cost"],
                        multiple=skillChange["multiple"],
                        icon=skillChange["icon"],
                        params=[Skill(
                            icon=skillParam["icon"],
                            skill_type=skillParam["type"],
                            hits=skillParam.get("hits", None),
                            accuracy=skillParam.get("accuracy", None),
                            duration=skillParam.get("duration", None),
                            target=skillParam["target"],
                            description=skillParam["description"],
                            description_extra=skillParam["descriptionExtra"],
                            name=skillParam.get("name", None)
                        ) for skillParam in skillChangeParams]
                    )

                    current_skill["change_skill"] = change_skill

                active_skill.append(current_skill)

            passive_skill = []
            for (_, raw_passive) in raw_skills.items():
                passiveParams = raw_passive["params"]
                current_passive = PassiveSkill(
                    id=raw_passive["id"],
                    icon=raw_passive["icon"],
                    act_type=raw_passive["type"],
                    params=[Skill(
                        icon=skillParam["icon"],
                        skill_type=skillParam["type"],
                        hits=skillParam.get("hits", None),
                        accuracy=skillParam.get("accuracy", None),
                        duration=skillParam.get("duration", None),
                        target=skillParam["target"],
                        description=skillParam["description"],
                        description_extra=skillParam["descriptionExtra"],
                        name=skillParam.get("name", None)
                    ) for skillParam in passiveParams]
                )
                passive_skill.append(current_passive)

            if raw_entrySkill is None:
                entry_skill = None
            else:
                entry_skill = EntrySkill(
                    id=raw_entrySkill["id"],
                    icon=raw_entrySkill["icon"],
                    params=[Skill(
                        icon=skillParam["icon"],
                        skill_type=skillParam["type"],
                        hits=skillParam.get("hits", None),
                        accuracy=skillParam.get("accuracy", None),
                        duration=skillParam.get("duration", None),
                        target=skillParam["target"],
                        description=skillParam["description"],
                        description_extra=skillParam["descriptionExtra"],
                        name=skillParam.get("name", None)
                    ) for skillParam in raw_entrySkill["params"]]
                )

            unit_skill = UnitSkill(
                id=raw_groupSkills["unitSkill"]["id"],
                icon=raw_groupSkills["unitSkill"]["icon"],
                descrption=raw_groupSkills["unitSkill"]["description"]
            )

            climaxSkillNormal = raw_groupSkills["climaxACT"]["skillNormal"]
            climax_skill = {}
            climax_skill["normal_skill"] = ActiveSkill(
                id=climaxSkillNormal["id"],
                name=climaxSkillNormal["name"],
                element=climaxSkillNormal["attribute"],
                cost=climaxSkillNormal["cost"],
                multiple=climaxSkillNormal["multiple"],
                icon=climaxSkillNormal["icon"],
                params=[Skill(
                    icon=skillParam["icon"],
                    skill_type=skillParam["type"],
                    hits=skillParam.get("hits", None),
                    accuracy=skillParam.get("accuracy", None),
                    duration=skillParam.get("duration", None),
                    target=skillParam["target"],
                    description=skillParam["description"],
                    description_extra=skillParam["descriptionExtra"],
                    name=skillParam.get("name", None)
                ) for skillParam in climaxSkillNormal["params"]]
            )

            if raw_groupSkills["climaxACT"]["skillChange"] is None:
                climax_skill["change_skill"] = None
            else:
                climaxSkillChange = raw_groupSkills["climaxACT"]["skillChange"]
                climax_skill["change_skill"] = ActiveSkill(
                    id=climaxSkillChange["id"],
                    name=climaxSkillChange["name"],
                    element=climaxSkillChange["attribute"],
                    cost=climaxSkillChange["cost"],
                    multiple=climaxSkillChange["multiple"],
                    icon=climaxSkillChange["icon"],
                    params=[Skill(
                        icon=skillParam["icon"],
                        skill_type=skillParam["type"],
                        hits=skillParam.get("hits", None),
                        accuracy=skillParam.get("accuracy", None),
                        duration=skillParam.get("duration", None),
                        target=skillParam["target"],
                        description=skillParam["description"],
                        description_extra=skillParam["descriptionExtra"],
                        name=skillParam.get("name", None)
                    ) for skillParam in climaxSkillChange["params"]]
                )

            finish_skill = FinishSkill(
                id=raw_groupSkills["finishACT"]["id"],
                icon=raw_groupSkills["finishACT"]["icon"],
                name=raw_groupSkills["finishACT"]["name"],
                description=raw_groupSkills["finishACT"]["description"]
            )

            return Dress(
                basic_info=basic_info,
                stat=stat,
                active_skill=active_skill,
                passive_skill=passive_skill,
                unit_skill=unit_skill,
                entry_skill=entry_skill,
                climax_skill=climax_skill,
                finish_skill=finish_skill
            )

    @staticmethod
    async def dict2text(dress: dict, summary=True) -> str:
        if summary:
            basic_info = dress["basic_info"]
            print(basic_info)
            stats = dress["stats"]

            name = f"角色: {basic_info['name'][LOCALE.JP]}"
            if basic_info["name"].get(LOCALE.EN, None):
                name = name + f"({basic_info['name'][LOCALE.EN]}, {basic_info['name'][LOCALE.CN]})"
            rarity = f"稀有度: {basic_info['rarity']}"
            release_date = f"卡池公布: {datetime.fromtimestamp(basic_info['release_date']).strftime('%Y-%m-%d %H:%M')}"

            element = f"属性: {ELEMENT[stats['element']]}"
            attack_type = f"类型: {ATTACK_TYPE[stats['attack_type']]}"
            role = f"站位: {ROLE[stats['role']]}"
            cost = f"Cost: {stats['cost']}"

            normal_stat = stats["normal_stat"]
            remake_stat = stats["remake_stat"]

            number_stats = "数值(再生产):"
            for k, v in ATTRIBUTES.items():
                number_stats += f"\n{v}: {normal_stat[k]}"
                if remake_stat:
                    number_stats += f"({remake_stat[k]})"

            result = "\n".join([name, rarity, release_date, "", element, attack_type, role, cost, "", number_stats])
        else:
            result = "TODO"

        return result