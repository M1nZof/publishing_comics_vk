import shutil

import requests
import os

from dotenv import load_dotenv


def download_random_comic():
    random_comic_url = 'https://c.xkcd.com/random/comic/'
    random_comic_response = requests.get(random_comic_url)
    random_comic_response.raise_for_status()

    random_comic_url_with_json = os.path.join(random_comic_response.url, 'info.0.json')
    random_comic = requests.get(random_comic_url_with_json)
    random_comic.raise_for_status()

    comic_image_link = random_comic.json()['img']

    download_image(comic_image_link, 'comic')

    return random_comic.json().get('alt')


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
    check_error_of_vk_api_response(photo_link_response)
    upload_url = photo_link_response.json()['response']['upload_url']
    user_id = photo_link_response.json()['response']['user_id']

    with open(os.path.join('comics', 'comic.png'), 'rb') as file:
        files = {'photo': file}
        upload_response = requests.post(upload_url, files=files)
    upload_response.raise_for_status()
    check_error_of_vk_api_response(upload_response)
    server, formatted_photo, photo_hash = upload_response.json().values()

    return user_id, server, formatted_photo, photo_hash


def save_photo(user_id, group_id, formatted_photo,
               server, hash, access_token):
    request_base_url = 'https://api.vk.com/method'
    save_photo_url = f'{request_base_url}/photos.saveWallPhoto'

    payload = {
        'user_id': user_id,
        'group_id': group_id,
        'photo': formatted_photo,
        'server': server,
        'hash': hash,
        'access_token': access_token,
        'v': '5.131'
    }
    save_photo_response = requests.post(save_photo_url, data=payload)
    save_photo_response.raise_for_status()
    check_error_of_vk_api_response(save_photo_response)

    save_photo_response_formatted = save_photo_response.json()['response'][0]
    media_id = save_photo_response_formatted['id']
    owner_id = save_photo_response_formatted['owner_id']
    
    return media_id, owner_id


def post_photo(owner_id, photo_owner_id, media_id, description, access_token):
    request_base_url = 'https://api.vk.com/method'
    post_photo_url = f'{request_base_url}/wall.post'

    payload = {
        'owner_id': f'-{owner_id}',
        'friends_only': 1,
        'from_group': 0,
        'attachments': f'photo{str(photo_owner_id)}_{str(media_id)}',
        'message': description,
        'access_token': access_token,
        'v': '5.131'
    }

    post_photo_response = requests.post(post_photo_url, data=payload)
    post_photo_response.raise_for_status()
    check_error_of_vk_api_response(post_photo_response)


def check_error_of_vk_api_response(response):
    formatted_response = response.json()
    if formatted_response.get('error'):
        raise Exception(
            f"Code {formatted_response['error']['error_code']} - {formatted_response['error']['error_msg']}"
        )


def download_image(url, filename, path='comics', payload=None):
    response = requests.get(url, params=payload)
    response.raise_for_status()
    _, file_format = os.path.splitext(url)

    image_path = os.path.join(path, f'{filename}{file_format}')
    with open(image_path, 'wb') as file:
        file.write(response.content)     


def delete_comics_directory(directory_name):
    current_directory_path = os.getcwd()
    comics_directory_path = os.path.join(current_directory_path, directory_name)
    comic_path = os.path.join(comics_directory_path, 'comic.png')
    os.remove(comic_path)

   
if __name__ == '__main__':
    load_dotenv()
    vk_access_token = os.environ['VK_ACCESS_TOKEN']
    vk_group_id = os.environ['VK_GROUP_ID']
    comics_directory = 'comics'

    os.makedirs(comics_directory, exist_ok=True)
    comic_description = download_random_comic()
    try:
        user_id, server, vk_formatted_photo, photo_hash = upload_photo(vk_group_id, vk_access_token)
    finally:
        delete_comics_directory(comics_directory)
    save_photo_media_id, save_photo_owner_id = save_photo(user_id, vk_group_id,
                                                          vk_formatted_photo, server,
                                                          photo_hash, vk_access_token)
    post_photo(vk_group_id, save_photo_owner_id, save_photo_media_id, comic_description, vk_access_token)
