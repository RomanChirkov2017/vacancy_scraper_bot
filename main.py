from fake_useragent import UserAgent
import json
import requests
import os
import asyncio
import aiohttp

from dotenv import load_dotenv
load_dotenv(".env")

API_KEY = os.getenv("SUPERJOB_API_KEY")

ua = UserAgent()


async def collect_hh_data(keywords):
    vacancies_hh_json = []

    url = "https://api.hh.ru/vacancies"
    params = {"per_page": 20, "text": keywords}

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers={'user-agent': f'{ua.random}'}, params=params) as response:
            data = await response.json()

    #response = requests.get(url=url, headers={'user-agent': f'{ua.random}'}, params=params)
    #data = response.json()

    items = data.get('items')

    for item in items:
        name = item.get("name").lower()
        url = item.get("alternate_url")
        salary_info = item.get("salary") or {}
        salary_from = salary_info.get("from", 0)
        salary_to = salary_info.get("to", salary_from)
        currency = salary_info.get("currency", "")
        #description = item.get("snippet").get("requirement", "").replace('<highlighttext>', '').replace('</highlighttext>', '')
        snippet = item.get("snippet", {})
        requirement = snippet.get("requirement") if snippet.get("requirement") is not None else ""
        description = requirement.replace('<highlighttext>', '').replace('</highlighttext>', '')

        vacancies_hh_json.append(
            {
                'name': name,
                'url': url,
                'salary_from': salary_from,
                'salary_to': salary_to,
                'currency': currency,
                'description': description
            }
        )

    with open('vacancies_hh.json', 'w') as file:
        json.dump(vacancies_hh_json, file, indent=4, ensure_ascii=False)

    print(len(vacancies_hh_json))


async def collect_sj_data(keywords):
    vacancies_sj_json = []

    url = "https://api.superjob.ru/2.0/vacancies"
    params = {"count": 20, "keyword": keywords}
    #secret_key = API_KEY
    headers = {"X-Api-App-Id": API_KEY}

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers, params=params) as response:
            data = await response.json()

    #response = requests.get(url=url, headers=headers, params=params)
    #data = response.json()

    objects = data.get('objects')

    for obj in objects:
        name = obj.get("profession").lower()
        url = obj.get("link")
        salary_from = obj.get("payment_from", 0)
        salary_to = obj.get("payment_to") if obj.get("payment_to") != 0 else obj.get("payment_from")
        currency = obj.get("currency").upper()
        description = obj.get("candidat").lower()

        vacancies_sj_json.append(
            {
                'name': name,
                'url': url,
                'salary_from': salary_from,
                'salary_to': salary_to,
                'currency': currency,
                'description': description
            }
        )

    with open('vacancies_sj.json', 'w') as file:
        json.dump(vacancies_sj_json, file, indent=4, ensure_ascii=False)

    print(len(vacancies_sj_json))


async def main():
    keywords = input("Input keyword...")
    await asyncio.gather(collect_hh_data(keywords), collect_sj_data(keywords))

    #print(collect_hh_data(keywords))
    #print(collect_sj_data(keywords))

if __name__ == "__main__":
    asyncio.run(main())