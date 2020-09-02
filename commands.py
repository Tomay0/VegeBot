# WORKING PROGRESS! Not in use yet and None of it has been tested

"""
How to use:

client = discord.Client()
cs = CommandSystem('vege ', client)

@cs.add_command('tick', 'Plays random Min tick')
def tick(message, args):
    pass

@cs.add_command('say', 'Will say out loud any text you give it', arguments=AnyText())
def say(message, args):
    pass

@cs.add_command(
    'colour me',
    'Will change the color of your discord name whatever you request',
    aliases=['colour', 'color me', 'colour me'],
    arguments=Or(ColorHex(), CSS3Name(), RGBValues())
)
def color(message, args):
    pass

client.run(token)
"""

import webcolors
import discord

class Command:
    def __init__(self, function, name, description, show_in_help=True, aliases=None, arguments=None):
        if aliases is None:
            aliases = []
        aliases.insert(0, name)  # first item is its primary name
        self.names = aliases

        if arguments is None:
            self.arguments = Nothing()
        else:
            self.arguments = arguments

        self.function = function
        self.description = description
        self.show_in_help = show_in_help


class CommandSystem:
    def __init__(self, prefix, client):
        self.prefix = prefix
        self.commands = []

        client.event(self.on_message)

        self.add_command('help', 'Shows you info about all the commands', show_in_help=False)(self._help_command)

    async def _help_command(self, message, args):
        embed = discord.Embed(
            title='Vegebot Help',
            description='This is a list of all the Vegebot commands.',
            color=discord.colour.Color.purple()
        )
        for command in self.commands:
            if command.show_in_help:
                embed.add_field(name='vege ' + command.names[0], value=command.description)
        await message.channel.send(embed=embed)

    def add_command(self, *args, **argv):
        def add(function):
            self.commands.append(Command(function, *args, **argv))
        return add

    async def on_message(self, message):
        # check it starts with the right prefix
        if not message.content.lower().startswith(self.prefix):
            return
        text = message.content[len(self.prefix):]

        # find the command that best matches
        command_to_run = None
        command_to_run_name = ''
        command_args_pass = False

        for command in self.commands:
            for name in command.names:
                if (text == name or text.startswith(name + ' ')) and len(name) > len(command_to_run_name):
                    passes = command.arguments.validate(text[len(name) + 1:])
                    if command_args_pass and not passes:
                        continue
                    command_to_run_name = name
                    command_to_run = command
                    command_args_pass = passes

        # if a command was found now check that it has the correct arguments
        if command_to_run is None:
            await message.channel.send('That is not a command')
        elif command_args_pass:
            await command_to_run.function(message, text[len(command_to_run_name) + 1:])
        else:
            error_message = 'That is not how this command should be used. Try: \n'
            for arg_example in command_to_run.arguments.get_example_usages():
                error_message += self.prefix + command_to_run_name + ' ' + arg_example + '\n'
            await message.channel.send(error_message)

# TODO: Make it so you can get feedback about why it did not validate


class Or:
    def __init__(self, *types):
        self.types = types

    def validate(self, args):
        for arg_type in self.types:
            if arg_type.validate(args):
                return True
        return False

    def get_example_usages(self):
        example_usages = []
        for arg_type in self.types:
            example_usages.extend(arg_type.get_example_usages())
        return example_usages


class All:
    def __init__(self, *types):
        self.types = types

    def validate(self, args):
        split_args = args.strip().replace(',', ' ').split()
        if len(split_args) != len(self.types):
            return False

        for i in range(len(split_args)):
            if not self.types[i].validate(split_args[i]):
                return False
        return True

    def get_example_usages(self):
        return All._combine_examples([arg_type.get_example_usages() for arg_type in self.types])

    @staticmethod
    def _combine_examples(x):
        if len(x) == 1:
            return x[0]
        examples = []
        for i in x[0]:
            examples += [i + ' ' + j for j in All._combine_examples(x[1:])]
        return examples


class AnyText:
    def validate(self, args):
        return len(args.strip()) > 0

    def get_example_usages(self):
        return ['weed wacker']


class ExactText:
    def __init__(self, text, case_sensitive=False):
        self.text = text if case_sensitive else text.lower()

    def validate(self, args):
        return self.text == args

    def get_example_usages(self):
        return [self.text]


class TextFromList:
    def __init__(self, texts, case_sensitive=False):
        self.texts = texts
        self.case_sensitive = case_sensitive

    def validate(self, args):
        if self.case_sensitive:
            return args.lower() in map(str.lower, self.texts)
        else:
            return args in self.texts

    def get_example_usages(self):
        return self.texts[:3]


class Nothing:
    def validate(self, args):
        return len(args.strip()) == 0

    def get_example_usages(self):
        return ['']


class Number:
    def __init__(self, decimals_allowed=True, ceiling=None, floor=None):
        self.decimals_allowed = decimals_allowed
        self.ceiling = ceiling
        self.floor = floor

    def validate(self, args):
        try:
            if self.decimals_allowed:
                num = int(args)
            else:
                num = float(args)
            return self.ceiling >= num >= self.floor
        except ValueError:
            return False

    def get_example_usages(self):
        return [str(self.ceiling)]


class ColorHex:
    def validate(self, args):
        return webcolors.HEX_COLOR_RE.match(args)

    def get_example_usages(self):
        return ['#ff0088']


class CSS3Name:
    def validate(self, args):
        return args.lower() in webcolors.CSS3_NAMES_TO_HEX

    def get_example_usages(self):
        return ['blue']


class RGBValues:
    validator = All(
        Number(decimals_allowed=False, floor=0, ceiling=255),
        Number(decimals_allowed=False, floor=0, ceiling=255),
        Number(decimals_allowed=False, floor=0, ceiling=255)
    )

    def validate(self, args):
        return self.validator.validate(args)

    def get_example_usages(self):
        return self.validator.get_example_usages()

