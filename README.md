# Running in Docker

Note you need to have a discord bot token in order for this to work.

Note that there are problems when running this through docker. These will be fixed at some stage...

```bash
docker build -t vegebot .
docker run -e DISCORD_TOKEN=YOUR_DISCORD_TOKEN vegebot
```

## Config

At the moment, you can alter Vegebot's greetings when people join voicechat. Vegebot will pick one of these greetings whenever someone joins voicechat.

You can alter the config.yml file to change these greetings. You can disable the greeting function by removing the option from the config all together.

# Commands

```
vege say                           When the bot is in a voice channel it will use text to speech to read your message aloud
vege come here                     Will make the bot join the voice channel you are in
vege go away                       Makes the bot leave the voice channel
vege colour me                     Colours your name the requested colour. You can give it hex, RGB values or the name of the colour you want
vege help                          Shows you a list of all the commands you can use and a description of how to use them
```
