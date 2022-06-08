# Yeahbut Jun 2022
# Mojang API Interface

import urllib.request
import json
import base64

def username_to_uuid(name):
    url = f"https://api.mojang.com/users/profiles/minecraft/{name}"
    request = urllib.request.Request(url)
    return json.loads(urllib.request.urlopen(request).read().decode('utf8'))

def _usernames_to_uuids(names):
    url = "https://api.minecraftservices.com/player/certificates"
    request = urllib.request.Request(url, data=json.dumps(names).encode('utf-8'), method='POST')
    request.add_header("Content-Type", "application/json")
    return json.loads(urllib.request.urlopen(request).read().decode('utf8'))

def uuid_to_name_history(uuid):
    url = f"https://api.mojang.com/user/profiles/{uuid}/names"
    request = urllib.request.Request(url)
    return json.loads(urllib.request.urlopen(request).read().decode('utf8'))

def uuid_to_profile(uuid):
    url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
    request = urllib.request.Request(url)
    return json.loads(urllib.request.urlopen(request).read().decode('utf8'))

def uuid_to_profile_texture(uuid):
    data = uuid_to_profile(uuid)['properties']
    for i in data:
        if i['name'] == 'textures':
            return json.loads(base64.b64decode(i['value']).decode('utf-8'))

def uuid_to_skin(uuid):
    data = uuid_to_profile_texture(uuid)
    if data is not None and 'SKIN' in data['textures']:
        url = data["textures"]["SKIN"]["url"]
        request = urllib.request.Request(url)
        return urllib.request.urlopen(request).read()

def uuid_to_cape(uuid):
    data = uuid_to_profile_texture(uuid)
    if data is not None and 'CAPE' in data['textures']:
        url = data["textures"]["CAPE"]["url"]
        request = urllib.request.Request(url)
        return urllib.request.urlopen(request).read()

def _blockedservers():
    url = "https://sessionserver.mojang.com/blockedservers"
    request = urllib.request.Request(url)
    return json.loads(urllib.request.urlopen(request).read().decode('utf8'))

def profile_info(access_token):
    url = "https://api.minecraftservices.com/minecraft/profile"
    request = urllib.request.Request(url)
    request.add_header("Authorization",f"Bearer {access_token}")
    return json.loads(urllib.request.urlopen(request).read().decode('utf8'))

def _player_attributes(access_token):
    url = "https://api.minecraftservices.com/player/attributes"
    request = urllib.request.Request(url)
    request.add_header("Authorization",f"Bearer {access_token}")
    return json.loads(urllib.request.urlopen(request).read().decode('utf8'))

def _player_blocklist(access_token):
    url = "https://api.minecraftservices.com/privacy/blocklist"
    #Authorization: Bearer <access token>
    request = urllib.request.Request(url)
    request.add_header("Authorization",f"Bearer {access_token}")
    return json.loads(urllib.request.urlopen(request).read().decode('utf8'))

def _player_certificates(access_token):
    url = "https://api.minecraftservices.com/player/certificates"
    request = urllib.request.Request(url, method='POST')
    request.add_header("Authorization",f"Bearer {access_token}")
    return json.loads(urllib.request.urlopen(request).read().decode('utf8'))

def _profile_name_change_information(access_token):
    url = "https://api.minecraftservices.com/minecraft/profile/namechange"
    request = urllib.request.Request(url)
    request.add_header("Authorization",f"Bearer {access_token}")
    return json.loads(urllib.request.urlopen(request).read().decode('utf8'))

def _name_availability(access_token, name):
    url = f"https://api.minecraftservices.com/minecraft/profile/name/{name}/available"
    request = urllib.request.Request(url)
    request.add_header("Authorization",f"Bearer {access_token}")
    return json.loads(urllib.request.urlopen(request).read().decode('utf8'))

def _change_name(access_token, name):
    url = f"https://api.minecraftservices.com/minecraft/profile/name/{name}"
    request = urllib.request.Request(url, method='PUT')
    request.add_header("Authorization",f"Bearer {access_token}")
    return json.loads(urllib.request.urlopen(request).read().decode('utf8'))

def change_skin(access_token, variant, skin_url):
    url = "https://api.minecraftservices.com/minecraft/profile/skins"
    payload = {
        "variant": variant,
        "url": skin_url
    }
    request = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), method='POST')
    request.add_header("Authorization",f"Bearer {access_token}")
    request.add_header("Content-Type", "application/json")
    return urllib.request.urlopen(request).read().decode('utf8')

def __upload_skin(access_token, variant, image): # WIP -----------------------------------------------
    url = "https://api.minecraftservices.com/minecraft/profile/skins"
    request = urllib.request.Request(url, method='POST')
    request.add_header("Authorization",f"Bearer {access_token}")
    return urllib.request.urlopen(request).read().decode('utf8')

def reset_skin(access_token, uuid):
    url = f"https://api.mojang.com/user/profile/{uuid}/skin"
    request = urllib.request.Request(url, method='DELETE')
    request.add_header("Authorization",f"Bearer {access_token}")
    return urllib.request.urlopen(request).read().decode('utf8')

def hide_cape(access_token):
    url = "https://api.minecraftservices.com/minecraft/profile/capes/active"
    request = urllib.request.Request(url, method='DELETE')
    request.add_header("Authorization",f"Bearer {access_token}")
    return urllib.request.urlopen(request).read().decode('utf8')

def show_cape(access_token, cape_id):
    url = "https://api.minecraftservices.com/minecraft/profile/capes/active"
    payload = {
        "capeId": cape_id
    }
    request = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), method='PUT')
    request.add_header("Authorization",f"Bearer {access_token}")
    return json.loads(urllib.request.urlopen(request).read().decode('utf8'))

if __name__ == "__main__":
    with open('test.png', 'wb') as file:
        file.write(uuid_to_skin("b874ee0001f74b6f841b00e820e6c1f2"))
