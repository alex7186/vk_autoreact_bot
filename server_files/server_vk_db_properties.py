from server_files.server_vk_properties import ServerVkPorperties

class ServerVkDbProperties(ServerVkPorperties):
    def __init__(self, api_token, server_name="", db_connection=None):

        super().__init__(api_token, server_name)

        self.make_db_connection(db_connection)


    def make_db_connection(self, db_connection):
        self.db_connection = db_connection
        self.db_cursor = self.db_connection.cursor()


    def print_log(self, category, message='', from_user='', to_user='', prefix=''):

        dt_str = super().print_log(category, message, from_user, to_user, prefix)

        db_command = f""" INSERT INTO logs
            VALUES
            (
                "{str(self.server_name)}", 
                "{str(dt_str)}", 
                "{str(category)}", 
                "{str(to_user)}", 
                "{str(from_user)}", 
                "{str(message)}"
            );"""

        try:
            self.db_cursor.execute(db_command)
            self.db_connection.commit()
        except Exception:
            print (prefix + f"{self.server_name} " + dt_str + "{:<10}".format("NOT COMMITED"))
