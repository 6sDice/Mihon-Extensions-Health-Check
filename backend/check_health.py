import json
from concurrent.futures import ThreadPoolExecutor

from curl_cffi import requests

site_list = []


def get_live_extension_list():
    index_url = (
        "https://raw.githubusercontent.com/keiyoushi/extensions/repo/index.min.json"
    )

    response = requests.get(index_url, impersonate="chrome124")
    data = response.json()

    for ext in data:
        if ext.get("lang") == "en":
            for source in ext.get("sources", []):
                if "baseUrl" in source:
                    site_list.append({"name": source["name"], "url": source["baseUrl"]})
    return site_list


def getStatus(site_list):
    with ThreadPoolExecutor(max_workers=12) as executor:
        results = list(executor.map(check_site_status, site_list))
    return results


def check_site_status(site):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br, zstd",
    }
    try:
        response = requests.get(
            site["url"], impersonate="chrome_android", timeout=10, headers=headers
        )
        final_response = response
        if response.status_code == 403:
            new_headers = headers.copy()
            new_headers["Referer"] = "https://www.google.com/"
            retry_response = requests.get(site["url"], headers=new_headers)
            final_response = retry_response

        return {
            "name": site["name"],
            "url": site["url"],
            "status": "UP"
            if final_response.status_code == 200
            else "CLOUDFLARE"
            if final_response.status_code == 403
            else "DOWN",
            "code": final_response.status_code,
        }
    except Exception as e:
        return {
            "name": site["name"],
            "url": site["url"],
            "status": "ERROR",
            "error": str(e),
        }


if __name__ == "__main__":
    data = get_live_extension_list()
    result = getStatus(data)
    with open("status.json", "w") as f:
        json.dump(result, f)
