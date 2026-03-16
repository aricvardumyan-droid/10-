import requests
import sys
from io import BytesIO
from PIL import Image
from spn import toponyms_to_spn
from recursive_get import get


toponym_to_find = " ".join(sys.argv[1:])

geocode_api_server = 'http://geocode-maps.yandex.ru/1.x/'

geocoder_params = {"apikey": "7eb1332d-4876-4b40-b314-76834f59eef7", "geocode": toponym_to_find, "format": "json"}

response = requests.get(geocode_api_server, geocoder_params)
target = response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
address_ll = get(target, 'Point', 'pos')


search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"


search_params = {"apikey": api_key, "text": "аптека", "lang": "ru_RU", "ll": address_ll.replace(' ', ','), "type": "biz"}

response = requests.get(search_api_server, params=search_params)
if not response:
    pass


pt = []

json_response = response.json()
organizations = json_response["features"][:10]
for organization in organizations:
    org_name = get(organization, "properties", "CompanyMetaData", "name")
    org_address = get(organization, "properties", "CompanyMetaData", "address")

    point = organization["geometry"]["coordinates"]
    org_point = f"{point[0]},{point[1]}"

    availabilities = get(organization, 'properties', 'CompanyMetaData', 'Hours', 'Availabilities', default=[])
    is24hours = None
    for entry in availabilities:
        if is24hours is None and 'Everyday' in entry and entry['Everyday']:
            is24hours = True
        if 'Intervals' in entry:
            is24hours = False
            break

    pt.append((org_point, 'gr' if is24hours is None else 'dg' if is24hours else 'db'))


apikey = "ed983e3f-c780-4aab-9899-589fda08af66"

spn = toponyms_to_spn(get(target, 'boundedBy', 'Envelope'), *[p[0] for p in pt])

map_params = {
    "ll": address_ll.replace(' ', ','),
    "spn": f'{spn[0]},{spn[1]}',
    "apikey": apikey,
    "pt": '~'.join((f"{org_point},pm2{color}l" for org_point, color in pt)),
}

map_api_server = "https://static-maps.yandex.ru/v1"
response = requests.get(map_api_server, params=map_params)
im = BytesIO(response.content)
opened_image = Image.open(im)
opened_image.show()
