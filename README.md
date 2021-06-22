# Adding vegebot to your server
Hosting vegebot isn't free. Because of this, it's not a public bot. However, you can run your own version if you want

# Running in Docker from Docker Hub
This is the easiest way to run your own version of vege.
You will need Docker and a discord bot token.

```bash
docker pull isaacirvine/vegebot
docker run -e DISCORD_TOKEN=<your token> isaacirvine/vegebot
```

Currently, no supported way to add custom greetings. In the future this should be doable through docker volumes or in the bot itself on a per discord server basis

# Running in Docker from source
You will need Docker and a discord bot token.
1. pull for git
2. open terminal in the root directory of this project
3. run the following

```bash
docker build -t vegebot .
docker run -e DISCORD_TOKEN=<your token> vegebot
```
If you want to use Docker Compose, there is an example file available.

# Running without Docker from source
This should probably be possible but is not supported.
Make sure ffmpeg, python and pip are installed.
Then run the following:
'''bash
pip install -r requirements.txt
python vegebot.py
'''

## Config
NOTE: For now this can only be done if you are running from source

At the moment, you can alter Vegebot's greetings when people join voice chat. Vegebot will pick one of these greetings whenever someone joins voice chat.

You can alter the config.yml file to change these greetings. You can disable the greeting function by removing the option from the config all together.

# Commands

```
vege say                           When the bot is in a voice channel it will use text to speech to read your message aloud
vege come here                     Will make the bot join the voice channel you are in
vege go away                       Makes the bot leave the voice channel
vege colour me                     Colours your name the requested colour. You can give it hex, RGB values or the name of the colour you want
vege help                          Shows you a list of all the commands you can use and a description of how to use them
```
