import json
import time

from curl_cffi import requests

site_list = []


def get_live_extension_list():
    index_url = (
        "https://raw.githubusercontent.com/keiyoushi/extensions/repo/index.min.json"
    )

    # We use requests here just to get the JSON index
    response = requests.get(index_url, impersonate="chrome124")
    data = response.json()

    for ext in data:
        # Filter for English and only extensions that have a defined baseUrl
        if ext.get("lang") == "en":
            for source in ext.get("sources", []):
                if "baseUrl" in source:
                    site_list.append({"name": source["name"], "url": source["baseUrl"]})
    return site_list


def sendOneSite(site_list):
    final_list = []
    for site in site_list[:3]:
        final_list.append(check_site_status(site))
    return final_list


def check_site_status(site):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Cookie": "cf_clearance=q7POtZJRwh.9KnihPwBwzKoV2cST8nhFDO.Gc0YMldA-1775104993-1.2.1.1-FdovOX_iEmzNJxEFGPIpasJQqRZ9pSCVR27AuuV4VK2shoPEvp4tRMq7OLDiMrBumF31Hf5F7gwBlLUe0YUYpEFtseffuh7hGaGayNjxk0bxH5gBVq0GNTIAZD7NIApbM8EOQ441Ow0BgZDK76ICZEgZXSm6sI9wP86vQzKRm6hVB8tgThNkzqffyoSQPjDG.Fq4QHid3bx4_oWAHlCKDXaUl_fDv11s7QFXw.Jab9w; _ga=GA1.1.1195948726.1775104995; fpestid=8tygYsBkh3PnMTTX3EgpDXb7vKpY1e6Mqaqs5f5FvZZWQAFa7D7YZI1iQZEHXQ9X2HUq0Q; _ga_0MPDY2E7QT=GS2.1.s1775104995$o1$g1$t1775105016$j39$l0$h0; _ga_WBZZWKCQVZ=GS2.1.s1775104995$o1$g1$t1775105016$j39$l0$h0",
    }
    try:
        response = requests.get(
            site["url"], impersonate="chrome", timeout=10, headers=headers
        )
        return {
            "name": site["name"],
            "url": site["url"],
            "status": "UP" if response.status_code == 200 else "DOWN",
            "code": response.status_code,
        }
    except Exception as e:
        return {
            "name": site["name"],
            "url": site["url"],
            "status": "ERROR",
            "error": str(e),
        }


if __name__ == "__main__":
    # Your execution logic goes here
    data = get_live_extension_list()
    result = sendOneSite(data)
    with open("status.json", "w") as f:
        json.dump(result, f)
