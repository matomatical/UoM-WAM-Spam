"""
log in to my.unimelb results page using a student account, check for a WAM
update, and then send the student a self-email if anything changed

:author: Matthew Farrugia-Roberts
"""
import time
import getpass

import requests
from bs4 import BeautifulSoup

from functools import partial
from notification import *


# # #
# SCRIPT CONFIGURATION
#

# set this to True if you would like the script to repeatedly check the results
# page, or False if you only want it to run once
CHECK_REPEATEDLY = True

# if you set the script to check repeatedly above, you can configure the delay 
# between WAM checks in minutes here
DELAY_BETWEEN_CHECKS = 60 # minutes

# leave these lines unchanged to be prompted for your username and password 
# every time you run the script, or just hard code your credentials here if 
# you're lazy (but then be careful not to let anyone else see this file)
UNIMELB_USERNAME = input("Username: ")
UNIMELB_PASSWORD = getpass.getpass()

# your WAM will be stored in this file in between checks
WAM_FILENAME = "wam.txt"


# # #
# WEB SCRAPING CONFIGURATION
#

# if you have multiple degrees, set this to the id of the degree with the WAM
# you want the script to watch (0, 1, 2, ... based on order from results page).
# if you only have a single degree, you can ignore this one.
DEGREE_INDEX = int(input("Degree index (or just press enter): ") or 0)

# select the HTML parser for BeautifulSoup to use. in most cases, you won't
# have to touch this.
BS4_PARSER = "html.parser"


# # #
# EMAIL CONFIGURATION
# 

# here we specify the format of the email messages (customise to your liking)
SUBJECT = "WAM Update Detected"
EMAIL_TEMPLATE = """Hello there!
{message}
Love,
WAM Spammer
"""
INCREASE_MESSAGE_TEMPLATE = """
I noticed that your WAM increased from {before} to {after}.
Congratulations! The hard work paid off (and I'm sure there
was a little luck involved, too).
"""
DECREASE_MESSAGE_TEMPLATE = """
I noticed that your WAM changed from {before} to {after}.
That's okay, I know you tried your best, and that's all
anyone can ask for.
"""
FIRSTMSG_MESSAGE_TEMPLATE = """
I noticed that your WAM is {after}. I hope it makes you
happy. Anyway, I'll keep an eye on it for you from now on,
and I'll let you know if it changes.
"""
HELLO_SUBJECT = "Hello! I'm WAM Spammer"
HELLO_MESSAGE = """
I'm WAM Spammer. This is just a test message to tell you
that I'm running. I'll look out for a change to your WAM
every so often---unless I crash! Every now and then you
should probably check to make sure nothing has gone wrong.
"""

# let's get to it!

def main():
    """Run the checking script, once or forever, depending on configuration."""
    # conduct the first check! don't catch any exceptions here, if the
    # check fails this first time, it's likely to be a configuration problem
    # (e.g. wrong username/password) so we should crash the script to let the
    # user know.

    # notification_helper = EmailNotification(UNIMELB_USERNAME, UNIMELB_PASSWORD)
    notification_helpers = select_notification_method()

    poll_and_notify(notification_helpers)
    # also send a test message to make sure the email configuration is working
    for notification_helper in notification_helpers:
        notification_helper.notify(HELLO_SUBJECT, EMAIL_TEMPLATE.format(message=HELLO_MESSAGE))

    while CHECK_REPEATEDLY:
        print("Sleeping", DELAY_BETWEEN_CHECKS, "minutes before next check.")
        time.sleep(DELAY_BETWEEN_CHECKS * 60) # seconds
        print("Waking up!")
        try:
            poll_and_notify(notification_helpers)
        except Exception as e:
            # if we get an exception now, it may have been some temporary
            # problem accessing the website, let's just ignore it and try
            # again next time.
            print("Exception encountered:")
            print(f"{e.__class__.__name__}: {e}")
            print("Hopefully it won't happen again. Continuing.")

def poll_and_notify(notification_helpers):
    """
    Check for an updated WAM, and send an email notification if any change is
    detected.
    """
    # check the results page for the updated WAM
    new_wam_text = scrape_wam()
    if new_wam_text is None:
        # no WAM found
        return
    new_wam = float(new_wam_text)

    # load the previous WAM to compare against
    try:
        with open(WAM_FILENAME) as wamfile:
            old_wam_text = wamfile.read()
        old_wam = float(old_wam_text)
    except:
        # the first time we run the script, there probably wont be a wam file
        old_wam = None

    # detect the type of WAM change so that we can choose which message to send
    if old_wam is None:
        message_template = FIRSTMSG_MESSAGE_TEMPLATE
    elif new_wam > old_wam:
        message_template = INCREASE_MESSAGE_TEMPLATE
    elif new_wam < old_wam:
        message_template = DECREASE_MESSAGE_TEMPLATE
    else:
        print("No change to WAM---stop before triggering notifications.")
        return

    # compose and send the message
    message = message_template.format(before=old_wam, after=new_wam)
    email_text = EMAIL_TEMPLATE.format(message=message)
    for notification_helper in notification_helpers:
        notification_helper.notify(SUBJECT, email_text)
    
    # update the wam file for next time
    with open(WAM_FILENAME, 'w') as wamfile:
        wamfile.write(f"{new_wam}\n")


class InvalidLoginException(Exception):
    """Represent a login form validation error"""


def scrape_wam(username=UNIMELB_USERNAME, password=UNIMELB_PASSWORD):
    with requests.Session() as session:
        # step 1. load a login page to initialse session
        print("Logging in to the results page")
        response = session.get("https://prod.ss.unimelb.edu.au"
            "/student/SM/ResultsDtls10.aspx?f=$S1.EST.RSLTDTLS.WEB")
        soup = BeautifulSoup(response.content, BS4_PARSER)

        # step 2. fill in login form and authenticate, reaching results page
        # get the form's hidden field values into the POST data
        hidden_fields = soup.find_all('input', type='hidden')
        login_form = {tag['name']: tag['value'] for tag in hidden_fields}
        # simulate filling in the form with username and password,
        # and pressing the login button
        login_form['ctl00$Content$txtUserName$txtText'] = username
        login_form['ctl00$Content$txtPassword$txtText'] = password
        login_form['__EVENTTARGET'] = "ctl00$Content$cmdLogin"
        # post the form, with a URL that will take us back to the results page
        response = session.post("https://prod.ss.unimelb.edu.au/student/"
            "login.aspx?f=$S1.EST.RSLTDTLS.WEB&ReturnUrl=%2fstudent%2fSM%2f"
            "ResultsDtls10.aspx%3ff%3d%24S1.EST.RSLTDTLS.WEB", data=login_form)
        # detect a potential failed login
        soup = BeautifulSoup(response.content, BS4_PARSER)
        if soup.find(id="ctl00_Content_valErrors"):
            raise InvalidLoginException("Your login attempt was not successful."
                " Please check your details and try again.")

        # now `soup` should be the parsed results page or multi-degree page...

        # step 3. if necessary, navigate to a specific degree page (for
        # multi-degree students)
        title = soup.find(id="ctl00_h1PageTitle")
        if title.text == "Results > Choose a Study Plan":
            print("Multiple degrees detected.")
            degree_grid = soup.find("table", id="ctl00_Content_grdResultPlans")
            cell = degree_grid.find_all("tr")[DEGREE_INDEX+1].find_all("td")[2]
            print(f"Loading results for degree {DEGREE_INDEX} - {cell.text}")
            # get the form's hidden field values into the POST data
            hidden_fields = soup.find_all('input', type='hidden')
            degree_form = {tag['name']: tag['value'] for tag in hidden_fields}
            # now simulate pressing the required degree button
            degree_form['__EVENTTARGET'] = "ctl00$Content$grdResultPlans"
            degree_form['__EVENTARGUMENT'] = f"ViewResults${DEGREE_INDEX}"
            # post the form, to take us to the results page proper
            response = session.post("https://prod.ss.unimelb.edu.au/student/SM/"
                "ResultsDtls10.aspx?f=$S1.EST.RSLTDTLS.WEB", data=degree_form)
            soup = BeautifulSoup(response.content, BS4_PARSER)

        # now `soup` should be the parsed results page for the chosen degree...

        # step 4. extract the actual WAM text from the results page, as required
        print("Extracting WAM")
        wam_para = soup.find(class_='UMWAMText')
        if wam_para is not None:
            wam_text = wam_para.find('b').text
        else:
            print("Couldn't find WAM (no WAM yet?)")
            wam_text = None

    return wam_text

def select_notification_method() -> NotificationHelper:
    print()

    methods = [
        ("Email", partial(EmailNotification, UNIMELB_USERNAME, UNIMELB_PASSWORD)),
        ("PushBullet", PushBulletNotification),
        ("ServerChan (WeChat)", ServerChanNotification),
        ("Telegram Bot", TelegramBotNotification),
        ("IFTTT Webhook", IFTTTWebhookNotification)
    ]
    for i, m in enumerate(methods):
        print("{}: {}".format(i, m[0]))
    inp = input("Please select your preferred notification method(s) (comma delimited): ")
    try:
        selected = set([int(i) for i in inp.split(',')])
        print("You have selected:", ", ".join([methods[i][0] for i in selected]))
    except:
        print(f"There was an error in your input, defaulting to method 0: {methods[0][0]}")
        return [methods[0][1]()]

    helpers = []
    for i in selected:
        helpers.append(methods[i][1]())

    return helpers


if __name__ == '__main__':
    main()
