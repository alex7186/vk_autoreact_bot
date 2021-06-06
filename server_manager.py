# -*- coding: utf-8 -*-

# Импорт класса Server
from server_files.server_actor import ServerActor
# Получение config.py
import config

from db_manager import connect
# from multiprocessing import Process

connection = connect() # db_manager.



server2 = ServerActor(
                api_token=config.vk_api_token, 
                server_name="my_server", 
                role='reader', # 'reader'
                db_connection=connection
                )

# vk_api_token - API токен, который мы ранее создали
# 197901530 - id сообщества-бота
# "server1" - имя сервера
# role - функционал сервера


# bot1 = Process(target=server1.start)
# bot1.start()
# bot1.join()


server2.start()
