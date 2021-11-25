# Importing all needed libraries.
import json
import requests
from slackclient import SlackClient

# Defining the Interface of the Factories.
class InterfaceFactory:
    def create_interface(self, token):
        pass

# Definition of the Telegram Interface Factory.
class TelegramFactory(InterfaceFactory):
    def create_interface(self, token):
        return TelegramInterface(token)

# Definition of the Slack Interface Factory.
class SlackFactory(InterfaceFactory):
    def create_interface(self, token):
        return SlackInterface(token)

# Definition of the Communication Interface.
class CommunicationInterface:
    def recv(self, offset):
        pass

    def send(self, text, chat_id):
        pass

# Definition of the Telegram Interface.
class TelegramInterface(CommunicationInterface):
    def __init__(self, token):
        self.token = token
        self.url = f"https://api.telegram.org/bot{self.token}"

    def recv(self, offset = None):
        url = self.url + "/getUpdates?timeout=100"
        if offset:
            url = url + f"&offset={offset + 1}"
        url_info = requests.get(url)
        data = json.loads(url_info.content)['result']
        messages = []
        if data:
            for item in data:
                offset = item['update_id']
                try:
                    message = item["message"]["text"]
                except:
                    message = None
                if message:
                    messages.append(
                        {
                            "text" : message,
                            "user_id" : item['message']['from']['id'],
                            "chat_id" : item['message']['chat']['id'],
                            "username" : item['message']['from']['last_name'] if 'last_name' in item['message']['from'] else item['message']['from']['first_name'],
                            "platform" : "telegram"
                        }
                    )
        return messages, offset

    def send(self, text, chat_id):
        url = self.url + f'/sendMessage?chat_id={chat_id}&text={text}'
        if text is not None:
            requests.get(url)

# Defining the Slack Interface class.
class SlackInterface(CommunicationInterface):
    def __init__(self, token):
        self.token = token
        self.slack_client = SlackClient(self.token)

    def recv(self, offset = None):
        events = self.slack_client.rtm_read()
        messages = []
        for event in events:
            if event['type'] == "message" and "subtype" not in event:
                messages.append(
                    {
                        "text" : event["text"],
                        "chat_id" : event["channel"],
                        "user_id" : event["user"],
                        "username" : str(event["user"]),
                        "platform" : 'slack'
                    }
                )
        return messages, offset

    def send(self, text, chat_id):
        self.slack_client.api_call(
            "chat.postMessage",
            channel = chat_id,
            text=text
        )
