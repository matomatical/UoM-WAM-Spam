"""
log in to my.unimelb results page using an externally-specified student
account, check for updates on the results page, and then send the student
an email if anything has changed
"""

# web stuff
from selenium import webdriver
from bs4 import BeautifulSoup

# email stuff
import smtplib
from email.mime.text import MIMEText


def main():

	# get login details from configuration file
	username, password = get_username_password("login.txt")

	# login to results page and get its source
	source = get_results(username, password)

	# parse results page to check for updates
	soup = BeautifulSoup(source, "html5lib")

	# get the WAM
	new_wam = float(soup.find(class_="UMWAMText").find("b").text)

	# has it changed?
	changed = False
	with open("wam.txt", 'r+') as f:
		
		# what was the old wam?
		old_wam = float(f.readline().strip())
		
		# update the file if it has changed
		if (new_wam != old_wam):
			changed = True
			f.seek(0)
			f.write(str(new_wam)+'\n')
			f.truncate()


	# formulate and send an email if anything changed
	if changed:

		# construct the message body
		message = "Hey, there!\n\n" \
				+ "I noticed that your wam has changed from " \
				+ str(old_wam) + " to " + str(new_wam) + ". "
		if(new_wam > old_wam):
			message += "Congratulations! "
		else:
			message += "That's okay, you tried your best, " \
					+ "and that's all anyone can ask for! "
		message += "\n\nHave a nice day!\n\nLove, results robot\n--\n"

		# also the subject and destination address
		subject = "WAM Update to " + str(new_wam)
		target = username + "@student.unimelb.edu.au"

		# and send off the message!
		send_results(target, subject, message)
		print "Sent an email to " + target



def get_results(username, password):
	"""
	log in to the results page as username, get the page's HTML source,
	log out of the page and then return the page source.
	"""

	# load up the browser
	driver = webdriver.PhantomJS()
	driver.set_window_size(1120, 550)

	# go to the results page and enter the username and password
	url = "https://prod.ss.unimelb.edu.au/student/SM/ResultsDtls10.aspx" \
		+ "?f=%24S1.EST.RSLTDTLS.WEB"
	driver.get(url)

	usernamebox = driver.find_element_by_id("ctl00_Content_txtUserName_txtText")
	passwordbox = driver.find_element_by_id("ctl00_Content_txtPassword_txtText")

	usernamebox.send_keys(username)
	passwordbox.send_keys(password)

	loginbutton = driver.find_element_by_id("ctl00_Content_cmdLogin")
	loginbutton.click()

	# great the source before we log out, then reurn the source
	page_source = driver.page_source

	logoutbutton = driver.find_element_by_id("ctl00_LogoutLinkButton")
	logoutbutton.click()

	return page_source


def send_results(target, subject, message):
	"""log in to gmail as the results robot, and send an email to the target"""

	# what are the results robot's authentication details?
	username, password = get_username_password("email.txt")

	sender = username + "@gmail.com"
	
	# make the email object
	msg = MIMEText(message)
	msg['To'] = target
	msg['Subject'] = subject
	msg['From'] = sender

	# Log into gmail's free SMTP server as the
	# results robot and send the message
	s = smtplib.SMTP('smtp.gmail.com', 587); s.ehlo(); s.starttls()
	s.login(sender, password)
	s.sendmail(sender, [target], msg.as_string())
	s.quit()

def get_username_password(filename):
	with open(filename) as f:
		username = f.readline().strip()
		password = f.readline().strip()
	return (username, password)

if __name__ == '__main__': main()