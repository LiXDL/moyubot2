import json
import zhconv
from aiofiles import open
from asyncio import gather, run
from pathlib import Path


class Converter:
    @staticmethod
    def simplify(zh_hant: str) -> str:
        return zhconv.convert(zh_hant, "zh-cn")

    @staticmethod
    async def generate_simplified_names(dir: Path) -> list[tuple[str, str]]:
        files = list(dir.glob("*.json"))

        async def single_extractor(filename: Path) -> tuple[str, str]:
            async with open(filename, "r") as afp:
                raw_data = await afp.read()
                raw_json = json.loads(raw_data)
                cid = raw_json["basicInfo"]["cardID"]
                cname = raw_json["basicInfo"]["name"]

                if len(cname) > 1:
                    return cid, zhconv.convert(cname["zh_hant"], "zh-cn")
                else:
                    return cid, cname["ja"]

        result = await gather(*[single_extractor(f) for f in files])

        return result

    @staticmethod
    async def persist(alias_dict: dict, target: Path):
        async with open(target, "w") as afp:
            await afp.write(json.dumps(alias_dict, indent=4, ensure_ascii=False))

    @staticmethod
    async def load(target : Path) -> dict:
        async with open(target, "r") as afp:
            return json.loads(await afp.read())


async def __main():
    cwd = Path(__file__)
    resource = cwd.parent.parent / "resource" / "json"
    initial_aliases = await Converter.generate_simplified_names(resource)

    result = {}
    for card in initial_aliases:
        result[card[0]] = {
            "name": card[1],
            "alias": [card[1]]
        }

    await Converter.persist({"root": result}, cwd.parent.parent / "resource" / "alias.json")


if __name__ == "__main__":
    run(__main())
