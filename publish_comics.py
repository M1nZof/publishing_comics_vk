import requests
import os

from dotenv import load_dotenv


def download_random_comics():
    comics_url = 'https://c.xkcd.com/random/comic/'
    random_comics_response = requests.get(comics_url)
    random_comics_response.raise_for_status()

    comics_url_with_json = os.path.join(random_comics_response.url, 'info.0.json')
    comics = requests.get(comics_url_with_json)
    comics.raise_for_status()

    comics_image_link = comics.json().get('img')

    image_download(comics_image_link, 'comics', 'comics')

    return comics.json().get('alt')


def upload_photo(request_base_url, group_id, access_token):
    payload = {
        'group_id': group_id,
        'access_token': access_token,
        'v': '5.131'
    }

    get_photo_link = request_base_url + 'photos.getWallUploadServer'

    photo_link_response = requests.get(get_photo_link, params=payload)
    photo_link_response.raise_for_status()
    upload_url = photo_link_response.json().get('response').get('upload_url')

    with open(os.path.join('comics', 'comics.png'), 'rb') as file:
        files = {'photo': file}
        upload_response = requests.post(upload_url, files=files)
        upload_response.raise_for_status()
    server, formatted_photo, photo_hash = upload_response.json().values()
    return server, formatted_photo, photo_hash


def save_photo(request_base_url, application_id, group_id, formatted_photo,
               server, hash, access_token):
    save_photo_url = request_base_url + 'photos.saveWallPhoto'

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
    save_photo_response_formatted = save_photo_response.json().get('response')[0]
    media_id = save_photo_response_formatted.get('id')
    owner_id = save_photo_response_formatted.get('owner_id')
    
    return media_id, owner_id


def post_photo(request_base_url, owner_id, media_id, description, access_token):
    post_photo_url = request_base_url + 'wall.post'

    payload = {
        'owner_id': 622627888,
        'friends_only': 1,
        'from_group': 0,
        'attachments': 'photo' + str(owner_id) + '_' + str(media_id),
        'message': description,
        'access_token': access_token,
        'v': '5.131'
    }

    post_photo_response = requests.post(post_photo_url, data=payload)
    post_photo_response.raise_for_status()

    if post_photo_response.ok:
        os.remove(os.path.join('comics', 'comics.png'))
        os.rmdir('comics')


def get_picture_format(picture):
    _, file_format = os.path.splitext(picture)
    return file_format


def image_download(url, filename, path, payload=None):
    response = requests.get(url, params=payload)
    response.raise_for_status()
    file_format = get_picture_format(url)

    if not os.path.exists(path):
        os.mkdir(path)

    image_path = os.path.join(path, (f'{filename}{file_format}'))
    with open(image_path, 'wb') as file:
        file.write(response.content)     
   
   
if __name__ == '__main__':
    load_dotenv()
    vk_application_id = os.environ['VK_APPLICATION_ID']
    vk_access_token = os.environ['VK_ACCESS_TOKEN']
    vk_group_id = 218998463
    vk_request_base_url = 'https://api.vk.com/method/'

    comics_description = download_random_comics()
    server, vk_formatted_photo, photo_hash = upload_photo(vk_request_base_url,
                                                          vk_group_id, vk_access_token)
    save_photo_media_id, save_photo_owner_id = save_photo(vk_request_base_url,
                                                          vk_application_id, vk_group_id,
                                                          vk_formatted_photo, server,
                                                          photo_hash, vk_access_token)
    post_photo(vk_request_base_url, save_photo_owner_id, save_photo_media_id, comics_description, vk_access_token)
