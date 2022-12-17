from asyncio import run
from pathlib import Path
from util.converter import Converter

async def __main():
    cwd = Path.cwd()
    resource = cwd / "resource" / "json"
    initial_aliases = await Converter.generate_simplified_names(resource)

    result = []
    for card in initial_aliases:
        result.append({
            "cid": card[0],
            "name": card[1],
            "alias": [card[1]]
        })

    await Converter.persist({"root": result}, cwd / "resource" / "alias.json")


run(__main())