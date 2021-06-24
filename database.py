import requests
import json


def clean_message(message):
    return message.replace('\u0000', ' ')


class PostgRESTDatabase:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def add_user(self, user_id, user_name):
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}

        # Check if it exists
        content = {'user_id': user_id}

        response = requests.get(f'{self.url}/discordusers', headers=headers, json=content)

        if response.status_code != 200:
            print(f"Error {response.status_code} adding user:\n{response.text}")
            return

        json_response = json.loads(response.text)

        print(json_response)

        if len(json_response) == 0:
            content = {'user_id': user_id, 'user_name': user_name}
            # Add new entry
            response = requests.post(f'{self.url}/discordusers', headers=headers, json=content)

            # TODO remove these test prints
            if response.status_code != 201:
                print(f"Error {response.status_code} adding user:\n{response.text}")
            else:
                print(f"Added user: {user_name}")
        elif json_response[0]['user_name'] != user_name:
            content = {'user_name': user_name}

            response = requests.patch(f'{self.url}/discordusers?user_id=eq.{user_id}', headers=headers, json=content)

            # TODO remove these test prints
            if response.status_code != 201:
                print(f"Error {response.status_code} updating user:\n{response.text}")
            else:
                print(f"Added user: {user_name}")
        else:
            print("Already added")

    def get_messages(self):
        headers = {'Authorization': f'Bearer {self.token}'}

        response = requests.get(f'{self.url}/discordmessages', headers=headers)

        return json.loads(response.text)

    def clear_database(self):
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}

        response = requests.delete(f'{self.url}/discordchannels', headers=headers, json={})
        response = requests.delete(f'{self.url}/discordguilds', headers=headers, json={})
        response = requests.delete(f'{self.url}/discordusers', headers=headers, json={})
        response = requests.delete(f'{self.url}/discordmessages', headers=headers, json={})

    def add_messages(self, messages):
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json',
                   'Prefer': 'params=multiple-objects'}

        content = [{'g_id': message.guild.id, 'g_name': message.guild.name, 'c_id': message.channel.id,
                    'c_name': message.channel.name, 'u_id': message.author.id, 'u_name': message.author.name,
                    'msg_id': int(message.id), 'msg': clean_message(message.content),
                    'msg_timestamp': message.created_at.strftime("%Y-%m-%d %H:%M:%S")} for message in messages]

        response = requests.post(f'{self.url}/rpc/add_message', headers=headers, json=content)

        if response.status_code != 200:
            print(f"Error {response.status_code} adding message:\n{response.text}")
        else:
            print("Successful post")
