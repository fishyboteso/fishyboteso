### fishyboteso
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
- Install [Provision's Chalutier : Fishing Mod](https://www.esoui.com/downloads/info2203-ProvisionsChalutierFishing.html) for ESO.
- Download/Clone the project.
- Install [Python v3.7.3](https://www.python.org/downloads/release/python-373/).
- Open the project folder then, `SHIFT + RIGHT CLICK` on the folder and press `Open Power Shell window here`.
- Type command `pip install -r requirements.txt` and press enter.  

Executing the Bot:
- Start the game.
- Type the command `python fishy.py` (For phone notification configuration, follow the instructions below instead). 

Starting fishing:
- Look at a fishing hole (don't start fishing)
- Press `f9` to start the bot.
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

> Botting does violate ESO's terms of service, so technically you could get banned. But this bot doesn't read or write memory from ESO so they won't know you are using a bot. This software doesn't come with any Liability or Warranty, I am not responsible if you do get banned.

How much automation does this bot provide?

> It's not a fully automated bot, it does fishing on its own but you will have to move from one hole to another manually (although I was developing a fully automated bot, I didn't get a positive feedback from the community so I discontinued it)

The bot says `look at a fishing hole before starting` but I am looking at a fishing hole

> The bot isn't able to detect the graphic/color created by `Provision's Chalutier : Fishing Mod`, this could be because,
> - Addon is not properly configured 
>   - Make sure you have copied the addon folder to `Elder Scrolls Online\live\AddOns` directory and turn on "Allow out of date addons" in ESO
>   - Try installing the addon from [Minion](https://minion.mmoui.com/)
> - Something is overlapping or bot can't find it 
>   - Move the emoji by pressing the `.` key and dragging it towards the center
> - Post processing effects (turn it off)
> 
> If it is still not working, try disabling all other addons in ESO.

The bot says `STARTED` but nothing is happening

> This is a known issue with the bot, try reducing the window size of the game.  Don't use it on fullscreen mode.

The bot catches the fish but doesn't press R to collect it

> Run the bot with the added option --collect-r for starting the bot, like `python fishy.py --collect-r`

I'm hitting the `F9` key but nothing is happening
> Certain keyboards have the F9 key assigned to another function.  Try remapping your F9 key to its intended function.  
> For example:
> - The Razer BlackWidow Chroma keyboard has the F9 key set to be a macro recording key.
>   - Simply go into Razer Synapse and reassign the F9 key from `Macro` to `Default`


### Contact
If you have any problems or you want to contact me for future ideas or want to collaborate in development you can contact me at the [DefineX Community discord server](https://discord.gg/V6e2fpc).

### Support Me
If you would like this project to continue its development, please consider supporting me on [Patreon](https://www.patreon.com/AdamSaudagar).  You can make a one time donation on [PayPal](https://www.paypal.me/AdamSaudagar).

### License
This project is licenced on the MIT License, check out the full license over [here](https://github.com/adsau59/fishyboteso/blob/master/LICENSE).
