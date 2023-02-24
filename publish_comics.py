import shutil

import requests
import os

from dotenv import load_dotenv


def download_random_comics():
    random_comics_url = 'https://c.xkcd.com/random/comic/'
    random_comics_response = requests.get(random_comics_url)
    random_comics_response.raise_for_status()

    random_comics_url_with_json = os.path.join(random_comics_response.url, 'info.0.json')
    random_comics = requests.get(random_comics_url_with_json)
    random_comics.raise_for_status()

    comics_image_link = random_comics.json()['img']

    download_image(comics_image_link, 'comics')

    return random_comics.json().get('alt')


def upload_photo(group_id, access_token):
    request_base_url = 'https://api.vk.com/method'
    payload = {
        'group_id': group_id,
        'access_token': access_token,
        'v': '5.131'
    }

    get_photo_link = f'{request_base_url}/photos.getWallUploadServer'

    photo_link_response = requests.get(get_photo_link, params=payload)
    photo_link_response.raise_for_status()
    upload_url = photo_link_response.json()['response']['upload_url']

    with open(os.path.join('comics', 'comics.png'), 'rb') as file:
        files = {'photo': file}
        upload_response = requests.post(upload_url, files=files)
        upload_response.raise_for_status()
    delete_directory_and_content('comics')
    server, formatted_photo, photo_hash = upload_response.json().values()
    return server, formatted_photo, photo_hash


def save_photo(application_id, group_id, formatted_photo,
               server, hash, access_token):
    request_base_url = 'https://api.vk.com/method'
    save_photo_url = f'{request_base_url}/photos.saveWallPhoto'

    payload = {
        'user_id': application_id,
        'group_id': group_id,
        'photo': formatted_photo,
        'server': server,
        'hash': hash,
        'access_token': access_token,
        'v': '5.131'
    }
    save_photo_response = requests.post(save_photo_url, data=payload)
    save_photo_response.raise_for_status()
    save_photo_response_formatted = save_photo_response.json()['response'][0]
    media_id = save_photo_response_formatted['id']
    owner_id = save_photo_response_formatted['owner_id']
    
    return media_id, owner_id


def post_photo(wall_owner_id, photo_owner_id, media_id, description, access_token):
    request_base_url = 'https://api.vk.com/method'
    post_photo_url = f'{request_base_url}/wall.post'

    payload = {
        'owner_id': wall_owner_id,
        'friends_only': 1,
        'from_group': 0,
        'attachments': 'photo' + str(photo_owner_id) + '_' + str(media_id),
        'message': description,
        'access_token': access_token,
        'v': '5.131'
    }

    post_photo_response = requests.post(post_photo_url, data=payload)
    post_photo_response.raise_for_status()


def get_picture_format(picture):
    _, file_format = os.path.splitext(picture)
    return file_format


def create_directory(path):
    os.makedirs(path, exist_ok=True)


def delete_directory_and_content(path):
    shutil.rmtree(path)


def download_image(url, filename, path='comics', payload=None):
    response = requests.get(url, params=payload)
    response.raise_for_status()
    file_format = get_picture_format(url)

    create_directory(path)
    image_path = os.path.join(path, f'{filename}{file_format}')
    with open(image_path, 'wb') as file:
        file.write(response.content)     
   
   
if __name__ == '__main__':
    load_dotenv()
    vk_application_id = os.environ['VK_APPLICATION_ID']
    vk_access_token = os.environ['VK_ACCESS_TOKEN']
    vk_group_id = os.environ['VK_GROUP_ID']
    owner_id = os.environ['VK_OWNER_ID']

    comics_description = download_random_comics()
    server, vk_formatted_photo, photo_hash = upload_photo(vk_group_id, vk_access_token)
    save_photo_media_id, save_photo_owner_id = save_photo(vk_application_id, vk_group_id,
                                                          vk_formatted_photo, server,
                                                          photo_hash, vk_access_token)
    post_photo(owner_id, save_photo_owner_id, save_photo_media_id, comics_description, vk_access_token)
