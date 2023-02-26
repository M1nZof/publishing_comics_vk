# `publishing_comics_vk`

Скрипт скачивает рандомный комикс с [ресурса](https://xkcd.com/) и публикует его на странице пользователя в VK

## Настройка окружения

```
VK_ACCESS_TOKEN=ISDFgbi2435ASKFBfjkbnxcg
VK_GROUP_ID=34634564537
```

- `VK_ACCESS_TOKEN` - Токен VK;
- `VK_GROUP_ID` - ID группы VK;
(у пользователя положительное число, у сообщества отрицательное)

Узнать ID приложения можно из адреса: https://vk.com/editapp?id=123123123&section=info
[Список приложений](https://vk.com/apps?act=manage)  
[Как узнать VK ID](https://regvk.com/id/)

## Как запустить

### Установка используемых библиотек:

```
pip install -r requirements.txt
```

### Запуск скрипта:

```
python publish_comics.py
```

## Описание функций

Код разбит на несколько функций, выполняющие пошаговые запросы на загрузку комиксов и API VK

### `download_image`

Функция загрузки фото.
Принимает обязательные аргументы:

- `url` - ссылка откуда скачивать фото;
- `filename` - как назвать фото;
- `path` - путь, куда сохранять фото

Опциональный аргумент:

- `payload` - параметры запроса на `url` (по умолчанию - None)

### `download_random_comic`

Функция запрашивает рандомный комикс благодаря встроенной ссылке на [ресурсе](https://xkcd.com/) случайный комикс по следующей [ссылке](https://c.xkcd.com/random/comic/).
Картинка комикса скачивается по функции `download_image`.
Функция возвращает описание комикса (комментарий автора)

### `upload_photo`

Функция загрузки фото на сервера VK. Фото **должно** лежать в папке `comics` и называться `comics.png`
Принимает обязательные аргументы:

- `request_base_url` - базовая ссылка на VK API;
- `group_id` - ID группы VK;
- `access_token` - ключ доступа VK

Возвращает `user_id`, `server`, `formatted_photo`, `photo_hash`

[Метод VK API](https://dev.vk.com/method/photos.getWallUploadServer)  

[Как получить ключ доступа VK](https://dev.vk.com/api/access-token/implicit-flow-user)

### `save_photo`

Функция сохраняет фото в альбом.
Принимает обязательные аргументы:

- `user_id` - ID пользователя;
- `group_id` - ID группы VK;
- `formatted_photo` - список форматов фото, который был получен в `upload_photo_and_get_vk_formatted_photo`;
- `server` - сервер, на который было загружено фото, который был получен в `upload_photo_and_get_vk_formatted_photo`;
- `hash` - hash загруженного фото, который был получен в `upload_photo_and_get_vk_formatted_photo`;
- `access_token` - ключ доступа VK

Возвращает `media_id`, `owner_id`

[Метод VK API](https://dev.vk.com/method/photos.saveWallPhoto)  

[Как получить ключ доступа VK](https://dev.vk.com/api/access-token/implicit-flow-user)

### `post_photo`

Принимает обязательные аргументы:
- `photo_owner_id` - ID владельца фото;
- `owner_id` - ID владельца приложения, который был получен в `save_photo_and_get_media_and_owner_ids`;
- `media_id` - ID приложения, который был получен в `save_photo_and_get_media_and_owner_ids`;
- `description` - сообщение (описание комикса);
- `access_token` - ключ доступа VK;

[Метод VK API](https://dev.vk.com/method/wall.post)  

[Как получить ключ доступа VK](https://dev.vk.com/api/access-token/implicit-flow-user)

### `check_error_of_vk_api_response`

Метод проверки ошибок VK API

Принимает обязательный аргумент:
- `response` - ответ от VK API

### `delete_comics_directory`

Метод удаления директории `comics` с ее содержимым
