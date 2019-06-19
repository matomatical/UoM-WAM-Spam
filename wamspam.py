"""
log in to my.unimelb results page using a student account, check for a WAM update, and then send the student a self-email if anything changed
"""
import time
import getpass
import smtplib
from email.mime.text import MIMEText

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


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
# If you only have a single degree, then set it to None.
# DEGREE_INDEX = 0
DEGREE_INDEX = None

# now, choose your web driver:

# after the deprecation of PhantomJS, the options are pretty much firefox or 
# google chrome. obviously we'll choose firefox (you don't use chrome, do you?)
DRIVER = webdriver.Firefox

# you'll also need to install the actual driver program. for firefox, it's 
# called `geckodriver`, and your package manager (e.g. brew) might have it,
# or just download the right version for your platform from the github page: 
# https://github.com/mozilla/geckodriver/releases and put it in the working 
# directory, or put it on your path (and remove the `./` from the line below)
DRIVER_EXEPATH = "./geckodriver"

# we probably want the web driver to run in headless mode (no display/GUI)
DRIVER_OPTIONS = webdriver.firefox.options.Options()
DRIVER_OPTIONS.headless = True

# # #
# EMAIL CONFIGURATION
# 

# the script will send email from and to your student email address
EMAIL_ADDRESS  = UNIMELB_USERNAME + "@student.unimelb.edu.au"
EMAIL_PASSWORD = UNIMELB_PASSWORD

# here we specify the format of the email messages (customise to your liking)
SUBJECT = "WAM Update Detected"
EMAIL_TEMPLATE = """Hey there!
{message}
Love,
Results Robot
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

# these are unlikely to change
UNIMELB_SMTP_HOST = "smtp.gmail.com"
UNIMELB_SMTP_PORT = 587

# let's get to it!

def main():
    """Run the checking script, once or forever, depending on configuration."""
    poll_and_email()

    while CHECK_REPEATEDLY:
        print("Sleeping", DELAY_BETWEEN_CHECKS, "minutes before next check.")
        time.sleep(DELAY_BETWEEN_CHECKS * 60) # seconds
        print("Waking up!")
        poll_and_email()


def poll_and_email():
    """
    Check for an updated WAM, and send an email notification if any change is
    detected.
    """

    # check the results page for the updated WAM
    new_wam_text = scrape_wam()
    if new_wam_text == None:
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
        print("No change to WAM---stop before sending an email.")
        return

    # compose and send the message
    message = message_template.format(before=old_wam, after=new_wam)
    email_text = EMAIL_TEMPLATE.format(message=message)
    email_self(SUBJECT, email_text)
    
    # update the wam file for next time
    with open(WAM_FILENAME, 'w') as wamfile:
        wamfile.write(f"{new_wam}\n")


def scrape_wam(username=UNIMELB_USERNAME, password=UNIMELB_PASSWORD):
    """
    Control a web browser to log into the results page as the student (with 
    provided username and password) and retrieve their WAM
    """
    print("Scraping WAM...")

    # load up the browser
    print("Setting up the web driver")
    with DRIVER(options=DRIVER_OPTIONS, executable_path=DRIVER_EXEPATH) as d:
        # d.set_window_size(1120, 550)
        d.implicitly_wait(5) # seconds
        
        # go to the results page and login with the provided username and 
        # password
        print("Logging in to the results page")
        d.get("https://prod.ss.unimelb.edu.au/student/SM/ResultsDtls10.aspx"
                "?f=$S1.EST.RSLTDTLS.WEB")
        usernamebox = d.find_element_by_id("ctl00_Content_txtUserName_txtText")
        passwordbox = d.find_element_by_id("ctl00_Content_txtPassword_txtText")
        loginbutton = d.find_element_by_id("ctl00_Content_cmdLogin")
        usernamebox.send_keys(username)
        passwordbox.send_keys(password)
        loginbutton.click()

        # if the student has multiple degrees, then we may need to navigate to
        # their chosen degree
        if DEGREE_INDEX is not None:
            # the buttons don't seem to have a convenient ID to latch on to,
            # but executing their scripted action directly achieves the same
            # effect as finding and clicking them:
            print("Loading results for degree number", DEGREE_INDEX)
            d.execute_script(
                f"javascript:__doPostBack('ctl00$Content$grdResultPlans',"
                f"'ViewResults${DEGREE_INDEX}')")
        
        # now we can try to find the WAM text itself within this results page
        try:
            wam_para = d.find_element_by_class_name("UMWAMText")
            print("Extracting WAM")
            wam_text = wam_para.find_element_by_tag_name("b").text
        except NoSuchElementException:
            print("Couldn't find WAM (no WAM yet, or page load timed out)")
            wam_text = None

        print("Logging out.")
        logoutbutton = d.find_element_by_id("ctl00_LogoutLinkButton")
        logoutbutton.click()

    return wam_text


def email_self(subject, text, address=EMAIL_ADDRESS, password=EMAIL_PASSWORD):
    """
    Send an email from the student to the student (with provided email address
    and password)

    :param subject: The email subject line
    :param text: The email body text
    :param address: The email address to use (as SMTP login username, email 
                    sender, and email recipient)
    :param password: The password to use for SMTP server login.
    """
    print("Sending an email to self...")
    print("From/To:", address)
    print("Subject:", subject)
    print("Message:", '"""', text, '"""', sep="\n")
    
    # make the email object
    msg = MIMEText(text)
    msg['To'] = address
    msg['From'] = address
    msg['Subject'] = subject

    # log into the unimelb student email SMTP server (gmail) to send it
    s = smtplib.SMTP(UNIMELB_SMTP_HOST, UNIMELB_SMTP_PORT)
    s.ehlo(); s.starttls()
    s.login(address, password)
    s.sendmail(address, [address], msg.as_string())
    s.quit()
    print("Sent!")


if __name__ == '__main__':
    main()
