# UoM WAM Spam

The official results release date is usually about two weeks after
the end of the exam period.  In practice, subject marks become visible
a week or two earlier than the official release date, and can be
inferred even earlier by detecting a change in calculated WAM (Weighted
Average Mark) as soon as the results are in the system (days before the
results themselves are made visible on the results page).

This script periodically checks the my.unimelb results page to detect
any changes to your WAM and listed results, and sends you a notification
when a change is detected.
If you run this script in the background on your computer or on a VPS,
you'll be free to enjoy the first few weeks of your holidays without
compulsively checking the results page yourself!
Or is it just me who does that?

Made with :purple_heart: by Matt, with contributions from CaviarChen,
blueset, josephsurin, and alanung.


## Installation

Clone this repository to get started WAM Spamming!

The basic WAM Spam script requires [Python 3.6](https://www.python.org/)
(or higher).

Once you have Python installed, you'll also need the following two
third-party Python packages for web scraping:

* [Requests](https://2.python-requests.org/en/master/), and 
* [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).

You can easily install these with [pip](https://pypi.python.org/pypi/pip)
using the command `pip3 install requests beautifulsoup4`, or however else
you prefer to install Python packages.


## Configuration

While the script has sensible default settings, it's also easily configurable.
You can modify the constants atop `wamspam.py` to easily change the behaviour.
Some important configuration options are:

* `CHECK_REPEATEDLY`: By default, the script will repeatedly check your WAM
until you kill it.
If you want the script to check your WAM only once, set this to `False`.

* `DELAY_BETWEEN_CHECKS`: You can configure how often the script logs in to
check for results.
I had mine set to check every 5 minutes (roughly the frequency at which I
would be checking if it wasn't for this script). But that seemed excessive...
so I set the default to 60 minutes.

* `DEGREES_TO_WATCH`: Unlike in a previous version, the script will watch all
degrees listed on your results page by default (`DEGREES_TO_WATCH = "all"`).
If you'd prefer it not to check them all for some reason, change this to a set
of degree indices to check (e.g. `DEGREES_TO_WATCH = {0}` to watch only the
first degree in the list). For students with only one degree, this option is
ignored.

There are some other configuration options, all documented in the script itself.

### Notifcation methods

The script can notify you using a range of notification methods. Each requires
its own configuration, as explained below:

* #### Student email (default)

   The default notifcation method. The script will log in to your university
   email account and send you a self-email notifying you about the WAM/results
   change.

   This option requires no additional configuration, but if you see an error
   (or similar):
   `smtplib.SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')`
   then Google must be blocking the script's attempt to log into your SMTP
   server. This is because Google thinks the way the script logs into your
   account does not meet their security standards.
   One work-around is to go to: [your Google security settings](https://myaccount.google.com/u/2/lesssecureapps?pageId=none)
   and turn on the option to "allow less secure apps".
   You might like to remember to turn it off when you get your results.

   The following notification method is a more secure workaround, with a few
   more configuration steps.

* #### Student email (Gmail with OAuth authentication)

   The script will log in to your university email account using Gmail's OAuth
   2.0 API and send you a self-email notification about the results change.

   This notification method requires two additional third-party Python packages:
   [Google API Python Client](https://github.com/googleapis/google-api-python-client) 
   and [Google OAuth](https://github.com/googleapis/google-auth-library-python-oauthlib).
   Install with e.g. `pip3 install google-api-python-client google-auth-oauthlib`.
   Then, follow these steps to configure the notification method:

   1. Obtain an OAuth 2.0 Client ID from the [Google API Console](https://console.developers.google.com)
      (Credentials > Create credentials > Create OAuth client ID > Other).
   2. Download the client ID JSON file and move it to the same directory as the
      script, in a file named `gmail-credentials.json` (this path is configurable
      in `notify/by_email_oauth.py`). This file is sensitive---remember to keep
      your secrets safe!
   3. Run the script. The first time, you'll need to authenticate in a browser
      to generate an authentication token. This will then be saved locally (in
      a file named `gmail-token.pickle`, configurable in `notify/by_email_oauth.py`)
      so that you won't have to do this step every time.
   4. If you want to run the script on a headless VPS etc. without a browser,
      you'll need to perform step 3 on a machine with a browser and then copy
      across the `gmail-token.pickle` file to the headless environment.

* #### WeChat message

   The script will use the [ServerChan](https://sc.ftqq.com) API to send you a
   [WeChat](https://wechat.com) message.

   You'll need to acquire a WeChat account and a ServerChan API key.
   Set up your account and then configure the script with your API key
   (you can hard-code it into `wamspam.py`, or add code to read it from a file 
   or environment variable or standard input, for example).
   Remember to keep your secrets safe!

* #### Telegram message

   The script will contact a Telegram Bot so that it may send you a Telegram
   message.

   You will need a [Telegram](https://telegram.org) account and a Telegram bot
   (which can be created using [@BotFather](https://t.me/botfather)).
   You'll then need a bot access token, which will be in the format:
   ```
   123456789:AaBbCcDdEeFfGgHhIiJjKkLlMm
   ```
   Set up your Telegram account and note the numerical user, group, or channel ID
   you wish to be contacted through (your 'destination').
   Configure the script with your access token and destination (you can hard-code
   them into `wamspam.py`, or add code to read them from a file or environment
   variable or standard input, for example).
   Remember to keep your secrets safe!

* #### Push notifications (Pushbullet)

   The script will use the [Pushbullet](https://www.pushbullet.com) API to send
   you a push notification (to whichever devices you have their apps installed).

   You'll need to acquire a Pushbullet account and API Access Token for this.
   Set up your account and link your desired devices, then configure the script
   with your access token (you can hard-code it into `wamspam.py`, or add code to
   read it from a file or environment variable or standard input, for example).
   Remember to keep your secrets safe!

* #### IFTTT webhook

   The script will trigger an [IFTTT](https://ifttt.com) webhook, which you can
   set up to contact you in any means supported by the IFTTT service.

   You'll need an IFTTT account and a webhook key. You can retrieve a key
   [here](https://ifttt.com/maker_webhooks), and should be in the format:
   ```
   Aa0Bb1Cc2Dd3Ee4Ff5Gg6H
   ```
   Configure the script with your webhook key (you can hard-code it into
   `wamspam.py`, or add code to read it from a file or environment variable or
   standard input, for example).
   The script will send notification messages with the event `wam-spam`, with
   `value1` set to the subject of the notification and `value2` set to the
   body text. Set up an IFTTT applet to respond to this event, and enter the
   webhook key into the script at runtime, or hard-code it into
   `notify/by_ifttt.py`.
   Remember to keep your secrets safe!

* #### Desktop notification

   The script will trigger a desktop notification displaying the update.

   Desktop notifications require an additional third-party Python module,
   [notify2](notify2.readthedocs.org). First, install this package (e.g.
   `pip install notify2`).

   Depending on your platform, you may need to install support for desktop
   notifications. For example, for Arch linux, you'll need [libnotify and a
   notification server](https://wiki.archlinux.org/index.php/Desktop_notifications).

   No script configuration is required, other than to turn on the notifier.

* #### Logfile message

   The script will log the notification message to a local file.

   The only configuration required is to configure the name of the desired file
   into the script (you can hard-code it into `wamspam.py`, or add code to read
   it from a file or environment variable or standard input, for example).

#### Multiple notification methods

The script can combine multiple notification methods in its attempt to reach
you regarding a detected WAM change.

All you'll need to configure each of your desired notification methods
individually using the above instructions, and ensure they all get added to the
multi-notifier during the configuration section of the script.

That is, to use multiple notification methods, *just uncomment and configure multiple
notification methods!*


## Usage

Once you have installed the requirements and configured the script, simply run
it with `python3 wamspam.py`.

The script will ask you for your unimelb username and password. It uses these
to log into the results page on your behalf every however-many minutes you
configured, looking for updated results. It stores the previous results in a
JSON-formatted text file between checks, for comparison.

The first time the script finds your results, or whenever it sees your results
data change, the script will also send you a notification using your configured
notification method(s).

> Note: Don't forget to stop the script after the final results release date!


### Common issues

The script is not very robust.  If anything goes wrong, it will probably crash
with an overly dramatic error message.  Please see these possible errors:

##### The script crashes with an error: `InvalidLoginException`.

You might have typed your username or password wrong.
Please check that you got them right, and try again.
