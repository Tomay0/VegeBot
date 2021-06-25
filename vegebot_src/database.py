import requests
import json
import logging
import setup_database

setup_database.setup()


def clean_message(message):
    return message.replace('\u0000', ' ')


class PostgRESTDatabase:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def get_data(self, query):
        headers = {'Authorization': f'Bearer {self.token}'}

        response = requests.get(f'{self.url}/{query}', headers=headers)

        return json.loads(response.text)

    def clear_database(self):
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}

        response = requests.delete(f'{self.url}/discordmessages', headers=headers, json={})

        if response.status_code != 204:
            logging.error(f"Error {response.status_code} deleting messages:\n{response.text}")

        response = requests.delete(f'{self.url}/discordchannels', headers=headers, json={})

        if response.status_code != 204:
            logging.error(f"Error {response.status_code} deleting channels:\n{response.text}")

        response = requests.delete(f'{self.url}/discordguilds', headers=headers, json={})

        if response.status_code != 204:
            logging.error(f"Error {response.status_code} deleting guilds:\n{response.text}")

        response = requests.delete(f'{self.url}/discordusers', headers=headers, json={})

        if response.status_code != 204:
            logging.error(f"Error {response.status_code} deleting users:\n{response.text}")

    def add_messages(self, messages):
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json',
                   'Prefer': 'params=multiple-objects'}

        content = [{'g_id': message.guild.id, 'g_name': message.guild.name, 'c_id': message.channel.id,
                    'c_name': message.channel.name, 'u_id': message.author.id, 'u_name': message.author.name,
                    'msg_id': message.id, 'msg': clean_message(message.content),
                    'msg_timestamp': message.created_at.strftime("%Y-%m-%d %H:%M:%S")} for message in messages]

        response = requests.post(f'{self.url}/rpc/add_message', headers=headers, json=content)

        if response.status_code != 200:
            logging.error(f"Error {response.status_code} adding messages:\n{response.text}")

    def add_message(self, message):
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}

        content = {'g_id': message.guild.id, 'g_name': message.guild.name, 'c_id': message.channel.id,
                   'c_name': message.channel.name, 'u_id': message.author.id, 'u_name': message.author.name,
                   'msg_id': int(message.id), 'msg': clean_message(message.content),
                   'msg_timestamp': message.created_at.strftime("%Y-%m-%d %H:%M:%S")}

        response = requests.post(f'{self.url}/rpc/add_message', headers=headers, json=content)

        if response.status_code != 200:
            logging.error(f"Error {response.status_code} adding message:\n{response.text}")

    def delete_message(self, message):
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}

        response = requests.delete(f'{self.url}/discordmessages?message_id=eq.{message.id}', headers=headers, json={})

        if response.status_code != 204:
            logging.error(f"Error {response.status_code} deleting message:\n{response.text}")
