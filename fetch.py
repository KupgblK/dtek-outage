import asyncio, json, os, sys
from pathlib import Path
from dtek_client import DtekClient

CITY = os.environ["DTEK_CITY"]
STREET = os.environ["DTEK_STREET"]
HOUSE = os.environ["DTEK_HOUSE"]

OUT = Path("data/outage.json")
HIST = Path("data/history.jsonl")

async def main():
    async with DtekClient("oem") as client:
        response = await client.get_home_num(CITY, STREET)
    entry = response.houses.get(HOUSE)
    if entry is None:
        sys.exit("house not found")
    dump = response.model_dump()
    e = entry.model_dump()
    state = {
        "site_updated": dump.get("update_timestamp"),
        "groups": e.get("group_ids"),
        "outage": {k: e.get(k) for k in
                   ("sub_type", "start_date", "end_date", "outage_type", "voluntarily")},
        "show_cur_outage_param": dump.get("show_cur_outage_param"),
    }
    new_text = json.dumps(state, ensure_ascii=False, indent=2, default=str)
    old_text = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    if new_text == old_text:
        return
    OUT.parent.mkdir(exist_ok=True)
    old_outage = json.loads(old_text).get("outage") if old_text else None
    if old_outage != state["outage"]:
        with HIST.open("a", encoding="utf-8") as f:
            f.write(json.dumps(state, ensure_ascii=False, default=str) + "\n")
    OUT.write_text(new_text, encoding="utf-8")

asyncio.run(main())
