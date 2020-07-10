import csv
import unicodedata

import requests
from bs4 import BeautifulSoup as Bs

URL = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=4&xnumnuts=3201"
FILE = "elections_results"


def main():
    parsed_1 = soup(URL)
    tables_1 = parsed_1.find_all("div", {"class": "t3"})
    villages = villages_codes(tables_1)
    voters = []
    votes = []
    urls2 = get_url2(parsed_1, URL)
    parties = []
    for url_2 in urls2:
        parsed_2 = soup(url_2)
        voters.append(voters_counts(parsed_2))
        vote, party = votes_parties(parsed_2)
        votes.append(vote)
        if not parties:
            parties.extend(party)
    data = data_all(villages, voters, votes)
    save_csv(data, parties, FILE)


def soup(url):
    response = requests.get(url)
    parsed = Bs(response.text, "html.parser")
    return parsed


def villages_codes(tables1):
    data_1 = []
    try:
        for table in tables1:
            rows1 = table.find_all("tr")[2:]
            for row in rows1:
                code_loc = []
                code = row.find_all("td")[0].text
                location = row.find_all("td")[1].text
                if code != "-":
                    code_loc.append(code)
                elif location != "-":
                    code_loc.append(location)
                data_1.append(code_loc)
        return list(filter(None, data_1))

    except AttributeError:
        print("Given cell indexes in the row are not correct")


def get_url2(parsed, url):
    urls = []
    try:
        table_data = parsed.find_all("td", {"class": "cislo"})
        for item in table_data:
            url_split = url.split("/")[:5]
            url_village = item.find("a")["href"]
            url_split.append(url_village)
            url_2 = "/".join(url_split)
            urls.append(url_2)
        return urls

    except AttributeError:
        print("Data not found.")


def voters_counts(parsed):
    try:
        table2 = parsed.find("table", {"id": "ps311_t1"})
        rows2 = table2.find_all("tr")[2:]
        data_2 = []
        for row in rows2:
            registered = row.find_all("td")[3].text
            envelopes = row.find_all("td")[4].text
            valid = row.find_all("td")[6].text
            items = registered, envelopes, valid
            for item in items:
                data_2.append(unicodedata.normalize("NFKD", item))
        return data_2

    except AttributeError:
        print("Given cell indexes in the row are not correct")


def votes_parties(parsed):
    try:
        tables3 = parsed.find_all("div", {"class": "t2_470"})
        votes = []
        parties = []
        for table in tables3:
            rows3 = table.find_all("tr")[2:]
            for row in rows3:
                vote = row.find_all("td")[2].text
                party = row.find_all("td")[1].text
                if vote != "-":
                    votes.append(unicodedata.normalize("NFKD", vote))
                elif party != "-":
                    parties.append(party)
        return votes, parties

    except AttributeError:
        print("Given cell indexes in the row are not correct")


def data_all(data1, data2, data3):
    for index, _ in enumerate(data1):
        data1[index].extend(data2[index])
        data1[index].extend(data3[index])
    return data1


def save_csv(data, parties, file):
    with open('{}.{ext}'.format(file, ext="csv"), "w", newline="") as er:
        headers = ["code", "location", "registered", "envelopes", "valid", *parties]
        writer = csv.writer(er)
        writer.writerow(headers)
        for item in data:
            writer.writerow(item)


if __name__ == "__main__":
    main()
