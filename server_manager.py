# Импорт класса Server
from server import Server
# Получение config.py
import config

from multiprocessing import Process

server1 = Server(api_token=config.vk_api_token1, server_name="server1", role='answering')
server2 = Server(api_token=config.vk_api_token2, server_name="server2", role='deleter')
# vk_api_token - API токен, который мы ранее создали
# 197901530 - id сообщества-бота
# "server1" - имя сервера
# role - функционал сервера


bot1 = Process(target=server1.start)
bot2 = Process(target=server2.start)

bot1.start()
bot2.start()
bot1.join()
bot2.join()
