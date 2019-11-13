# fishyboteso
Auto fishing bot for Elder Scrolls Online. The Bot automatically fishes until the fishing hole disappears.  It can also send a notification to the users phone with the statistics of that fishing hole.

Don't forget to star this repository if you really liked it :)

### Demo Video
<div align="center">
  <a href="https://www.youtube.com/watch?v=E4Y9BFhCICI"><img src="https://img.youtube.com/vi/E4Y9BFhCICI/0.jpg" alt="IMAGE ALT TEXT"></a>
</div>

### Technology Stack
- Python
- cv2 
- docopt 
- numpy 
- pyautogui

### How to configure
Project Requirements:
- Download/Clone the project.
- Copy Provision's Chalutier folder into `Documents\Elder Scrolls Online\live\AddOns`.
- Install [Python v3.7.3](https://www.python.org/downloads/release/python-373/) (make sure you tick, `Add Python to PATH`).
- Run `install_modules.bat` file.

Executing the Bot:
- Start the game.
- Run `run_fishybot.bat` file.
- Optional: To add additional parameters, you will need to run the bot using powershell, to do so open powershell then use `cd <project-dir>` command, eg. `cd C:\fishyboteso-master`. Then type `python fishy.py` followed by the parameters you wish to use.

Starting fishing:
- Press `f9` to start the bot.
- Look at a fishing hole, bot will automatically start fishing.
- After the fishing is done, just move to next hole and look at it, fishing will start automatically.
- **IMPORTANT**: Keep the window focus on the game, even when controlling the bot.

Tip:  
To increase the check rate of the bot, try changing `--check-frequency` option to less than 1, like
`python fishy.py --check-frequency 0.5`  

### For Phone Notifications (Only Android)
- Install `notificationApp.apk` from the project files in your phone.
- Go to the app settings of the fishy app and allow all the notification permissions if you want the floating notification with sound.
- Make sure your PC and your phone are on the same network.
- Open the app and press the start service button.
- Type `python fishy.py --ip <local-ip>` where local-ip is the ip you see in the App.
- You can minimize the app but **don't close it** as the service will stop.

### FAQs
Will I get baned using this bot?

> Botting does violate ESO's terms of service, so technically you could get banned. But this bot doesn't read or write memory from ESO so they won't know you are using a bot. **This software doesn't come with any Liability or Warranty, I am not responsible if you do get banned.**

How much automation does this bot provide?

> It's not a fully automated bot, it does fishing on its own but you will have to move from one hole to another manually (although I was developing a fully automated bot, I didn't get a positive feedback from the community so I discontinued it)

Why am I getting this `pip : The term 'pip' is not recognized as the name of a cmdlet, function, script file, or operable program.`?

> Python and Pip are not in path variables, follow [this guide](https://www.youtube.com/watch?v=UTUlp6L2zkw) to add it.

I'm hitting the `F9` key but nothing is happening

> - Certain keyboards have the F9 key assigned to another function.  Try remapping your F9 key to its intended function.
> - Windows messing up with input. Try running powershell/cmd as admin. Then use `cd <directory-of-fishybot>` to get into the fishybot project folder. eg, `cd C:\fishyboteso-master\`.

The bot says `look at a fishing hole before starting` but I am looking at a fishing hole

> The bot isn't able to detect the graphic/color created by `Provision's Chalutier : Fishing Mod`, this could be because,
> - Addon is not properly configured 
>   - Make sure you have copied the addon folder to `Elder Scrolls Online\live\AddOns` directory and turn on "Allow out of date addons" in ESO
> - Something is overlapping or bot can't find it 
>   - Make sure that the addon is aligned on top-left in the game.
>   - Move the emoji by pressing the `.` key.
> - Post processing effects (turn it off).
> 
> If it is still not working, try disabling all other addons in ESO.

~~The bot says `STARTED` but nothing is happenin~~

> [FIXED] ~~This is a known issue with the bot, try reducing the window size of the game.  Don't use it on fullscreen mode.~~

Bot doesn't work in full screen.

> Run the bot with added option `--borderless` for starting the bot, like `python fishy.py --borderless`.

The bot catches the fish but doesn't press R to collect it

> Run the bot with the added option --collect-r for starting the bot, like `python fishy.py --collect-r`

### Contact
If you have any problems or you want to contact me for future ideas or want to collaborate in development you can contact me at the [DefineX Community discord server](https://discord.gg/V6e2fpc).

### Support Me
If you would like this project to continue its development, please consider supporting me on [Patreon](https://www.patreon.com/AdamSaudagar).  You can make a one time donation on [PayPal](https://www.paypal.me/AdamSaudagar).

### License
This project is licenced on the MIT License. Check out the full license over [here](https://github.com/adsau59/fishyboteso/blob/master/LICENSE).