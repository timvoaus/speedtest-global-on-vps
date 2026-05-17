import subprocess
import urllib.parse
import random
import json
import time

SERVER_COUNT = 3
LIMIT = 100
SLEEP_SECONDS = 1
TIMEOUT = 20

COUNTRIES = [
    # Asia
    {"name": "Singapore", "cc": "SG", "lat": 1.3521, "lon": 103.8198},
    {"name": "Japan", "cc": "JP", "lat": 35.6762, "lon": 139.6503},
    {"name": "South Korea", "cc": "KR", "lat": 37.5665, "lon": 126.9780},
    {"name": "Hong Kong", "cc": "HK", "lat": 22.3193, "lon": 114.1694},
    {"name": "Taiwan", "cc": "TW", "lat": 25.0330, "lon": 121.5654},
    {"name": "India", "cc": "IN", "lat": 19.0760, "lon": 72.8777},
    {"name": "Indonesia", "cc": "ID", "lat": -6.2088, "lon": 106.8456},
    {"name": "Malaysia", "cc": "MY", "lat": 3.1390, "lon": 101.6869},
    {"name": "Thailand", "cc": "TH", "lat": 13.7563, "lon": 100.5018},
    {"name": "Vietnam", "cc": "VN", "lat": 10.8231, "lon": 106.6297},
    {"name": "Philippines", "cc": "PH", "lat": 14.5995, "lon": 120.9842},
    {"name": "Pakistan", "cc": "PK", "lat": 24.8607, "lon": 67.0011},
    {"name": "Bangladesh", "cc": "BD", "lat": 23.8103, "lon": 90.4125},
    {"name": "Sri Lanka", "cc": "LK", "lat": 6.9271, "lon": 79.8612},
    {"name": "Nepal", "cc": "NP", "lat": 27.7172, "lon": 85.3240},
    {"name": "Kazakhstan", "cc": "KZ", "lat": 43.2220, "lon": 76.8512},
    {"name": "Mongolia", "cc": "MN", "lat": 47.8864, "lon": 106.9057},

    # Europe
    {"name": "Germany", "cc": "DE", "lat": 52.5200, "lon": 13.4050},
    {"name": "Netherlands", "cc": "NL", "lat": 52.3676, "lon": 4.9041},
    {"name": "United Kingdom", "cc": "GB", "lat": 51.5072, "lon": -0.1276},
    {"name": "France", "cc": "FR", "lat": 48.8566, "lon": 2.3522},
    {"name": "Sweden", "cc": "SE", "lat": 59.3293, "lon": 18.0686},
    {"name": "Switzerland", "cc": "CH", "lat": 47.3769, "lon": 8.5417},
    {"name": "Poland", "cc": "PL", "lat": 52.2297, "lon": 21.0122},
    {"name": "Italy", "cc": "IT", "lat": 41.9028, "lon": 12.4964},
    {"name": "Spain", "cc": "ES", "lat": 40.4168, "lon": -3.7038},
    {"name": "Finland", "cc": "FI", "lat": 60.1699, "lon": 24.9384},
    {"name": "Turkey", "cc": "TR", "lat": 41.0082, "lon": 28.9784},
    {"name": "Russia", "cc": "RU", "lat": 55.7558, "lon": 37.6173},
    {"name": "Norway", "cc": "NO", "lat": 59.9139, "lon": 10.7522},
    {"name": "Denmark", "cc": "DK", "lat": 55.6761, "lon": 12.5683},
    {"name": "Belgium", "cc": "BE", "lat": 50.8503, "lon": 4.3517},
    {"name": "Austria", "cc": "AT", "lat": 48.2082, "lon": 16.3738},
    {"name": "Portugal", "cc": "PT", "lat": 38.7223, "lon": -9.1393},
    {"name": "Greece", "cc": "GR", "lat": 37.9838, "lon": 23.7275},
    {"name": "Czech Republic", "cc": "CZ", "lat": 50.0755, "lon": 14.4378},
    {"name": "Romania", "cc": "RO", "lat": 44.4268, "lon": 26.1025},
    {"name": "Ireland", "cc": "IE", "lat": 53.3498, "lon": -6.2603},

    # North America
    {"name": "United States", "cc": "US", "lat": 37.7749, "lon": -122.4194},
    {"name": "Canada", "cc": "CA", "lat": 43.6532, "lon": -79.3832},
    {"name": "Mexico", "cc": "MX", "lat": 19.4326, "lon": -99.1332},

    # South America
    {"name": "Brazil", "cc": "BR", "lat": -23.5505, "lon": -46.6333},
    {"name": "Argentina", "cc": "AR", "lat": -34.6037, "lon": -58.3816},
    {"name": "Chile", "cc": "CL", "lat": -33.4489, "lon": -70.6693},
    {"name": "Colombia", "cc": "CO", "lat": 4.7110, "lon": -74.0721},
    {"name": "Peru", "cc": "PE", "lat": -12.0464, "lon": -77.0428},
    {"name": "Venezuela", "cc": "VE", "lat": 10.4806, "lon": -66.9036},
    {"name": "Uruguay", "cc": "UY", "lat": -34.9011, "lon": -56.1645},
    {"name": "Ecuador", "cc": "EC", "lat": -0.1807, "lon": -78.4678},

    # Middle East
    {"name": "United Arab Emirates", "cc": "AE", "lat": 25.2048, "lon": 55.2708},
    {"name": "Saudi Arabia", "cc": "SA", "lat": 24.7136, "lon": 46.6753},
    {"name": "Qatar", "cc": "QA", "lat": 25.2854, "lon": 51.5310},
    {"name": "Israel", "cc": "IL", "lat": 32.0853, "lon": 34.7818},
    {"name": "Kuwait", "cc": "KW", "lat": 29.3759, "lon": 47.9774},
    {"name": "Bahrain", "cc": "BH", "lat": 26.2235, "lon": 50.5876},
    {"name": "Oman", "cc": "OM", "lat": 23.5880, "lon": 58.3829},
    {"name": "Jordan", "cc": "JO", "lat": 31.9539, "lon": 35.9106},

    # Africa
    {"name": "South Africa", "cc": "ZA", "lat": -26.2041, "lon": 28.0473},
    {"name": "Kenya", "cc": "KE", "lat": -1.2921, "lon": 36.8219},
    {"name": "Nigeria", "cc": "NG", "lat": 6.5244, "lon": 3.3792},
    {"name": "Egypt", "cc": "EG", "lat": 30.0444, "lon": 31.2357},
    {"name": "Morocco", "cc": "MA", "lat": 33.5731, "lon": -7.5898},
    {"name": "Algeria", "cc": "DZ", "lat": 36.7538, "lon": 3.0588},
    {"name": "Tunisia", "cc": "TN", "lat": 36.8065, "lon": 10.1815},
    {"name": "Ethiopia", "cc": "ET", "lat": 9.0300, "lon": 38.7400},
    {"name": "Ghana", "cc": "GH", "lat": 5.6037, "lon": -0.1870},
    {"name": "Tanzania", "cc": "TZ", "lat": -6.7924, "lon": 39.2083},

    # Oceania
    {"name": "Australia", "cc": "AU", "lat": -33.8688, "lon": 151.2093},
    {"name": "New Zealand", "cc": "NZ", "lat": -36.8485, "lon": 174.7633},
]


def fetch_servers(country):
    params = {
        "engine": "js",
        "limit": LIMIT,
        "lat": country["lat"],
        "lon": country["lon"],
        "https_functional": "true",
    }

    query = urllib.parse.urlencode(params)
    url = f"https://www.speedtest.net/api/js/servers?{query}"

    for attempt in range(1, 4):
        try:
            result = subprocess.run(
                [
                    "curl",
                    "-s",
                    "-L",
                    "-A",
                    "curl/8.5.0",
                    url,
                ],
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
            )

            if result.returncode != 0:
                raise Exception(result.stderr.strip())

            if not result.stdout.strip():
                raise Exception("empty response")

            data = json.loads(result.stdout)

            if not isinstance(data, list):
                raise Exception(f"bad response: {str(data)[:100]}")

            return [
                server for server in data
                if server.get("cc") == country["cc"]
            ]

        except Exception as e:
            print(f"[RETRY {attempt}] {country['name']}: {e}")
            time.sleep(2)

    return []


def clean_server(server):
    return {
        "id": server.get("id"),
        "name": server.get("name"),
        "country": server.get("country"),
        "cc": server.get("cc"),
        "sponsor": server.get("sponsor"),
        "host": server.get("host"),
        "url": server.get("url"),
        "lat": server.get("lat"),
        "lon": server.get("lon"),
        "distance": server.get("distance"),
    }


def main():
    results = {}
    missing = {
        "partial": [],
        "missing": [],
    }

    server_ids_by_country = {}
    server_ids_txt_lines = []

    for country in COUNTRIES:
        servers = fetch_servers(country)
        cleaned = [clean_server(server) for server in servers]

        if len(cleaned) >= SERVER_COUNT:
            selected = random.sample(cleaned, SERVER_COUNT)
            status = "OK"
        elif len(cleaned) > 0:
            selected = cleaned
            status = "PARTIAL"
            missing["partial"].append({
                "country": country["name"],
                "cc": country["cc"],
                "found": len(cleaned),
            })
        else:
            selected = []
            status = "MISSING"
            missing["missing"].append({
                "country": country["name"],
                "cc": country["cc"],
                "found": 0,
            })

        if selected:
            results[country["cc"]] = {
                "country": country["name"],
                "cc": country["cc"],
                "servers": selected,
            }

            server_ids_by_country[country["cc"]] = [
                server["id"] for server in selected
            ]

            server_ids_txt_lines.append(
                f"# {country['name']} ({country['cc']})"
            )

            for server in selected:
                server_ids_txt_lines.append(
                    f"{server['id']} # {server['sponsor']} / {server['name']}"
                )

            server_ids_txt_lines.append("")

        print(f"[{status}] {country['name']}: {len(selected)} servers")
        time.sleep(SLEEP_SECONDS)

    with open("speedtest_servers_by_country.json", "w") as f:
        json.dump(results, f, indent=2)

    with open("speedtest_server_ids_by_country.json", "w") as f:
        json.dump(server_ids_by_country, f, indent=2)

    with open("speedtest_server_ids.txt", "w") as f:
        f.write("\n".join(server_ids_txt_lines))

    with open("missing_countries.json", "w") as f:
        json.dump(missing, f, indent=2)

    print("")
    print("DONE")
    print("Saved: speedtest_servers_by_country.json")
    print("Saved: speedtest_server_ids_by_country.json")
    print("Saved: speedtest_server_ids.txt")
    print("Saved: missing_countries.json")


if __name__ == "__main__":
    main()
