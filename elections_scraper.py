import csv
import unicodedata

import requests
from bs4 import BeautifulSoup as Bs
from urllib.parse import urljoin


URL = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=4&xnumnuts=3201"
FILE = "elections_results_2"


def main():
    parsed_1 = soup(URL)
    villages = villages_codes(parsed_1)
    urls2 = get_url2(parsed_1)
    votes_info = []
    for url_2 in urls2:
        parsed_2 = soup(url_2)
        party = votes_parties(parsed_2)
        table2 = parsed_2.find("table", {"id": "ps311_t1"})
        for row in table2.find_all("tr")[2:]:
            items = {"registered": collect_registered(row, "td", 3),
                     "envelopes": collect_registered(row, "td", 4),
                     "valid": collect_registered(row, "td", 7)}
            items.update(party)
            votes_info.append(items)

    data = data_all(villages, votes_info)
    save_csv(data, FILE)


def soup(url):
    response = requests.get(url)
    parsed = Bs(response.text, "html.parser")
    return parsed


def get_url2(parsed):
    urls_2 = []
    for td_elem in parsed.select("td.cislo a"):
        href = urljoin("https://volby.cz/pls/ps2017nss/", td_elem["href"])
        urls_2.append(href)
    return urls_2


def villages_codes(parsed_1):
    code_loc = []
    try:
        for table in parsed_1.find_all("div", {"class": "t3"}):
            for row in table.find_all("tr")[2:]:
                code = row.find_all("td")[0].text
                location = row.find_all("td")[1].text
                code_loc.append({"code": code, "location": location})
        return list(filter(lambda x: '-' not in x.values(), code_loc))

    except AttributeError:
        print("Given cell indexes in the row are not correct")


def collect_registered(current_row, tag, index):
    registered = current_row.find_all(tag)[index].text
    return unicodedata.normalize("NFKD", registered)


def votes_parties(parsed):
    results = {}
    try:
        for table in parsed.find_all("div", {"class": "t2_470"}):
            for row in table.find_all("tr")[2:]:
                vote = row.find_all("td")[2].text
                party = row.find_all("td")[1].text
                results.setdefault(party, vote)
        return dict(filter(lambda x: x[0] != '-', results.items()))

    except AttributeError:
        print("Given cell indexes in the row are not correct")


def data_all(data1, data2):
    for index, _ in enumerate(data1):
        data1[index].update(data2[index])
    return data1


def save_csv(data, file):
    with open('{}.{ext}'.format(file, ext="csv"), "w", newline="") as er:
        headers = data[0].keys()
        writer = csv.DictWriter(er, fieldnames=headers)
        writer.writeheader()
        for item in data:
            writer.writerow(item)


if __name__ == "__main__":
    main()
