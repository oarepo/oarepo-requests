BASE_URL = "/thesis/"
BASE_URL_REQUESTS = "/requests/"


def link_api2testclient(api_link):
    base_string = "https://127.0.0.1:5000/api/"
    return api_link[len(base_string) - 1 :]
