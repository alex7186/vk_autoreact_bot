import vk_api.vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from datetime import datetime
import random
# import sys
import time

# запрещенные сообщения
delete_list = ['Ага', 'ага', '👺', '😈', '👿', '😡', '🌚', '🌝', '👽']
answer_pattern = ['Лол', 'лол', 'Ахах', 'Ахахах', 'Ахахахах', 'Ахахахахах']

# запрещено присылать сообщения выше
not_allowed_id_list = [194801143, 241028460] 
allowed_answering_id_list = [470915582, 249274091]

class Server:

    def __init__(self, api_token, role, server_name=""):

        self.server_name = server_name

        # Для Long Poll
        self.vk_session = vk_api.VkApi(token=api_token)

        # Для вызова методов vk_api session_api
        self.session_api = self.vk_session.get_api()

        # Для использования Long Poll API
        self.long_poll = VkLongPoll(self.vk_session)

        # индикатор работы
        self.flag_should_work = True

        # тип работы
        if role not in ['answering', 'deleter']:
            raise ValueError("Role must be ['answering', 'deleter'] ")
        self.role = role

        self.review()

    def review(self):
        if self.role == 'answering':
            res = f"""answering pattern           : {answer_pattern}
    allowed answering id list   : {[self.get_page_info_by_id(el) for el in allowed_answering_id_list]}"""
        elif self.role == 'deleter':
            res = f"""messages to delete          : {delete_list}
    not allowed sending id list :{[self.get_page_info_by_id(el) for el in not_allowed_id_list]}

    """

        print(f"""
    server name                 : {self.server_name}
    server role                 : {self.role}
    """+res)

    # Отправляем сообщение по id пользователя
    def send_msg(self, user_id, message, random_id=0):
        message_id = self.session_api.messages.send(
            user_id=user_id, 
            message=message, 
            random_id=random_id)

        sender = self.get_page_info_by_id(user_id)
        self.add_log_message('SEND', f"to {' '.join(sender)} : '{message}'")
        return message_id

    def reply_msg(self, user_id, forward_message_id, message, random_id=0):
        message_id = self.session_api.messages.send(
            user_id=user_id,
            reply_to=forward_message_id,
            message=message,
            random_id=random_id)

        sender = self.get_page_info_by_id(user_id)
        self.add_log_message('SEND-FORWARD', f"to {' '.join(sender)} : '{message}' ")
        return message_id

    # Посылаем сообщение пользователю с указанным ID
    def test(self): 
        self.send_msg(1, f"Тестовое сообщение от бота {self.server_name}")
        
    # отправляем текст сообщения по id 
    def get_message_by_id(self, message_id):
        message = self.session_api.messages.getById(
            message_ids=message_id, 
            preview_length=1, 
            extend=0)

        try:
            return message['items'][0]['from_id'], message['items'][0]['text']
        except:
            self.add_log_message('ERROR RETURNING', str(message))
            return ('None', 'None')

    # возвращаем имя и фимилию по id
    def get_page_info_by_id(self, id):
        res = self.session_api.users.get(user_ids=id)[0]
        # print(res['first_name'], res['last_name'])
        return res['first_name'], res['last_name']

    # удаляем сообщение по id
    def delete_message(self, message_id, spam=0, delete_for_all=0):
        arr = self.get_message_by_id(message_id)

        sender = self.get_page_info_by_id(arr[0])
        self.add_log_message("DELETED", f"from {' '.join(sender)} : '{arr[1]}'")

        delete_result = self.session_api.messages.delete(
            message_ids=message_id, 
            spam=spam, 
            delete_for_all=delete_for_all)

        return delete_result # 1, 0

    # выводим в консоль и заносим в бд
    def add_log_message(self, category, message, prefix=''):
        dt_str = "   {:<4}-{:>2}-{:>2} {:>2}:{:>2}:{:>2} ".format(*list(datetime.now().timetuple()))
        res = prefix + f" {self.server_name} " + dt_str + "{:<15}".format(category) + message
        print(res)

        f = open(self.server_name + ".log", "a")
        f.write(res)
        f.close()

    def set_account_online(self):
        self.session_api.account.setOnline()
        self.add_log_message("SET-ONLINE", '')

    def react_as_deleter(self, event, sender, not_allowed_id_list, delete_list):
        # сообщения этих людей фильтруются
        id = int(event.user_id)
        if id in not_allowed_id_list:
            # удаляем стикеры
            if (len(event.attachments) > 0) and ('attach1_type' in list(event.attachments.keys())) and (event.attachments['attach1_type'] == 'sticker'):
                message_id = self.send_msg(id, """Сообщение со стикером было автоматически удалено по желанию пользователя""" )

                self.add_log_message('RECIEVED', f"{' '.join(sender)} : sticker '{event.attachments['attach1']}'") 

                # удаление сообщения об удалении
                self.delete_message(message_id)
                # удаление сообщения
                self.delete_message(event.message_id)

            # удаляем сообщения
            elif event.text in delete_list :

                self.add_log_message('RECIEVED', f"from {' '.join(sender)} : '{event.text}'")
                # сообщение об удалениии
                message_id = self.send_msg(id, """Сообщение '""" + event.text[:10] + """'' было автоматически удалено по желанию пользователя""" )
                # удаление сообщения об удалении
                self.delete_message(message_id)
                # удаление сообщения
                self.delete_message(event.message_id)

    def react_as_answering(self, event, sender, allowed_answering_id_list, answer_pattern):
        id = int(event.user_id)
        if id in allowed_answering_id_list:

            if datetime.now().time().hour in [13, 17, 18]:

                # получено сообщение
                self.add_log_message('RECIEVED', f"from {' '.join(sender)} : '{event.text}'")

                # прочитать сообщение
                self.session_api.messages.markAsRead(
                    peer_id=event.user_id)
                sleep_time = random.randint(3, 60)

                # статус online
                self.set_account_online()

                self.add_log_message("SLEEP", f"{sleep_time} sec")
                time.sleep(sleep_time)
                self.add_log_message('READED', f"from {' '.join(sender)} : '{event.text}'")

                # поставить статус пеатает
                self.session_api.messages.setActivity(
                    user_id=event.user_id,
                    type='typing')
                time.sleep(2)

                # отвечаем на сообщение с пересылкой
                answer = answer_pattern[random.randint(0, len(answer_pattern)-1)]
                self.reply_msg(id, event.message_id, answer)

    # основная функция
    def start(self):
        self.add_log_message("START", '')
        while self.flag_should_work:
            try:
                for event in self.long_poll.listen():   # Слушаем сервер
                    if event.type == VkEventType.MESSAGE_NEW:
                        # print(event)
                        if event.to_me and event.from_user and not event.from_me:

                            sender = self.get_page_info_by_id(event.user_id)

                            if self.role == 'deleter':
                                self.react_as_deleter(event, sender, not_allowed_id_list, delete_list) 

                            elif self.role == 'answering':
                                self.react_as_answering(event, sender, allowed_answering_id_list, answer_pattern)

            except KeyboardInterrupt:
                self.stop(message="""by KeyboardInterrupt
""")

            except Exception:
                # time.sleep(1)
                self.add_log_message('ERROR', f'timeout {Exception}')
                self.restart()


    # остановка сервера
    def stop(self, message=''):
        self.add_log_message("STOP", message, prefix="\n")
        self.flag_should_work = False

    # перезапуск сервера
    def restart(self):
        self.stop()
        self.add_log_message("RESTART", '')
        self.flag_should_work = True
        self.start()
