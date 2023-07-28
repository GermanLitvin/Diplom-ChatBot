from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import comunity_token, acces_token
from core import VkTools
from data_store import check_user, add_user, engine
from datetime import datetime

import vk_api
import re


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
    
    def _bdate_toyear(salf, bdate):
        user_year = bdate.split('.')[2]
        now = datetime.now().year
        return now - int(user_year)

# Проверка всех пfраметров пользователя.
    def new_message(self, x):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if x == 0:
                    contains_digit = False
                    for y in event.text:
                        if y.isdigit():
                            contains_digit = True
                            break
                    if contains_digit:
                        self.message_send(event.user_id, 'Давайте знакомится, введите пожалуйста ваше имя и фамилию:')
                    else:
                        return event.text

                if x == 1:
                    if event.text == "1" or event.text == "2":
                        return int(event.text)
                    else:
                        self.message_send(event.user_id, 'Вы мальчик или девочка? Введите ваш пол : Мужской - 1, Женский - 2:')

                if x == 2:
                    contains_digit = False
                    for y in event.text:
                        if y.isdigit():
                            contains_digit = True
                            break
                    if contains_digit:
                        self.message_send(event.user_id, 'От куда вы? Введите пожалуйста название вашего города:')
                    else:
                        return event.text

                if x == 3:
                    pattern = r'^\d{2}\.\d{2}\.\d{4}$'
                    if not re.match(pattern, event.text):
                        self.message_send(event.user_id, 'А когда у вас День Рождение? Пожалуйста, введите дату вашего рождение (формат - дд.мм.гггг):')
                    else:
                        return self._bdate_toyear(event.text)

    def recon(self, event):
        if self.params['name'] is None:
            self.message_send(event.user_id, 'Введите ваше имя и фамилию:')
            return self.new_message(0)

        if self.params['sex'] is None:
            self.message_send(event.user_id, 'Введите свой пол (1-м, 2-ж):')
            return self.new_message(1)

        elif self.params['city'] is None:
            self.message_send(event.user_id, 'Введите город:')
            return self.new_message(2)

        elif self.params['year'] is None:
            self.message_send(event.user_id, 'Введите вашу дату рождения (формат - дд.мм.гггг):')
            return self.new_message(3)

#Добавление и проверка БД.
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

# обработка событий / получение сообщений
    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':

                    '''Логика для получения данных о пользователе'''
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(
                        event.user_id, f'Приветствую тебя {self.params["name"]} в это непростое время.')   
                    self.keys = self.params.keys()
                    for inf in self.keys:
                        if self.params[inf] is None:
                            self.params[inf] = self.recon(event)
                    self.message_send(event.user_id, 'Напиши "Поиск" и ты найдешь себе пару.')
                elif event.text.lower() == 'поиск':

                    #Логика для поиска анкет
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
