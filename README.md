# How to run

Make sure ffmpeg, python and pip are installed.

Use python version 3.6 (not later).

It is recommended you run this on linux because of the tflearn library which is not officially supported on windows.

Then open the terminal at the project root folder and do the following:

```bash
sudo pip install virtualenv
virtualenv vegebot
source vegebot/bin/activate
pip install discord gtts pynacl webcolors tflearn tensorflow==1.14 tweepy asgiref
python vegebot.py
```

You also require some additional files in order to get the bot to run. Some are optional though.

## Additional files

There are additional files that are required in order to run the bot.

#### Required:

**token.txt** put the discord bot token in here.

**channel-name.txt** put the name of the channel you want the bot to mainly post to here.

#### Twitter integration

**twitter_tokens.txt** includes 4 tokens, one per line. In this order: API key, API secret key, Access key, access secret key.

**following.txt** a list of all twitter users (by their ID) to follow and post tweets from into your discord server. 1 per line.

#### Greetings

**greetings.txt** if Vegebot is in a voice call, they will say greetings to people as they join. A greeting is randomly selected from this file. One greeting per line. Use {name} within the file to insert the display name of the user.

# Imitation

This bot includes a feature where you can train a neural network to talk like a particular person. This requires a lot of setup, which includes training a neural network for multiple hours.

## Training

First you need to obtain data of the person you want to imitate. The data should be contained within a text file under `imitate/{name}/data_unicode.txt`. 
Note that the output you are imitating only includes alphabetical characters and whitespace (no symbols or numbers). \
This file is allowed these banned characters, however, note that they will be removed in the generated `data.txt` file that will be generated.

To train a bot: run the python script "train.py". Enter the name of the person you want to train. This should be the same as the directory under `imitate/`.
Then you must enter how many generations you want to train for. This depends on how accurate you want your bot to be and how long the data is. To get a really good imitation you will have to train for several hours.
The time it takes for each generation depends on how complex the data is. The model is saved after each generation so you can reload it later without losing progress.

When your bot is running, users can type `vege imitate {name}` to generate some output from that person.


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
vege imitate                       Imitate a particular user on the channel.
```
