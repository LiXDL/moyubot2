import pandas as pd
from pathlib import Path
from nonebot.utils import run_sync

ALIAS: pd.DataFrame


class AliasInfo:
    '''
    status is in one of the following:
        200: OK
        404: Not Found
        500: Internal Error
    '''
    status: int
    cid: int
    cname: str
    calias: list

    def __init__(self, status: int, cid: int = 0, cname: str = "", calias: list = []):
        self.status, self.cid, self.cname, self.calias = status, cid, cname, calias


def load(filename: Path):
    global ALIAS
    ALIAS = pd.read_csv(filename, header=0)


def persist(filename: Path):
    ALIAS.to_csv(filename, index=False)


@run_sync
def retrive_id(cid: int) -> AliasInfo:
    if ALIAS is None:
        return AliasInfo(500)

    search_result = ALIAS.loc[ALIAS["cid"]==cid]

    if search_result.shape[0] == 0:
        return AliasInfo(404)

    cname = search_result.iloc[0, 1]
    calias = search_result["alias"].to_list()
    return AliasInfo(200, cid, str(cname), calias)


@run_sync
def retrive_info(cinfo: str) -> list[AliasInfo]:
    '''
    cinfo needs to be simplified into zh-cn before passing in
    '''
    if ALIAS is None:
        return [AliasInfo(500)]

    search_name = ALIAS.loc[ALIAS["name"]==cinfo]
    search_alias = ALIAS.loc[ALIAS["alias"]==cinfo]

    if search_name.empty and search_alias.empty:
        return [AliasInfo(404)]
    else:
        if search_alias.empty:
            search_name_grouped = search_name.groupby("cid")
            result = []
            for gid, g in search_name_grouped:
                calias = g["alias"].to_list()
                result.append(AliasInfo(200, int(str(gid)), cinfo, calias))
            return result
        else:
            search_alias_grouped = search_alias.groupby("cid")
            result = []
            for gid, g in search_alias_grouped:
                cname = g.iloc[0, 1]
                calias = g["alias"].to_list()
                result.append(AliasInfo(200, int(str(gid)), str(cname), calias))
            return result


@run_sync
def add_alias(cid: int, calias: list[str]) -> AliasInfo:
    '''
    calias needs to be simplified to zh-cn before passing in
    '''
    global ALIAS
    if ALIAS is None:
        return AliasInfo(500)

    existsed_aliases = ALIAS.loc[ALIAS["cid"]==cid]
    if existsed_aliases.empty:
        return AliasInfo(404)

    cname = existsed_aliases.iloc[0, 1]

    new_entries = []
    for a in calias:
        if a not in existsed_aliases["alias"]:
            new_entries.append({
                "cid": cid,
                "name": cname,
                "alias": a
            })
    ALIAS = pd.concat([ALIAS, pd.DataFrame(new_entries)], axis=0, ignore_index=True)
    new_aliases = ALIAS.loc[ALIAS["cid"]==cid]["alias"].to_list()

    return AliasInfo(200, cid, str(cname), new_aliases)


@run_sync
def remove_alias(cid: int, calias: list[str]) -> AliasInfo:
    '''
    calias needs to be simplified to zh-cn before passing in
    '''
    global ALIAS
    if ALIAS is None:
        return AliasInfo(500)

    existed_aliases = ALIAS.loc[ALIAS["cid"]==cid]
    if existed_aliases.empty:
        return AliasInfo(404)

    cname = existed_aliases.iloc[0, 1]

    ALIAS.drop(ALIAS.loc[ALIAS["alias"].isin(calias)].index, inplace=True)
    ALIAS.reset_index(drop=True, inplace=True)

    new_aliases = ALIAS.loc[ALIAS["cid"]==cid]["alias"].to_list()

    return AliasInfo(200, cid, str(cname), new_aliases)

