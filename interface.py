from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import comunity_token, acces_token
from core import VkTools
from data_store import check_user, add_user, engine

import vk_api


class BotInterface():
    def __init__(self, comunity_token, acces_token):
        self.vk = vk_api.VkApi(token=comunity_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(acces_token)
        self.params = {}
        self.worksheets = []
        self.keys = []
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send',
                       {'user_id': user_id,
                        'message': message,
                        'attachment': attachment,
                        'random_id': get_random_id()}
                       )

    def photos_for_send(self, worksheet):
        photos = self.vk_tools.get_photos(worksheet['id'])
        photo_string = ''
        for photo in photos:
            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
        return photo_string

#  Добавление и проверка БД.
    def get_profile(self, worksheets, event):
        while True:           
            if worksheets:
                worksheet = worksheets.pop()
                if not check_user(engine, event.user_id, worksheet['id']):
                    add_user(engine, event.user_id, worksheet['id'])
                    yield worksheet
            else:
                worksheets = self.vk_tools.search_worksheet(
                    self.params, self.offset)

# Jбработка событий / получение сообщений.
    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':

# Логика для получения данных о пользователе.
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(
                        event.user_id, f'Приветствую тебя {self.params["name"]} в это непростое время.')               
                    self.message_send(event.user_id, 'Напиши "Поиск" и ты найдешь себе пару.')
                elif event.text.lower() == 'поиск':

# Логика для поиска анкет.
                    try:
                        self.message_send(
                            event.user_id, 'Активация поиска.')
                        research = next(iter(self.get_profile(self.worksheets, event)))
                        if research:
                            photo_string = self.photos_for_send(research)
                            self.offset += 50
                            self.message_send(
                                event.user_id,
                                f'Пользователь: {research["name"]}. \n Аккаунт id{research["id"]}.',
                                attachment=photo_string
                            )
                    except:
                        self.message_send(event.user_id, 'Постой, а где привет? :)')
                elif event.text.lower() == 'пока':
                    self.message_send(
                        event.user_id, 'До новых встреч.')
                else:
                    self.message_send(
                        event.user_id, 'Поприветствуй нас для начала знакомства с нами и следуй подсказкам. :)')


if __name__ == '__main__':
    bot_interface = BotInterface(comunity_token, acces_token)
    bot_interface.event_handler()
