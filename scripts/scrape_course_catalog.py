import re
import urllib

import pandas as pd
import requests
import yaml
from bs4 import BeautifulSoup

#%%

## Configuration

# start here:
start_url = 'http://www.olin.edu/course-listing/'

# actually start on all these pages:
# TODO a more robust implementation would look for the ?page links on the original start page
start_urls = [start_url] + [start_url + '?page=%d' % i for i in range(1, 8)]

# download and parse all the pages
pages = [BeautifulSoup(requests.get(u).text, 'lxml') for u in start_urls]

# collect all the <a href="xxx"/> targets
hrefs = {a.attrs['href'] for page in pages for a in page.find_all('a')}

# select only those href targets whose URLs look like course pages:
# /course-listing/, followed by three or four letters, and optional hypen, three or four digits,
# an optional letter, a hypen, and after that we don't care.
course_urls = {urllib.parse.urljoin(start_url, href) for href in hrefs if re.match(r'\/course-listing\/[a-z]{3,4}-?\d{3,4}[a-z]?-', href)}

# download and parse all the course pages
course_pages = {u: BeautifulSoup(requests.get(u).text, 'lxml') for u in course_urls}

#%%
def parse_page(course_url, html):
    field_names = ['course-title', 'course-credits', 'course-hours', 'recommended-requisites', 'course-contact', 'course-description']
    field_elements = {field_name: html.select('.' + field_name) for field_name in field_names}
    field_text = {field_name: elts[0].text.strip() if elts else None for field_name, elts in field_elements.items()}

    course_number, course_name = re.match(r'(.+) - (.+)', field_text['course-title']).groups()
    course_credits = re.match(r'Credits:\s*(.+)', field_text['course-credits']).group(1)
    course_hours = field_text['course-hours'] and re.match(r'Hours:\s*(.+)', field_text['course-hours']).group(1)
    course_contact = field_text['course-contact'] and re.match(r'For information contact:\s*(.*)', field_text['course-contact']).group(1)
    course_description = ('\n'.join(e.text for e in field_elements['course-description'][0].next_siblings if not isinstance(e, str)).strip()
                          if field_elements['course-description'] else None)
    return {
        'course_url'        : course_url,
        'course_number'     : course_number,
        'course_name'       : course_name,
        'course_credits'    : course_credits,
        'course_hours'      : course_hours,
        'course_contact'    : course_contact,
        'course_description': course_description,
    }


df = pd.DataFrame.from_records([parse_page(course_url, html) for course_url, html in course_pages.items()])
df['course_area'] = df.course_number.str.extract(r'^([A-Z]+)', expand=False)
df.set_index('course_number', inplace=True)
df.sort_index(inplace=True)

df.head()

#%%
with open('./data/olin-courses-16-17.csv', 'w') as f:
    df.to_csv(f)
