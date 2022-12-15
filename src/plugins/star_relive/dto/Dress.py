from pydantic import BaseModel
from typing import Union


class BaseInfo(BaseModel):
    id: str
    name: dict[str, str]
    rarity: int
    profile: dict[str, str]
    message: dict[str, str]
    description: dict[str, str]
    release_date: int


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


class Skill(BaseModel):
    icon: int
    skill_type: str
    hits: int | None
    accuracy: int | None
    duration: dict[str, str] | None
    target: dict[str, str] | None
    description: dict[str, str] | None
    description_extra: dict[str, str] | None
    name: dict[str, str] | None


class ActiveSkill(BaseModel):
    id: int
    name: dict[str, str]
    element: int
    cost: int
    multiple: bool
    icon: int
    params: list[Skill]


class PassiveSkill(BaseModel):
    id: int
    icon: int
    act_type: dict[str, str]
    params: list[Skill]


class EntrySkill(BaseModel):
    id: int
    icon: int
    params: list[Skill]


class UnitSkill(BaseModel):
    id: int
    icon: int
    descrption: dict[str, str]


class FinishSkill(BaseModel):
    id: int
    icon: int
    name: dict[str, str] | None
    description: dict[str, str] | None


class Dress(BaseModel):
    basic_info: BaseInfo
    stat: Stat
    active_skill: list[dict[str, Union[ActiveSkill, None]]]
    passive_skill: list[PassiveSkill]
    unit_skill: UnitSkill
    entry_skill: EntrySkill
    climax_skill: dict[str, Union[ActiveSkill, None]]
    finish_skill: FinishSkill
