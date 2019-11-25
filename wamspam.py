"""
log in to my.unimelb results page using a student account, check for a results
update, and then send the student a notification if anything changed

:author: Matthew Farrugia-Roberts and contributors
"""
import json
import time
import getpass

import requests
from bs4 import BeautifulSoup

import messages

# # #
# SCRIPT CONFIGURATION
#

print("Configuring script...")

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

# your results will be stored in this file in between checks
RESULTS_FILENAME = "results.txt"

# by default, the script will watch all of your degrees. you can alter this
# setting here by providing a set of degree indexes (based on the order from
# the results page, starting with 0) or "all" for all degrees:
DEGREES_TO_WATCH = "all"
# for example, to watch only your first degree:
# DEGREES_TO_WATCH = {0}
# for students with only a single degree, this option is ignored

# for students with a single degree, we can't scrape the degree name from the
# degree list, so we use a default
# you can optionally personalise your degree name here (e.g. replace with
# "Bachelor of Science (Computing and Software Systems)":
DEFAULT_DEGREE_NAME = "degree"


# # #
# WEB SCRAPING CONFIGURATION
#

# select the HTML parser for BeautifulSoup to use. in most cases, you won't
# have to touch this.
BS4_PARSER = "html.parser"


# # #
# NOTIFICATION CONFIGURATION
#

# we'll use a multi-notifier to allow for any number of
# notification methods (added below)
from notify.by_multiple import MultiNotifier
NOTIFIER = MultiNotifier()

# choose one or more notification methods to use when a change is detected.

# in most cases you can configure the notification method with the required
# secrets by including them in the corresponding script, or by leaving the
# scripts alone and typing them in at start-up time (see README for per-method
# instructions, and remember to keep your secrets safe!)
print("Configuring chosen notification method(s)...")

# option 0: student email notification, via SMTP
from notify.by_email import SMTPGmailNotifier
# the script will send email from and to your student email address
# by default.
# if you need to use an app-specific password to get around 2FA on
# your email account, or other authentication issues, you can set it
# here as the value of password.
GMAIL_ADDRESS  = UNIMELB_USERNAME + "@student.unimelb.edu.au"
GMAIL_PASSWORD = UNIMELB_PASSWORD # or app-specific password
NOTIFIER.add_notifier(SMTPGmailNotifier(
    address=GMAIL_ADDRESS,
    password=GMAIL_PASSWORD)) 

# option 1: student email notification, via Gmail's API + OAuth
# from notify.by_email_oauth import GmailAPINotifier
# GMAIL_ADDRESS = UNIMELB_USERNAME + "@student.unimelb.edu.au"
# # TODO: Add other configuration e.g oauth token
# NOTIFIER.add_notifier(GmailAPINotifier(
#     address=GMAIL_ADDRESS))

# option 2: wechat notification via ServerChan
# uncomment below and configure to enable
# from notify.by_wechat import ServerChanNotifier
# SERVERCHAN_API_KEY = # put API key here, as a string (see README)
# NOTIFIER.add_notifier(ServerChanNotifier(
#    apikey=SERVERCHAN_API_KEY))

# option 3: telegram notification via a telegram bot
# uncomment below and configure to enable
# from notify.by_telegram import TelegramBotNotifier
# TELEGRAM_ACCESS_TOKEN = # put access token string here (see README)
# TELEGRAM_DESTINATION  = # put destination chat name here (see README)
# NOTIFIER.add_notifier(TelegramBotNotifier(
#    token=TELEGRAM_ACCESS_TOKEN,
#    chat=TELEGRAM_DESTINATION))

# option 4: push notification via pushbullet
# uncomment below and configure to enable
# from notify.by_push import PushbulletNotifier
# PUSHBULLET_ACCESS_TOKEN = # put access token here (string) (see README)
# NOTIFIER.add_notifier(PushbulletNotifier(
#    token=PUSHBULLET_ACCESS_TOKEN))

# option 5: ifttt notification via triggering a webhook
# uncomment below and configure to enable
# from notify.by_ifttt import IFTTTWebhookNotifier
# IFTTT_WEBHOOK_KEY = # put webhook key string here (see README)
# NOTIFIER.add_notifier(IFTTTWebhookNotifier(
#    key=IFTTT_WEBHOOK_KEY))

# option 6: desktop notifications using notify2 python library
# uncomment below to enable
# from notify.by_desktop import DesktopNotifier
# NOTIFIER.add_notifier(DesktopNotifier())

# option 7: notifications via appending to a local file
# uncomment below and configure to enable
# from notify.by_logfile import LogFileNotifier
# LOGFILE_FILEPATH = # put filepath string here (see README)
# NOTIFIER.add_notifier(LogFileNotifier(
#    filepath=LOGFILE_FILEPATH))


# let's get to it!

def main():
    """Run the checking script, once or forever, depending on configuration."""
    # send a test message to make sure the notification configuration works
    NOTIFIER.notify(*messages.hello_message(delay=DELAY_BETWEEN_CHECKS))

    # conduct the first check! don't catch any exceptions here, if the check
    # fails this first time, it's likely to be a configuration problem (e.g.
    # wrong username/password) so we should crash the script to let the user
    # know.
    poll_and_notify()

    while CHECK_REPEATEDLY:
        print("Sleeping", DELAY_BETWEEN_CHECKS, "minutes before next check.")
        time.sleep(DELAY_BETWEEN_CHECKS * 60) # seconds
        print("Waking up!")
        try:
            poll_and_notify()
        except Exception as e:
            # if we get an exception now, it may have been some temporary
            # problem accessing the website, let's just ignore it and try
            # again next time.
            print("Exception encountered:")
            print(f"{e.__class__.__name__}: {e}")
            print("Hopefully it won't happen again. Continuing.")


def poll_and_notify():
    """
    Check for updated results, and send a notification if a change is detected.
    """
    # check the results page for the latest results
    new_results = scrape_results(UNIMELB_USERNAME, UNIMELB_PASSWORD)

    # load the previous results from file
    try:
        with open(RESULTS_FILENAME) as resultsfile:
            old_results = json.load(resultsfile)
    except:
        # the first run, there probably won't be such a file
        # imagine a default
        old_results = {DEFAULT_DEGREE_NAME: {"wam": None, "results": []}}

    # compare the results for each degree:
    degrees = new_results.keys() | old_results.keys()
    for degree in degrees:
        if degree not in new_results:
            # maybe by error, the degree seems to have been removed
            # that doesn't mean we should forget it! forward old results
            # so that we don't remove them from the file
            print("Missing results for", degree)
            new_results[degree] = old_results[degree]
        elif degree not in old_results:
            # still unlikely during results period; but a new degree has
            # appeared! send the initialisation message
            print("Found new results for", degree)
            results = new_results[degree]
            NOTIFIER.notify(*messages.initial_message(degree, results))
        else:
            # more likely, we have seen the degree before, but the results may
            # have changed:
            old = old_results[degree]
            new = new_results[degree]
            if old != new:
                # compute difference, and send notification
                print("Found updated results for", degree)
                NOTIFIER.notify(*messages.update_message(degree, old, new))
            else:
                # no change to results for this degree. ignore it!
                print("No change for", degree)

    # update the results file for next time
    with open(RESULTS_FILENAME, 'w') as resultsfile:
        json.dump(new_results, resultsfile, indent=2)


class InvalidLoginException(Exception):
    """Represent a login form validation error"""


def scrape_results(username, password):
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
        # step 3. either way, we are ready to start building the transcript!
        transcript = {}

        title = soup.find(id="ctl00_h1PageTitle")
        if title.text == "Results > Choose a Study Plan":
            print("Multiple degrees detected. Walking results pages...")
            grid = soup.find("table", id="ctl00_Content_grdResultPlans")
            rows = grid.find_all("tr")[1:] # skip header
            cells = [row.find_all("td")[2].text for row in rows]

            # get the form's hidden field values into the POST data
            hidden_fields = soup.find_all('input', type='hidden')
            degree_form = {tag['name']: tag['value'] for tag in hidden_fields}

            for degree_index, degree_name in enumerate(cells):
                if DEGREES_TO_WATCH != "all":
                    if degree_index not in DEGREES_TO_WATCH:
                        print(f"Skipping degree {degree_index}: {degree_name}")
                        continue
                print(f"Loading results for {degree_index}: {degree_name}")
                # now simulate pressing the required degree button
                degree_form['__EVENTTARGET'] = "ctl00$Content$grdResultPlans"
                degree_form['__EVENTARGUMENT'] = f"ViewResults${degree_index}"
                # post the form, to take us to the results page proper
                response = session.post("https://prod.ss.unimelb.edu.au/"
                    "student/SM/ResultsDtls10.aspx?f=$S1.EST.RSLTDTLS.WEB",
                    data=degree_form)
                soup = BeautifulSoup(response.content, BS4_PARSER)
                # now `soup` should be the parsed results page for this degree
                transcript[degree_name] = parse_page(soup)
        else:
            print("Single degree detected. Parsing results page directly...")
            # in this case `soup` is already the parsed results page for the
            # only degree
            transcript[DEFAULT_DEGREE_NAME] = parse_page(soup)
            
        return transcript

def parse_page(soup):
    # step 4. extract the results data from the results page, as required
    print("Extracting WAM")
    wam_para = soup.find(class_='UMWAMText')
    if wam_para is not None:
        wam_text = wam_para.find('b').text
    else:
        print("Couldn't find WAM (no WAM yet?)")
        wam_text = None

    print("Extracting subject results")
    results = []
    results_table = soup.find("table", id='ctl00_Content_grdResultDetails')
    if results_table is None:
        print("Couldn't find results (no results yet?)")
    else:
        rows = results_table.find_all("tr")[1:] # skip header
        for row in rows:
            cells = [cell.text.strip() for cell in row.find_all("td")]
            # cells is a list of strings containing this result's details e.g.:
            # ['2019', 'Semester 1', 'COMP90045', 'PLI', '2', '99', 'H1', '12.500']
            # extract the relevant details:               (^ btw this is 'version')
            result = {
                "subject": f"{cells[2]} {cells[3]}",
                "date":    f"{cells[0]}, {cells[1]}",
                "mark":    cells[5],
                "grade":   cells[6],
                "credits": cells[8]
            }
            results.append(result)

    return {"wam": wam_text, "results": results}


if __name__ == '__main__':
    main()
