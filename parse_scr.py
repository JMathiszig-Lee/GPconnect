import json
import asyncio
from bs4 import BeautifulSoup
from pprint import pprint


async def parse_scr(scr):
    """
    parses scr json and returns structured data
    """
    entry = scr["entry"][0]

    scr_dict = {}

    async def parse_scr_section(section):
        """
        parses each section of the scr and converts html to stuctured data
        """
        section_list = []

        section_html = section["text"]["div"]
        soup = BeautifulSoup(section_html, "html.parser")
        table = soup.find("table")
        if table:
            headings = table.find_all("th")
            headings = [ele.text.strip() for ele in headings]

            rows = table.find("tbody").find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                cols = [ele.text.strip() for ele in cols]
                row_entry = {}
                for ind, val in enumerate(cols):
                    row_entry[headings[ind]] = val
                section_list.append(row_entry)
        scr_dict[section["title"]] = section_list

    await asyncio.gather(
        *[parse_scr_section(section) for section in entry["resource"]["section"]]
    )

    print(scr_dict)


if __name__ == "__main__":
    with open("scr.json") as scr_json:
        scr = json.load(scr_json)
        asyncio.run(parse_scr(scr))
