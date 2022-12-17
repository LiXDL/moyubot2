from pydantic import BaseModel

from collections import OrderedDict
from datetime import datetime
from enum import Enum
from typing import Union
import re


TURN_LEVEL = re.compile(r"\[.+\]")
TURN_FIXED = re.compile(r"\d")

EMPTY = ""

ELEMENT: list = ["", "花", "风", "雪", "月", "宙", "云", "梦", "日", "星"]
ATTACK_TYPE: list = ["", "通常", "特殊"]
ATTRIBUTES: OrderedDict[str, str] = OrderedDict([("total", "综合力"), ("atk", "ACT Power"), ("hp", "HP"), ("agi", "速度"), ("mdef", "特防"), ("pdef", "物防")])
ROLE: dict[str, str] = {"front": "前排", "middle": "中排", "back": "后排"}
EFFECT_TYPE: dict[str, str] = {"normal": "", "fieldEffect": "舞台效果"}

class LOCALE(str, Enum):
    JP = "ja"
    CN = "zh_hant"
    EN = "en"
    KR = "ko"

class SKILL_CHANGE(str, Enum):
    N = "normal_skill"
    C = "change_skill"


def turn_helper(s: str) -> str:
    g : re.Match | None
    if (g := re.search(TURN_LEVEL, s)) is not None:
        return g.group(0)
    if (g := re.search(TURN_FIXED, s)) is not None:
        return g.group(0)
    return ""


class BaseInfo(BaseModel):
    id: str
    name: dict[str, str]
    rarity: int
    profile: dict[str, str]
    message: dict[str, str]
    description: dict[str, str]
    release_date: int

    def summary(self) -> str:
        name = f"角色: {self.name[LOCALE.JP]}"
        if len(self.name) > 1:
            name += f"({self.name[LOCALE.EN]}, {self.name[LOCALE.JP]})"
        rarity = f"稀有度: {self.rarity}"
        release_date = f"卡池公布: {datetime.fromtimestamp(self.release_date).strftime('%Y-%m-%d %H:%M')}"

        return "\n".join([name, rarity, release_date])

    def full(self) -> list:
        summary = self.summary()

        profile = "简介:\n{}".format(self.profile[LOCALE.JP])
        message = "台词:\n{}".format(self.message[LOCALE.JP])
        description = "描述:\n{}".format(self.description[LOCALE.JP])

        # if len(self.name) > 1:
        #     profile += "\n{}".format(self.profile[LOCALE.JP])
        #     message += "\n{}".format(self.message[LOCALE.JP])
        #     description += "\n{}".format(self.description[LOCALE.JP])
        
        return [summary, "\n\n".join([profile, message, description])]


class Stat(BaseModel):
    element: int
    attack_type: int
    role: str
    role_index: int
    cost: int
    accessories: list[int] | None
    remake: bool
    normal_stat: dict[str, int]
    remake_stat: dict[str, int]
    fix_stat: dict[str, int]

    def summary(self) -> str:
        element = f"属性: {ELEMENT[self.element]}"
        attack_type = f"类型: {ATTACK_TYPE[self.attack_type]}"
        role = f"站位: {ROLE[self.role]}({self.role_index})"
        cost = f"Cost: {self.cost}"

        number_stats = "数值(再生产):"
        for k, v in ATTRIBUTES.items():
            number_stats += "\n{}: {}".format(v, self.normal_stat[k])
            if self.remake_stat:
                number_stats += f"({self.remake_stat[k]})"

        return "\n".join([element, attack_type, role, cost, "", number_stats])

    def full(self):
        return self.summary()


class Effect(BaseModel):
    icon: int
    effect_type: str
    hits: int | None
    accuracy: int | None
    duration: dict[str, str] | None
    target: dict[str, str] | None
    description: dict[str, str] | None
    description_extra: dict[str, str] | None
    name: dict[str, str] | None

    def summary(self) -> str:
        return ""

    def full(self) -> str:
        name = EMPTY if not self.name else self.name[LOCALE.JP]
        effect_type = EFFECT_TYPE[self.effect_type]
        description = EMPTY if not self.description else self.description[LOCALE.JP]
        description_extra = EMPTY if not self.description_extra else self.description_extra[LOCALE.JP]
        hits = EMPTY if not self.hits else f"Hit(s) {self.hits}"
        target = EMPTY if not self.target else self.target[LOCALE.JP]
        duration = EMPTY if not self.duration else f"生效 {self.duration[LOCALE.JP]}"
        
        type_name = ": ".join(filter(lambda s: len(s) > 0, [effect_type, name]))
        valid_target = f"{target}" if target else ""
        des_info = ", ".join(filter(lambda s: len(s) > 0, [description, description_extra]))

        return "; ".join(filter(lambda s: len(s) > 0, [type_name, valid_target, des_info, hits, duration]))
        

class ActiveSkill(BaseModel):
    id: int
    name: dict[str, str]
    element: int
    cost: int
    multiple: bool
    icon: int
    params: list[Effect]

    def summary(self) -> str:
        return ""

    def full(self) -> str:
        name = self.name[LOCALE.JP]
        element = f"属性: {ELEMENT[self.element]}"
        cost = f"COST: {self.cost}"
        effects = "效果: \n\n"
        effects += "\n".join([effect.full() for effect in self.params])

        return "\n".join([name, f"{element}, {cost}", effects])


class PassiveSkill(BaseModel):
    id: int
    icon: int
    act_type: dict[str, str]
    params: list[Effect]

    def summary(self) -> str:
        return ""

    def full(self) -> str:
        return "{}\n\n{}".format(
            self.act_type[LOCALE.JP], 
            '\n\n'.join([effect.full() for effect in self.params])
        )


class EntrySkill(BaseModel):
    id: int
    icon: int
    params: list[Effect]

    def summary(self) -> str:
        return ""
    
    def full(self) -> str:
        return "\n\n".join([effect.full() for effect in self.params])


class UnitSkill(BaseModel):
    id: int
    icon: int
    descrption: dict[str, str]
    
    def sumary(self) -> str:
        return ""

    def full(self) -> str:
        return self.descrption[LOCALE.JP]


class FinishSkill(BaseModel):
    id: int
    icon: int
    name: dict[str, str]
    description: dict[str, str]

    def summary(self) -> str:
        return ""

    def full(self) -> str:
        return "{}\n{}".format(
            EMPTY if not self.name else self.name[LOCALE.JP], 
            '' if not self.description else self.description[LOCALE.JP]
        )


class Dress(BaseModel):
    basic_info: BaseInfo
    stat: Stat
    active_skill: list[dict[str, Union[ActiveSkill, None]]]
    passive_skill: list[PassiveSkill]
    unit_skill: UnitSkill
    entry_skill: Union[EntrySkill, None]
    climax_skill: dict[str, Union[ActiveSkill, None]]
    finish_skill: FinishSkill

    def summary(self) -> str:
        basic_info = self.basic_info.summary()
        stat = self.stat.summary()

        return "{}\n\n{}".format(basic_info, stat)

    def full(self) -> list[str]:
        basic_info = self.basic_info.full()

        active_skills = []
        for (i, s) in enumerate(self.active_skill):
            normal_skill, change_skill = s[SKILL_CHANGE.N], s[SKILL_CHANGE.C]
            skill_str = "主动技能{}: {}".format(i + 1, '' if not normal_skill else normal_skill.full())
            skill_str += "" if not change_skill else "\n主动技能{}切换: \n{}".format(i, change_skill.full())
            active_skills.append(skill_str)

        passive_skills = ["被动技能{}: {}".format(i + 1, s.full()) for (i, s) in enumerate(self.passive_skill)]

        unit_skill = "Unit Skill: \n{}".format(self.unit_skill.full())

        entry_skill = EMPTY if not self.entry_skill else f"开幕雷击: {self.entry_skill.full()}"

        normal_climax, change_climax = self.climax_skill[SKILL_CHANGE.N], self.climax_skill[SKILL_CHANGE.C]
        climax_skill = "Climax: \n{}".format('' if not normal_climax else normal_climax.full())
        climax_skill += "" if not change_climax else "\n\n切换: \n{}".format(change_climax.full())

        finish_skill = "闭幕雷击: {}".format(self.finish_skill.full())

        other_skills = "\n\n".join(filter(lambda s: len(s) > 0, [unit_skill, entry_skill, finish_skill]))
        
        return [self.summary(), basic_info[1], *active_skills, *passive_skills, climax_skill, other_skills]
