import vk_api#.vk_api
from vk_api.longpoll import VkLongPoll
from datetime import datetime

class ServerVkPorperties():
    def __init__(self, api_token, server_name=""):
        

        # Для Long Poll
        self.vk_session = vk_api.VkApi(token=api_token) 

        # Для вызова методов vk_api session_api
        self.session_api = self.vk_session.get_api()

        # Для использования Long Poll API
        self.long_poll = VkLongPoll(self.vk_session)

        if server_name:
            self.server_name = server_name 
        else :
            self.server_name = self.get_base_account_info()


    # Получаем информацию о подключенном аккаунте
    def get_base_account_info(self, name_only=True):
        res = self.session_api.account.getProfileInfo()
        res = {'id':res['id'], 
                'first_name':res['first_name'],
                'last_name':res['last_name']}

        if name_only:
            return ' '.join([res['first_name'], res['last_name']])
        else:
            return res

    def get_page_info_by_id(self, id):
        res = self.session_api.users.get(user_ids=id)[0]
        # print(res['first_name'], res['last_name'])
        return res['first_name'], res['last_name']


    # Посылаем тестовое сообщение подключенному аккаунту
    def test(self): 
        self.send_msg(self.get_base_account_info(name_only=False)['id'], 
            f"Тестовое сообщение от бота {self.server_name}")


    # Отправляем сообщение по id пользователя
    def send_msg(self, user_id, message_text, random_id=0):
        message_id = self.session_api.messages.send(
            user_id=user_id, 
            message=message_text, 
            random_id=random_id)

        sender = self.get_page_info_by_id(user_id)
        self.print_log(
            category='SENDED', 
            from_user=self.get_base_account_info(), 
            to_user=f"{' '.join(sender)}", 
            message=f"{message_text}")
        
        return message_id


    # удаляем сообщение по id
    def delete_message(self, message_id, spam=0, delete_for_all=0):
        arr = self.get_message_by_id(message_id)

        sender = self.get_page_info_by_id(arr[0])

        delete_result = self.session_api.messages.delete(
            message_ids=message_id, 
            spam=spam, 
            delete_for_all=delete_for_all)

        self.print_log(category="DELETED", from_user=f"{' '.join(sender)}", to_user=self.get_base_account_info(), message=f"{arr[1]}") 

        return delete_result # 1, 0


    def print_log(self, category, message='', from_user='', to_user='', prefix=''):

        dt_str = " {:<4}-{:>2}-{:>2} {:>2}:{:>2}:{:>2} ".format(*list(datetime.now().timetuple()))
        
        from_user_str = f"from : {from_user} " if from_user else from_user
        to_user_str = f"to : {to_user} " if to_user else to_user
        message_str = f"message : '{message}' " if message else message

        res = prefix + \
            f" {self.server_name} " + \
            dt_str + "{:<10}".format(category) + \
            from_user_str + to_user_str + \
            message_str

        print(res)

        return dt_str


    def set_account_online(self):
        self.session_api.account.setOnline()
        self.print_log(category="SET-ONLINE")


    # отправляем текст сообщения по id 
    def get_message_by_id(self, message_id):
        message = self.session_api.messages.getById(
            message_ids=message_id, 
            preview_length=1, 
            extend=0)

        return message['items'][0]['from_id'], message['items'][0]['text']


    def reply_msg(self, user_id, forward_message_id, message_text, random_id=0):
        message_id = self.session_api.messages.send(
            user_id=user_id,
            reply_to=forward_message_id,
            message=message_text,
            random_id=random_id)

        sender = self.get_page_info_by_id(user_id)
        self.print_log(
            category='FORWARDED', 
            from_user=self.get_base_account_info(), 
            to_user=f"{' '.join(sender)}", 
            message=f"{message_text}")
        
        return message_id


    def get_dialog_history(self, offset, count, user_id):
        return self.session_api.messages.getHistory(
            count=count,
            offset=offset,
            user_id=user_id)
