#!/usr/bin/env python
from bs4 import BeautifulSoup
import pandas as pd
import requests
import sys
import webbrowser


res = requests.get('https://google.com/search?q=site%3Astackoverflow.com+'+''.join(sys.argv[1:]))
res.raise_for_status()

soup = BeautifulSoup(res.text, 'lxml')
linkElements = soup.find_all('a')

def is_google_domain(url):
    google_domains = ('https://www.google.', 
                      'https://google.', 
                      'https://webcache.googleusercontent.', 
                      'http://webcache.googleusercontent.', 
                      'https://policies.google.',
                      'https://support.google.',
                      'https://maps.google.',
                      'https://accounts.google.')

    for g_url in google_domains:
        if url.startswith(g_url):
            return False

    return True


i = 0
for link in linkElements:
    strLink = link.get('href')[7:]
    if strLink.startswith('https://'):
        if not is_google_domain(strLink):
            continue
        print(strLink)
        i += 1
    if i >= 5:
        break


    
# with open('so.html', 'r') as html_file:
#     content = html_file.read()

#     tags = soup.find_all('code')
#     for tag in tags:
#         print(tag.text)
