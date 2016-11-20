# Unimelb Results Checker

Periodically checks my.unimelb results page for new results and sends an email when new results are posted.

By Matt Farrugia

## Dependencies

Requires python modules [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/), [html5lib](https://github.com/html5lib/), and [Selenium](http://docs.seleniumhq.org/). You can install these dependencies with [pip](https://pypi.python.org/pypi/pip) using `pip install -r path/to/repo/requirements.txt`.

Selenium requires headless browser [PhantomJS](http://phantomjs.org/) to be installed and on the path, so make sure `phantomjs` runs before you proceed.

> Note: I ran into some trouble using the version of phantomjs installed with `apt install phantomjs`, and needed to download the binary directly from the website linked above.

## Usage

The results-checking script needs two files to be placed within the **results** directory: **login.txt** and **email.txt**. **login.txt** should contain your student username on the first line, followed by your student password on the second line. An example **login.txt** file would be:

```
farrugiam
pAS5w0rd!1
```

**email.txt** uses the same structure, but should contain the gmail username of the account you want to use to email the results, and its gmail password on the second line. An example **email.txt** file for the gmail address `results.robot@gmail.com` would be:

```
results.robot
pAS5w0rd!1
```

> Note: only the part of the email address before the `@gmail.com` is included in the file.

After these files have been added to the **results** directory, you should be able to run the script from within that directory with `python main.py`. If the WAM on your results page is different from the number in **results/wam.txt**, you'll receive an email at `username@student.unimelb.edu.au` where `username` is the name in the first line of **results/login.txt**.


Finally, you probably want to run the script periodically. When executed from within the **results** directory, the bash script **results/run.sh** will run **main.py** forever, pausing inbetween for 300 seconds. So, you should be able to run, background and disown the script to have it run forever:

```
results/ $ bash run.sh > output.txt &
results/ $ disown %J
```
where J is the job number shown when you background sh run.sh

> Note: don't forget to stop it after all final results release date! In bash, you can `kill` a disowned script using its process ID, which can be found using `ps -x`. Make sure you use the ID of `bash run.sh`, not `sleep 300` or `python main.py`.