import json
import requests
from datetime import date
from tqdm import tqdm
import mimetypes
class Uploader:
    """
    access_token: token for sending vk requests;
    toke_disk: token for sending yandex disk requests;
    user_id: user id of the VK.
     """
    base_host_ya = 'https://cloud-api.yandex.net/'

    def __init__(self, token_disk, access_token='...'):
        self.token_disk = token_disk
        self.access_token = # You need to specify the token for requests to VK
        self.page_photos = {}
        self.photo_size = {}


    def get_photo_profile(self, user_id):
        """
        The method gets the user's profile photo in maximum quality.
        """
        get_photo_url = 'https://api.vk.com/method/photos.get'
        params = {'access_token': self.access_token, 'owner_id': user_id,
                  'v': '5.131', 'album_id': 'profile', 'extended': '1',
                  'photo_sizes': '1', 'rev': '0'}
        response = requests.get(get_photo_url, params=params)
        for values in response.json().values():
            for largest_photo in values['items']:
                likes = str(largest_photo['likes']['count'])
                photo_date = largest_photo['date']
                f_photo_date = str(date.fromtimestamp(photo_date))
                if likes in self.page_photos.keys():
                    self.page_photos[likes + ' ' + f_photo_date] =\
                       largest_photo['sizes'][-1]['url']
                else:
                    self.page_photos[likes] = largest_photo['sizes'][-1]['url']
                if likes in self.photo_size.keys():
                    self.photo_size[likes + ' ' + f_photo_date] =\
                        largest_photo['sizes'][-1][
                        'type']
                else:
                    self.photo_size[likes] = largest_photo['sizes'][-1]['type']
    def _get_headers(self):
        return {
            'Content-type': 'application/json',
            'Authorization': f'OAuth {self.token_disk}'
        }

    def create_folder(self, user_id):
        """
        Method creates a folder in the cloud storage.
        """
        folder_url = self.base_host_ya + 'v1/disk/resources'
        params = {'path': user_id}
        response_folder = requests.put(folder_url, headers=self._get_headers(),
                                       params=params)
        return response_folder

    def upload(self, user_id, num_photos):
        """
        Method uploads photos by list to a specified folder in the cloud.
        File names are the number of likes.
        Сreates a json file with information about the photo.
        """
        url_upload = self.base_host_ya + 'v1/disk/resources/upload'
        num_photo = -1
        list_info_photo = []
        for key, value in tqdm(self.page_photos.items(), ncols=100,
                               dynamic_ncols=True, desc='Loading'):
            num_photo += 1
            if num_photo == num_photos:
                break
            params = {'path': f"{user_id}/{key}", 'url': value,
                      'disable_redirects': True}
            response_upload = requests.post(url_upload,
                                            headers=self._get_headers(),
                                            params=params)
            dict_1 = {}
            dict_1['file_name'] = f"{key}.{mimetypes.guess_type(params['url'], strict=True)[0]}"
            dict_1['size'] = self.photo_size[f'{key}']
            list_info_photo.append(dict_1)
        if response_upload.status_code == 202:
            print('Загрузка прошла успешно!')
        else:
            print(f'Ошибка: {response_upload.status_code}')
        with open('photos_info.json', 'w') as file:
            json.dump(list_info_photo, file)


if __name__ == '__main__':
    user_id = input('Введите id пользователя: ')
    token_disk = input('Введите токен Яндекс диска: ')
    ya = Uploader(token_disk)
    ya.get_photo_profile(user_id)
    num_photos = input(
        f'Введите количество фото из {len(ya.page_photos)}, которое хотите '
        f'загрузить(по умолчанию 5): ')
    while type(num_photos) != int or num_photos <= 0:
        try:
            num_photos = int(num_photos)
        except ValueError:
            if num_photos == '':
                print('number = 5')
                num_photos = 5
            else:
                print('Количество загружаемых фотографий должно быть больше 0')
                num_photos = int(input(
                    f'Введите количество фото из {len(ya.page_photos)}, которое хотите '
                    f'загрузить(по умолчанию 5): '))
        else:
            if num_photos > 0:
                break
            else:
                print('Количество загружаемых фотографий должно быть больше 0')
                num_photos = int(input(
                    f'Введите количество фото из {len(ya.page_photos)}, которое хотите '
                    f'загрузить(по умолчанию 5): '))
    ya.create_folder(user_id)
    ya.upload(user_id, num_photos)