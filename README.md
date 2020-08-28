# How to run

Make sure ffmpeg, python and pip are installed.

Use python version 3.6 (not later)

Add your discord bot's token into project root folder. Call it ```token.txt```

Then open the terminal at the project root folder and do the following:

```bash
sudo pip install virtualenv
virtualenv vegebot
source vegebot/bin/activate
pip install discord gtts pynacl webcolors tflearn tensorflow==1.14 
python vegebot.py
```



# Command

```
vege say                           When the bot is in a voice channel it will use text to speech to read your message aloud
vege come here                     Will make the bot join the voice channel you are in
vege go away                       Makes the bot leave the voice channel
vege delete history                Shows all the messages that have been deleted in this channel in the last 15 minutes
vege edit history                  Shows all the messages that have been edited in this channel in the last 15 minutes
vege colour me                     Colours your name the requested colour. You can give it hex, RGB values or the name of the colour you want
vege tick                          Plays a random Min tick
vege help                          Shows you a list of all the commands you can use and a description of how to use them
```
