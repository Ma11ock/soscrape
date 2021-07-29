#!/usr/bin/env python
from bs4 import BeautifulSoup
import requests
import sys
import urllib
import json

res = requests.get('https://stackoverflow.com/questions/tagged/'+''.join(sys.argv[1:]))

soup = BeautifulSoup(res.text, "lxml")

questions = soup.select(".question-summary")

questions_data = {
    "questions": []
}

for que in questions:
    unanswered = que.select_one('.unanswered')
    if(unanswered):
        continue
    link = que.select_one('.question-hyperlink')
    q = link.getText()
    a = link.get('href')
    vote_count = que.select_one('.vote-count-post').getText()
    views = que.select_one('.views').attrs['title']
    questions_data['questions'].append({
        "questions": q,
        "views": views,
        "vote_count": vote_count,
        "link": "https://stackoverflow.com" + a,
    })

print(questions_data)
