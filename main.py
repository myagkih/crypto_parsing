import requests
from bs4 import BeautifulSoup


def get_tokens(limit):
    url = "https://etherscan.io/tokens"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка: {e}")
        return []

    soup = BeautifulSoup(r.content, 'html.parser')
    tokens = []

    table = soup.select_one("table.table.table-hover.mb-0")
    if not table:
        print("Таблица не найдена.")
        return []

    rows = table.select("tbody tr")
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 4:
            continue

        name_td = cols[1]
        link_el = name_td.find('a')
        if not link_el:
            continue

        name = link_el.get_text(strip=True)

        rel_link = link_el.get('href')
        full_link = f"https://etherscan.io{rel_link}" if rel_link else None

        price_td = cols[3]
        price_el = price_td.select_one('.d-inline[data-bs-title]')

        if price_el:
            price_text = price_el.get('data-bs-title', '')
            if not price_text:
                price_text = price_el.get_text(strip=True)
        else:
            price_div = price_td.select_one('.d-inline')
            if price_div:
                price_text = price_div.get_text(strip=True)
            else:
                continue

        clean_price = price_text.replace('$', '').replace(',', '').strip()
        try:
            price = float(clean_price)
        except ValueError:
            continue

        tokens.append({
            'name': name,
            'price': price,
            'link': full_link
        })

    tokens.sort(key=lambda x: x['price'], reverse=True)
    return tokens[:limit]


if __name__ == "__main__":
    try:
        n = int(input("Сколько токенов вывести: "))
    except ValueError:
        print("Ошибка: нужно число.")
        exit()

    token_list = get_tokens(n)

    if not token_list:
        print("Токены не найдены.")
    else:
        print(f"\nТоп-{n} токенов по цене:")
        print("-" * 80)
        for i, token in enumerate(token_list, 1):

            print(f"{i:2d}. {token['name']:40} - ${token['price']:12.2f} - {token['link']}")
