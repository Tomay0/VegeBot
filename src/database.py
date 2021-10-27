import requests
import json
import logging
import psycopg2
from os import getenv
from time import sleep


def wait_for_postgrest(num_tries=20):
    n = 0
    while True:
        try:
            return requests.head(getenv('POSTGREST_URL'))
        except requests.exceptions.ConnectionError:
            sleep(1)
            n += 1
            if n >= num_tries:
                raise RuntimeError("Could not connect to PostgREST")


async def reset_database(client, database):
    if database is None:
        logging.warning('Database config is not set, so could not be loaded')
        return

    wait_for_postgrest()
    database.clear_database()

    all_messages = []
    for guild in client.guilds:
        for channel in guild.text_channels:
            perms = channel.permissions_for(guild.me)
            if perms.read_messages:

                async for m in channel.history(limit=None):
                    all_messages.append(m)

    database.add_messages(all_messages)

    logging.info("Database Reset")

    return database


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

        response = requests.delete(f'{self.url}/messages', headers=headers, json={})

        if response.status_code != 204:
            logging.error(f"Error {response.status_code} deleting messages:\n{response.text}")

        response = requests.delete(f'{self.url}/channels', headers=headers, json={})

        if response.status_code != 204:
            logging.error(f"Error {response.status_code} deleting channels:\n{response.text}")

        response = requests.delete(f'{self.url}/guilds', headers=headers, json={})

        if response.status_code != 204:
            logging.error(f"Error {response.status_code} deleting guilds:\n{response.text}")

        response = requests.delete(f'{self.url}/users', headers=headers, json={})

        if response.status_code != 204:
            logging.error(f"Error {response.status_code} deleting users:\n{response.text}")

    def add_messages(self, messages):
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json',
                   'Prefer': 'params=multiple-objects'}

        content = [{'g_id': str(message.guild.id), 'g_name': message.guild.name, 'c_id': str(message.channel.id),
                    'c_name': message.channel.name, 'u_id': str(message.author.id), 'u_name': message.author.name,
                    'msg_id': str(message.id), 'msg': clean_message(message.content),
                    'msg_timestamp': message.created_at.strftime("%Y-%m-%d %H:%M:%S")} for message in messages]

        response = requests.post(f'{self.url}/rpc/add_message', headers=headers, json=content)

        if response.status_code != 200:
            logging.error(f"Error {response.status_code} adding messages:\n{response.text}")

    def add_message(self, message):
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}

        content = {'g_id': str(message.guild.id), 'g_name': message.guild.name, 'c_id': str(message.channel.id),
                   'c_name': message.channel.name, 'u_id': str(message.author.id), 'u_name': message.author.name,
                   'msg_id': str(message.id), 'msg': clean_message(message.content),
                   'msg_timestamp': message.created_at.strftime("%Y-%m-%d %H:%M:%S")}

        response = requests.post(f'{self.url}/rpc/add_message', headers=headers, json=content)

        if response.status_code != 200:
            logging.error(f"Error {response.status_code} adding message:\n{response.text}")

    def delete_message(self, message):
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}

        response = requests.delete(f'{self.url}/messages?id=eq.{message.id}', headers=headers, json={})

        if response.status_code != 204:
            logging.error(f"Error {response.status_code} deleting message:\n{response.text}")