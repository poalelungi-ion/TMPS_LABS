# Importing all needed libraries.
import sqlite3
from sqlite3 import Error

class DBNoAccessError(Exception):
    pass

# The DataBaseManager service interface.
class DataBaseInterface:
    def get_username(self, user_id, platform):
        pass

    def get_message_query(self, user_id, platform):
        pass

    def insert_message(self, chat_id, user_msg, classification, response, user_id, platform):
        pass

    def insert_user(self, user_id, user_name, platform):
        pass

    def close(self):
        pass

    def open_access(self):
        pass

    def close_access(self):
        pass

# The Data Base Manager class.
class DataBaseManager:
    def __init__(self, db_path : str) -> None:
        '''
            The Data Base Manager constructor.
        :param db_path: str
            The path to the data base.
        '''
        # Trying to connect to data base.
        try:
            self.conn = sqlite3.connect(db_path)
        except Error as e:
            print(e)

        # Creating the cursor.
        self.c = self.conn.cursor()

        # The messages table creation query.
        self.messages_table_creation_query = '''CREATE TABLE IF NOT EXISTS messages(
                                                id integer PRIMARY KEY,
                                                chat_id integer NOT NULL,
                                                context text NOT NULL,
                                                classification text NOT NULL,
                                                response text NOT NULL,
                                                user_id integer NOT NULL,
                                                platform text NOT NULL,
                                                FOREIGN KEY (user_id) REFERENCES users (user_id)
                                                );'''

        # The user table creation query.
        self.user_table_creation_query = '''CREATE TABLE IF NOT EXISTS users(
                                            id integer PRIMARY KEY,
                                            user_id integer NOT NULL,
                                            user_name text NOT NULL,
                                            platform text NOT NULL
                                            );'''

        # The message insert query.
        self.message_insert_query = '''INSERT INTO messages (chat_id,
                                                            context,
                                                            classification,
                                                            response,
                                                            user_id,
                                                            platform)
                                        VALUES (?,?,?,?,?,?)
                                    '''

        # The message insert query.
        self.message_insert_query = '''INSERT INTO messages (chat_id,
                                                            context,
                                                            classification,
                                                            response,
                                                            user_id,
                                                            platform)
                                        VALUES (?,?,?,?,?,?)
                                        '''
        # The user insert query.
        self.user_insert_query = '''INSERT INTO users (user_id,
                                                       user_name,
                                                       platform)
                                    VALUES (?,?,?)
                                 '''

        # The query for getting the user name.
        self.select_user_query = '''SELECT user_name FROM users
                                    WHERE user_id=? AND platform=?'''

        # The query for the the classification of the certain message.
        self.select_message_query = '''SELECT classification FROM users
                                       WHERE user_id=? AND platform=?'''

        # Creating the user and messages tables.
        self.c.execute(self.messages_table_creation_query)
        self.c.execute(self.user_table_creation_query)

    def get_username(self, user_id, platform):
        return self.c.execute(self.select_user_query, (user_id,platform)).fetchone()

    def get_message_query(self, user_id, platform):
        return self.c.execute(self.select_message_query, (user_id,platform)).fetchall()

    def insert_message(self, chat_id, user_msg, classification, response, user_id, platform):
        self.c.execute(self.message_insert_query,
                       (chat_id, user_msg, classification, response, user_id, platform))
        self.conn.commit()

    def insert_user(self, user_id, user_name, platform):
        self.c.execute(self.user_insert_query, (user_id, user_name,platform))
        self.conn.commit()

    def close(self):
        self.c.close()
        self.conn.close()

# The Data Base Manager Proxy.
class DataBaseProxy(DataBaseInterface):
    def __init__(self, service):
        self.service = service
        self.access = True

    def get_username(self, user_id, platform):
        if self.access:
            return self.service.get_username(user_id, platform)
        else:
            raise DBNoAccessError("Access isn't granted to the Data Base!")

    def get_message_query(self, user_id, platform):
        if self.access:
            return self.service.get_message_query(user_id, platform)
        else:
            raise DBNoAccessError("Access isn't granted to the Data Base!")

    def insert_message(self, chat_id, user_msg, classification, response, user_id, platform):
        if self.access:
            self.service.insert_message(chat_id, user_msg, classification, response, user_id, platform)
        else:
            raise DBNoAccessError("Access isn't granted to the Data Base!")

    def insert_user(self, user_id, user_name, platform):
        if self.access:
            self.service.insert_user(user_id, user_name, platform)
        else:
            raise DBNoAccessError("Access isn't granted to the Data Base!")

    def close(self):
        if self.access:
            self.service.close()
        else:
            raise DBNoAccessError("Access isn't granted to the Data Base!")

    def open_access(self):
        self.access = True

    def close_access(self):
        self.access = False