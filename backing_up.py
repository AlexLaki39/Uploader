import json
import requests
from datetime import date
from tqdm import tqdm


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
        with open('photos_info.json', 'w') as file:
            json.dump(response.json(), file)

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

    def upload(self, user_id):
        """
        Method uploads photos by list to a specified folder in the cloud.
        File names are the number of likes.
        """
        url_upload = self.base_host_ya + 'v1/disk/resources/upload'
        for key, value in tqdm(self.page_photos.items(), ncols=100,
                               dynamic_ncols=True, desc='Loading'):
            params = {'path': f"{user_id}/{key}", 'url': value}
            response_upload = requests.post(url_upload,
                                            headers=self._get_headers(),
                                            params=params)
        if response_upload.status_code == 202:
            print('Загрузка прошла успешно!')
        else:
            print(f'Ошибка: {response_upload.status_code}')


if __name__ == '__main__':
    user_id = input('Введите id пользователя: ')
    token_disk = input('Введите токен Яндекс диска: ')
    ya = Uploader(token_disk)
    ya.get_photo_profile(user_id)
    ya.create_folder(user_id)
    ya.upload(user_id)
