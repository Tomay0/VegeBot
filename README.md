# How to run

Make sure ffmpeg, espeak, python and pip are installed.

Add your discord token into project root folder. Call it ```token.txt```

Then open the terminal at the project root folder and do the following:

```bash
sudo pip install virtualenv
virtualenv vegebot
source vegebot/bin/activate
pip install discord pyttsx3 pynacl
python vegebot.py
```



# Command

``` vege come here``` will make Vege Bot join the voice channel you are currently in

``` vege go away``` will make Vege Bot leave the voice channel its currently in

``` vege say <message>``` will say the message you give it out loud in the voice chat that it is currently in.

``` vege edit history``` will tell you every message that's been edited in the last 15 minutes in the text channel that you are in.

``` vege delete history``` will tell you every message that's been deleted in the last 15 minutes in the text channel that you are in.
