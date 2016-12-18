import re
import mechanize
import pickle

import credentials


# Returns the raw HTML of the roster page post-login
def login_and_grab_roster():
    br = mechanize.Browser()
    br.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:45.0) Gecko/20100101 Firefox/45.0')]
    br.open("http://willcallclub.com/login.php")

    br.select_form(nr=0)

    br.find_control(name="username").value = credentials.USERNAME
    br.find_control(name="password").value = credentials.PASSWORD

    response_login = br.submit()

    return response_login.get_data()


# Returns a sorted list of all available titles
def fetch_fresh_available_titles(html):
    available_titles = []

    regex_available = re.compile('.*<div class=.footer.>(.*)</div>.*', re.IGNORECASE)
    regex_sold_out = re.compile('.*<div class=.footer.>(.*)<.*SOLD OUT.*</div>.*', re.IGNORECASE)
    for line in html.splitlines():
        the_match = regex_sold_out.match(line)
        if the_match:
            title = the_match.group(1)
            # Currently, I'm not doing anything with SOLD OUT except ignoring them (as though not offered at all)
        else:
            the_match = regex_available.match(line)
            if the_match:
                title = the_match.group(1)
                available_titles.append(title)

    return sorted(available_titles)


def fetch_previous_available_titles():
    with open("willcallclub_avail_titles.pkl") as f:
        return pickle.load(f)


def titlelist_abbrev(arr_titles):
    return str(map(lambda t: t[0:45], arr_titles))

# This differ Would be much nicer as a lambda use of filter() -- good exercise for Matt
def differ(old, new):
    new_offerings = []
    for x in new:
        if x not in old:
            new_offerings.append(x)
    return new_offerings


prev_avail = None
try:
    prev_avail = fetch_previous_available_titles()
except:
    prev_avail = []

new_avail = fetch_fresh_available_titles(login_and_grab_roster())

new_offerings = differ(prev_avail, new_avail)

if new_offerings:
    import subprocess
    titles =  titlelist_abbrev(new_offerings).replace('\'','').replace('"','')
    retval = subprocess.call(['/bin/sh', './report_new_offerings.sh', titles, credentials.SMSEMAIL])
    print("Return value from the email-alert launch: " + str(retval))
    new_offerings = new_offerings
    retval = subprocess.call([
        'curl',
        '-X',
        'POST',
        '--data-urlencode',
        'payload={"channel": "#general", "username": "webhookbot", "text": "%s", "icon_emoji": ":ghost:"}' % titles,
        'https://hooks.slack.com/services/%s' % credentials.SLACK
    ])
    print("Return value from the slack webhook launch: " + str(retval))
    

with open("willcallclub_avail_titles.pkl", "w") as f:
    pickle.dump(new_avail, f)
