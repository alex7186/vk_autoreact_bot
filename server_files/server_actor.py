from server_files.server_vk_db_properties import ServerVkDbProperties
from vk_api.longpoll import VkEventType
import time


# запрещенные сообщения
delete_list = ['Ага', 'ага', '👺', '😈', '👿', '😡', '🌚', '🌝', '👽']
answer_pattern = ['Лол', 'лол', 'Ахах', 'Ахахах', 'Ахахахах', 'Ахахахахах']

# запрещено присылать сообщения выше
allowed_id_list = [] 
allowed_answering_id_list = [470915582, 249274091]



class ServerActor(ServerVkDbProperties):
    def __init__(self, api_token, role, server_name="",  db_connection=None):
        super().__init__(api_token, server_name, db_connection)

        self.reacted = False
        self.flag_should_work = True

        roles = ['answerer', 'deleter', 'reader']
        if role not in roles:
            raise ValueError("Role must be " + str(roles))

        self.role = role

        if self.role == 'answerer':
            import random

        self.review()

    def review(self):
        if self.role == 'answerer':
            res = f"answering pattern           : {answer_pattern} \n    allowed answering id list   : {[self.get_page_info_by_id(el) for el in allowed_answering_id_list]}"
        elif self.role == 'deleter':
            res = f"messages to delete          : {delete_list}    \n    allowed sending   id list   : {[]}" # self.get_page_info_by_id(el) for el in allowed_id_list
        elif self.role == 'reader':
            res = ''

        print(f"""
    account of                  : {self.get_base_account_info()}
    server name                 : {self.server_name}
    server role                 : {self.role}
    """ + res + '\n')


    def react_as_deleter(self, event, sender, allowed_id_list, delete_list):
        # сообщения этих людей фильтруются
        id = int(event.user_id)
        if id not in allowed_id_list:
            # удаляем стикеры
            if (len(event.attachments) > 0) and ('attach1_type' in list(event.attachments.keys())) and (event.attachments['attach1_type'] == 'sticker'):
                # message_id = self.send_msg(id, "Сообщение со стикером было автоматически удалено по желанию пользователя" )
                
                self.print_log(category='RECIEVED', from_user=f"{' '.join(sender)}", to_user=self.get_base_account_info(), message=f"sticker '{event.attachments['attach1']}'") 

            # обрабатываем сообщения
            else:
                self.print_log(category='RECIEVED', from_user=f"{' '.join(sender)}", to_user=self.get_base_account_info(), message=f"{event.text}")
                if event.text in delete_list :

                    
                    # сообщение об удалениии
                    message_id = self.reply_msg(id, event.message_id, "Автоматически удалено для пользователя" )

                    # удаление сообщения об удалении
                    self.delete_message(message_id)
                    # удаление сообщения
                    self.delete_message(event.message_id)
                    return True
        return False


    def react_as_reader(self, event, sender):
        if (len(event.attachments) > 0) and ('attach1_type' in list(event.attachments.keys())) and (event.attachments['attach1_type'] == 'sticker'):
            self.print_log(category='RECIEVED', from_user=f"{' '.join(sender)}", to_user=self.get_base_account_info(), message=f"sticker '{event.attachments['attach1']}'") 
        else:
            self.print_log(category='RECIEVED', from_user=f"{' '.join(sender)}", to_user=self.get_base_account_info(), message=f"{event.text}")

        return True


    def react_as_answering(self, event, sender, allowed_answering_id_list, answer_pattern):
        id = int(event.user_id)
        if id in allowed_answering_id_list:

            if datetime.now().time().hour in [13, 17, 18]:

                # получено сообщение
                self.print_log(category='RECIEVED', from_user=f"{' '.join(sender)}", to_user=self.get_base_account_info(), message=f"{event.text}")

                # прочитать сообщение
                self.session_api.messages.markAsRead(
                    peer_id=event.user_id)
                sleep_time = random.randint(3, 60)

                # статус online
                self.set_account_online()

                self.print_log(category="SLEEP", message=f"{sleep_time} sec")
                time.sleep(sleep_time)
                self.print_log(category='READED', from_user=f"{' '.join(sender)}", to_user=self.get_base_account_info(), message=f"{event.text}'")

                # поставить статус пеатает
                self.session_api.messages.setActivity(
                    user_id=event.user_id,
                    type='typing')
                time.sleep(2)

                # отвечаем на сообщение с пересылкой
                answer = answer_pattern[random.randint(0, len(answer_pattern)-1)]
                self.reply_msg(id, event.message_id, answer)

                return True
        return False

    def start(self):
        self.print_log(category="STARTED")
        while self.flag_should_work:
            try:
                for event in self.long_poll.listen():   # Слушаем сервер
                    # print('111')
                    if event.type == VkEventType.MESSAGE_NEW:
                        # print(event)
                        if event.to_me and event.from_user :

                            sender = self.get_page_info_by_id(event.user_id)

                            if self.role == 'deleter':
                                self.reacted = self.react_as_deleter(event, sender, allowed_id_list, delete_list) 

                            elif self.role == 'answering':
                                self.reacted = self.react_as_answering(event, sender, allowed_answering_id_list, answer_pattern)  

                            elif self.role == 'reader':
                                self.reacted = self.react_as_reader(event, sender)                      


                        elif event.from_me and not self.reacted:
                            sender = self.get_page_info_by_id(event.user_id)
                            if (len(event.attachments) > 0) and ('attach1_type' in list(event.attachments.keys())) and (event.attachments['attach1_type'] == 'sticker'):
                                # message_id = self.send_msg(id, "Сообщение со стикером было автоматически удалено по желанию пользователя" )
                                
                                self.print_log(category='SENDED', from_user=self.get_base_account_info(), to_user=f"{' '.join(sender)}", message=f"sticker '{event.attachments['attach1']}'") 
                                
                            else:
                                self.print_log(category='SENDED', from_user=self.get_base_account_info(), to_user=f"{' '.join(sender)}", message=f'{event.text}')


            except KeyboardInterrupt:
                self.stop(message="""by KeyboardInterrupt""")
                self.db_cursor.close()
                self.db_connection.close()
                

            except Exception:
                time.sleep(1)
                self.print_log(category='ERROR', message=f'timeout {Exception}')
                self.restart()

    
    # остановка сервера
    def stop(self, message=''):
        self.print_log(category="STOP", message=message, prefix="\n")
        self.flag_should_work = False


    # перезапуск сервера
    def restart(self):
        self.stop()
        self.print_log(category="RESTART")
        self.flag_should_work = True
        self.make_db_connection(self.db_connection)
        self.start()
