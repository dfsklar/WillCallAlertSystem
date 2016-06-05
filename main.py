import re
import mechanize
# import lxml
# from lxml import etree
import pickle

import credentials


# Returns the raw HTML of the roster page post-login
def login_and_grab_roster():
    br = mechanize.Browser()
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

# Would be much nicer as a lambda use of filter()
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
    prev_avail = None

new_avail = fetch_fresh_available_titles(login_and_grab_roster())

if prev_avail:
    new_offerings = differ(prev_avail, new_avail)
    if new_offerings:
        print("WE HAVE NEW OFFERINGS TO REPORT")
        print(new_offerings)

with open("willcallclub_avail_titles.pkl", "w") as f:
    pickle.dump(new_avail, f)
