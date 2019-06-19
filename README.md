# UoM WAM Spam

The official results release date is usually about two weeks after the end of the exam period. In practice, subject marks become visible a week or two earlier than the official release date, and can be inferred even earlier by detecting a change in calculated WAM (Weighted Average Mark) as soon as the results are in the system (days before the results themselves are made visible on the results page).

This script periodically checks the my.unimelb results page to detect any changes to your WAM, and sends you an email when a change is detected. If you run this script in the background on your computer or on a VPS, you'll be free to enjoy the first few weeks of your holidays without compulsively checking the results page yourself! Or is it just me who does that?

Made with :purple_heart: by Matt


## Dependencies

Requires:

* [Python 3.6](https://www.python.org/) (or higher).
* [Selenium](http://docs.seleniumhq.org/), a third-party web automation library. 
    * Easily install with [pip](https://pypi.python.org/pypi/pip) using `pip install -r requirements.txt`.
* A web driver such as Firefox's [geckodriver](https://github.com/mozilla/geckodriver) (enabling Selenium to browse the web for you).
    * Your package manager (e.g. homebrew) might have geckodriver, or you can just download the right version for your platform from [the releases page](https://github.com/mozilla/geckodriver/releases) and put it in the directory you are running the script from.
    * It should also be pretty simple to use ChromeDriver if you use Google Chrome rather than Firefox. You'll need to reconfigure the script to use a different browser wrapper (see below). Also, you should probably stop using Google Chrome.


## Configuration

While the script has sensible default settings, it's also easily configurable. You can modify the constants atop `wamspam.py` to easily change the behaviour. Some important configuration options are:

* `DEGREE_INDEX`: This one's important! If you have multiple degrees, then you need oto tell the script which degree's WAM you want it to monitor. Just specify a (zero-based) index into the list of degrees on your results page (0 for the top degree in the list, 1 for the second, and so on). If you only have a single degree, just leave the value as `None`.

* `DRIVER_EXEPATH`: Depending on how you install geckodriver, you may need to change the `DRIVER_EXEPATH` setting:
    * If you downloaded the executable and put it in the directory you are running the script from, leave it as `"./geckodriver"`.
    * If you put the executable somewhere else, set a relative or absolute filepath accordingly.
    * If you installed geckodriver into your system path, change this variable to `"geckodriver"`.
    
    If you chose to go with ChromeDriver then you'll have to change this variable (and also `DRIVER` and probably `DRIVER_OPTIONS`) to something else.

* `CHECK_REPEATEDLY`: By default, the script will repeatedly check your WAM until you kill it. If you want the script to check your WAM only once, set this to `False`.

* `DELAY_BETWEEN_CHECKS`: You can configure how often the script logs in to check for results. I had mine set to check every 5 minutes (roughly the frequency at which I would be checking if it wasn't for this script). That seemed a bit excessive, so I changed it to check every hour. I'll probably speed it up when the results release date draws closer.

There are other configuration options, all documented in the script itself.

## Usage

Once you have installed the requirements and configured the script, simply run it with `python3 wamspam.py`.

The script will ask you for your unimelb username and password. It uses these to log into the results page on your behalf every however-many minutes you configured, looking for your WAM. It stores the previous WAM in a text file in-between checks, for comparison.

The first time the script finds your WAM, or whenever it sees your WAM change, the script will also log in to your university email and send you a self-email notifying you about the WAM change.

> Note: Don't forget to stop the script after the final results release date!
