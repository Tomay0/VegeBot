import requests
import json


class PostgRESTDatabase:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def add_channel(self, channel_id, channel_name):
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        content = {'channel_id': channel_id, 'channel_name': channel_name}

        response = requests.post(f'{self.url}/discordchannels', headers=headers, json=content)

        # TODO remove these test prints
        if response.status_code != 201:
            print(f"Error {response.status_code} adding channel:\n{response.text}")
        else:
            print(f"Added channel: {channel_name}")

    def add_guild(self, guild_id, guild_name):
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        content = {'guild_id': guild_id, 'guild_name': guild_name}

        response = requests.post(f'{self.url}/discordguilds', headers=headers, json=content)

        # TODO remove these test prints
        if response.status_code != 201:
            print(f"Error {response.status_code} adding guild:\n{response.text}")
        else:
            print(f"Added guild: {guild_name}")

    def add_user(self, user_id, user_name):
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        content = {'user_id': user_id, 'user_name': user_name}

        response = requests.post(f'{self.url}/discordusers', headers=headers, json=content)

        # TODO remove these test prints
        if response.status_code != 201:
            print(f"Error {response.status_code} adding user:\n{response.text}")
        else:
            print(f"Added user: {user_name}")

    def get_messages(self):
        headers = {'Authorization': f'Bearer {self.token}'}

        response = requests.get(f'{self.url}/discordmessages', headers=headers)

        return json.loads(response.text)

    def add_message(self, message):
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}

        content = {'message_id': message.id, 'guild_id': message.guild.id, 'channel_id': message.channel.id,
                   'user_id': message.user.id, 'message': message.content, 'message_timestamp': message.created_at}

        response = requests.post(f'{self.url}/discordmessages', headers=headers, json=content)

        # TODO remove these test prints
        if response.status_code != 201:
            print(f"Error {response.status_code} adding message:\n{response.content}")
        else:
            print(f"Added message: {message.content}")
