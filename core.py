from pprint import pprint
from vk_api.exceptions import ApiError
from config import acces_token

import vk_api

# получение данных о пользователе
class VkTools:
    def __init__(self, acces_token):
        self.vkapi = vk_api.VkApi(token=acces_token)
    
    #Вычисление параметров.
    def get_profile_info(self, user_id):
        try:
            info, = self.vkapi.method('users.get',
                                        {
                                        'user_id': user_id,
                                        'fields': 'city,sex,bdate,relation,bdate'
                                        }
                                        )           
        except ApiError as e:
            info ={}
            print(f'Хьюстон, у нас проблемы = {e}.')

        result = {'name' : (info ['first_name'] + ' ' + info ['last_name']) if 
                  'first_name' in info and 'last_name' in info else None,
                  'sex' : info.get('sex'),
                  'city' : info.get('city')['title'] if info.get('city') is not None else None,
                  'year' : self._bdate_toyear(info.get('bdate'))
                  }
        return result
    
    #Вычисление параметров.
    def search_worksheet(self,params,offset):
        try:
            users = self.vkapi.method('users.search',
                                {'count': 50,
                                 'offset': offset,
                                 'hometown':params['city'],
                                 'sex': 1 if params['sex'] == 2 else 2,
                                 'has_photo': True,
                                 'age_from': params['year'] -3,
                                 'age_to': params['year'] +3,
                                 }
                                 )
        except ApiError as e:
            user =[]
            print(f'Хьюстон, у нас проблемы = {e}.')

        #Причесали поиск.
        result = [{'name': item['first_name'] + ' ' + item['last_name'],
                    'id': item['id']
                    } 
                for item in users['items'] if item['is_closed'] is False
                 ]       
        return result

    #Поиск фото.
    def get_photos(self, id):
        try:
            photos = self.vkapi.method('photos.get',
                                {'owner_id': id,                                 
                                 'album_id': 'profile',
                                 'extended': 1
                                 }
                                 )
        except ApiError as e:
            photos ={}
            print(f'Хьюстон, у нас проблемы = {e}.')

        #Параметры фото.
        result = [{'owner_id': item['owner_id'],
                   'id': item['id'],
                   'likes': item['likes']['count'],
                   'comments': item['comments']['count']
                    } for item in photos['items']
                   ]
        
        #Здесь сортируем по лайкам и коментариям. 
        result.sort(key=lambda x: (x['likes'] + x['comments']), reverse=True)
        return result[:3]
        
if __name__ == '__main__':
    user_id = 43655950
    tools = VkTools(acces_token)
    params = tools.get_profile_info(user_id)
    worksheets = tools.search_worksheet(params,10)
    worksheet = worksheets.pop()
    photos = tools.get_photos(worksheet['id'])
    pprint(worksheets)

