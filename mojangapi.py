# Yeahbut Jun 2022
# Mojang API Interface

import requests
import json
import base64
import io

SKIN_VARIANTS = ('Classic','Slim')

def username_to_uuid(name):
    url = f"https://api.mojang.com/users/profiles/minecraft/{name}"
    request = requests.get(url)
    return request.json()

def _usernames_to_uuids(names):
    url = "https://api.minecraftservices.com/player/certificates"
    headers = {"Content-Type": "application/json"}
    request = requests.post(url, data=names, headers=headers)
    return request.json()

def uuid_to_name_history(uuid):
    url = f"https://api.mojang.com/user/profiles/{uuid}/names"
    request = requests.get(url)
    return request.json()

def uuid_to_profile(uuid):
    url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
    request = requests.get(url)
    return request.json()

def uuid_to_profile_texture(uuid):
    data = uuid_to_profile(uuid)['properties']
    for i in data:
        if i['name'] == 'textures':
            return json.loads(base64.b64decode(i['value']).decode('utf-8'))

def uuid_to_skin(uuid):
    data = uuid_to_profile_texture(uuid)
    if data is not None and 'SKIN' in data['textures']:
        url = data["textures"]["SKIN"]["url"]
        request = requests.get(url)
        return request.content

def uuid_to_cape(uuid):
    data = uuid_to_profile_texture(uuid)
    if data is not None and 'CAPE' in data['textures']:
        url = data["textures"]["CAPE"]["url"]
        request = requests.get(url)
        return request.content

def profile_info(access_token):
    url = "https://api.minecraftservices.com/minecraft/profile"
    headers = {"Authorization":f"Bearer {access_token}"}
    request = requests.get(url, headers=headers)
    return request.json()

def _player_attributes(access_token):
    url = "https://api.minecraftservices.com/player/attributes"
    headers = {"Authorization":f"Bearer {access_token}"}
    request = requests.get(url, headers=headers)
    return request.json()

def _player_blocklist(access_token):
    url = "https://api.minecraftservices.com/privacy/blocklist"
    headers = {"Authorization":f"Bearer {access_token}"}
    request = requests.get(url, headers=headers)
    return request.json()

def _player_certificates(access_token):
    url = "https://api.minecraftservices.com/player/certificates"
    headers = {"Authorization":f"Bearer {access_token}"}
    request = requests.post(url, headers=headers)
    return request.json()

def _profile_name_change_information(access_token):
    url = "https://api.minecraftservices.com/minecraft/profile/namechange"
    headers = {"Authorization":f"Bearer {access_token}"}
    request = requests.get(url, headers=headers)
    return request.json()

def _name_availability(access_token, name):
    url = f"https://api.minecraftservices.com/minecraft/profile/name/{name}/available"
    headers = {"Authorization":f"Bearer {access_token}"}
    request = requests.get(url, headers=headers)
    return request.json()

def _change_name(access_token, name):
    url = f"https://api.minecraftservices.com/minecraft/profile/name/{name}"
    headers = {"Authorization":f"Bearer {access_token}"}
    request = requests.put(url, headers=headers)
    return request.json()

def change_skin(access_token, variant, skin_url):
    url = "https://api.minecraftservices.com/minecraft/profile/skins"
    payload = {
        "variant": variant.lower(),
        "url": skin_url
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    request = requests.post(url, data=payload, headers=headers)
    return request.content

def upload_skin(access_token, variant, image, image_name="skin.png"):

    data = {"variant": variant.lower()}
    files = {'file': (image_name, io.BytesIO(image))}

    url = "https://api.minecraftservices.com/minecraft/profile/skins"
    headers = {"Authorization": f"Bearer {access_token}"}
    request = requests.post(url, data=data, files=files, headers=headers)
    return request.content

def reset_skin(access_token, uuid):
    url = f"https://api.mojang.com/user/profile/{uuid}/skin"
    headers = {"Authorization":f"Bearer {access_token}"}
    request = requests.delete(url, headers=headers)
    return request.content

def hide_cape(access_token):
    url = "https://api.minecraftservices.com/minecraft/profile/capes/active"
    headers = {"Authorization":f"Bearer {access_token}"}
    request = requests.delete(url, headers=headers)
    return request.content

def show_cape(access_token, cape_id):
    url = "https://api.minecraftservices.com/minecraft/profile/capes/active"
    payload = {
        "capeId": cape_id
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    request = requests.put(url, data=payload, headers=headers)
    return request.json()

if __name__ == "__main__":
    with open('test.png', 'wb') as file:
        file.write(uuid_to_skin("b874ee0001f74b6f841b00e820e6c1f2"))
