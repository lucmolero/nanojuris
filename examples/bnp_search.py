from nanojuris import NanoJurisClient

client = NanoJurisClient()
page = client.search(
    "ICMS consumidor final",
    courts=["STF", "STJ"],
    types=["RG", "RR"],
    page_size=5,
)

for result in page.results:
    print(result.court, result.type, result.number, result.thesis)
