# UoM WAM Spam

The official results release date is usually about two weeks after the end of the exam period. In practice, subject marks become visible a week or two earlier than the official release date, and can be inferred even earlier by detecting a change in calculated WAM (Weighted Average Mark) as soon as the results are in the system (days before the results themselves are made visible on the results page).

This script periodically checks the my.unimelb results page to detect any changes to your WAM, and sends you an email when a change is detected. If you run this script in the background on your computer or on a VPS, you'll be free to enjoy the first few weeks of your holidays without compulsively checking the results page yourself! Or is it just me who does that?

Made with :purple_heart: by Matt


## Installation

The WAM Spam script has the following dependencies:

* [Python 3.6](https://www.python.org/) (or higher).

* [Requests](https://2.python-requests.org/en/master/) and [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), third-party Python packages for web scraping.

    Easily install with [pip](https://pypi.python.org/pypi/pip) using the commands `pip3 install requests beautifulsoup4` or `pip3 install -r requirements.txt`, or however else you prefer to install Python packages.

If using the Gmail API with OAuth 2.0 (enabled by default), the script also has the following dependencies:

* [Google API Python Client](https://github.com/googleapis/google-api-python-client) (`pip3 install google-api-python-client`)
* [Google OAuth](https://github.com/googleapis/google-auth-library-python-oauthlib) (`pip3 install google-auth-oauthlib`)

    **You must obtain an OAuth 2.0 Client ID from the [Google API Console](https://console.developers.google.com) for the script to be able to send emails.** Save this in the file specified by `CLIENT_ID_PATH` in the `APIMailer` class of `mailer.py`.

If you do not wish to use the Gmail API (not recommended), set `LEGACY_AUTH` to `True` in `wamspam.py`. The last two dependencies are not required; remove the `APIMailer` class and the following imports from `mailer.py`:

```
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
```

## Configuration

While the script has sensible default settings, it's also easily configurable. You can modify the constants atop `wamspam.py` to easily change the behaviour. Some important configuration options are:

* `DEGREE_INDEX`: **This one's important!** If you have multiple degrees, then you need to tell the script which degree's WAM you want it to monitor. Just specify a (zero-based) index into the list of degrees on your results page (0 for the top degree in the list, 1 for the second, and so on). If you only have a single degree, you can leave this value.


* `CHECK_REPEATEDLY`: By default, the script will repeatedly check your WAM until you kill it. If you want the script to check your WAM only once, set this to `False`.

* `DELAY_BETWEEN_CHECKS`: You can configure how often the script logs in to check for results. I had mine set to check every 5 minutes (roughly the frequency at which I would be checking if it wasn't for this script). That seemed a bit excessive, so I changed it to check every hour. I'll probably speed it up when the results release date draws closer.

There are some other configuration options, all documented in the script itself.

## Usage

Once you have installed the requirements and configured the script, simply run it with `python3 wamspam.py`.

The script will ask you for your unimelb username and password. It uses these to log into the results page on your behalf every however-many minutes you configured, looking for your WAM. It stores the previous WAM in a text file between checks, for comparison.

If using the Gmail API (default), you will be asked to authenticate and grant permission to send email on your behalf the first time you run the script.

The first time the script finds your WAM, or whenever it sees your WAM change, the script will send you a self-email notifying you about the WAM change. Now you can compulsively check your email, instead of compulsively checking the results page! Haha.

> Note: Don't forget to stop the script after the final results release date!

### Common issues

The script is not very robust. If anything goes wrong, it will probably crash with an overly dramatic error message. Please see these possible errors:

##### The script crashes with an error: `InvalidLoginException`.

You might have typed your username or password wrong. Please check that you got them right, and try again.


##### The script crashes when logging in to my email account, with error `smtplib.SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted` or similar.

It sounds like you have set `LEGACY_AUTH` to `True` and Google is blocking the script's attempt to log in to its SMTP server. This is because the way the script logs into your account with this setting does not meet Google's security standards. The solution is to go to https://myaccount.google.com/u/2/lesssecureapps?pageId=none and turn the "allow less secure apps" option on. Remember to turn it off when you get your results.
