### fishyboteso
Auto fishing bot for Elder Scrolls Online. The Bot automatically fishes till the fishing hole disappears then it sends  notification of to the users phone including the statistics of that fishing hole.

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
Installing Project Requirements:
- Install [Provision's Chalutier : Fishing Mod](https://www.esoui.com/downloads/info2203-ProvisionsChalutierFishing.html) for ESO.
- Download/Clone the project.
- Install [Python](https://www.python.org/downloads/release/python-350/) (Recomended Python version 3.5.0 x64).
- Open the project folder then, `SHIFT + RIGHT CLICK` on the folder and press `Open Power Shell window here`.
- Type command `pip install -r requirements.txt` and press enter.  

Executing the Bot:
- Start the game.
-  Type command `python fishy.py` (For phone notification configuration, follow the instructions below instead). 

Starting fishing:
- Now look at a fishing hole (don't start fishing)
- And then press `f9` to start the bot.
- After the fishing is done, just move to next hole and look at it, fishing will start automatically.
- **IMPORTANT**: Keep the window focus on the game.

Tip:  
To increase the check rate of the bot, try changing `--check-frequency` option to less than 1, like
`python fishy.py --check-frequency 0.5`  

### For Phone Notification (Only Android)
- Install `notificationApp.apk` from the project files in your phone.
- Go to the app settings of the fishy app and allow all the notification permsions if you want floating notification with sound.
- Make sure your PC and your phone are on the same network.
- Open the app and press start service butoon.
- Type command `python fishy.py --ip <local-ip>` where local-ip is the ip you see in the App.
- You can minimize the app but don't close it as the service will stop.

### Contact
If you have any problems or you want to contact me for feature ideas or want to collaborate in development you can contact me on [DefineX Community discord server](https://discord.gg/V6e2fpc).

### Feeling generous?
You can donate me on [PayPal](https://www.paypal.me/AdamSaudagar).

### License
This project is licence to the MIT License, check out the full license over [here](https://github.com/adsau59/fishyboteso/blob/master/LICENSE).