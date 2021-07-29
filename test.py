#!/usr/bin/env python
from bs4 import BeautifulSoup, NavigableString, Tag
import requests
import sys
import urllib
import json
from flask import Flask, request, jsonify
#from flask_restful import Resource, api

res = requests.get('https://stackoverflow.com/questions/tagged/'+''.join(sys.argv[1:]))

soup = BeautifulSoup(res.text, "lxml")

questions = soup.select(".question-summary")

questions_data = {
    "questions": []
}

app = Flask(__name__)

def get_question_description(http_page):
    desc_soup = BeautifulSoup(http_page, "lxml")
    desc = desc_soup.find("div", {"class": "js-post-body"})
    all_text = ""
    for res in desc:
        if isinstance(res, Tag):
            all_text += res.text + '\n'
        elif isinstance(res, NavigableString):
            all_text += res + '\n'


    return all_text

def get_answer(http_page):
    answer_soup = BeautifulSoup(http_page, "lxml")
    answer_cell = answer_soup.find("div", {"id": "answers"})
    answer = answer_cell.find("div", {"class": "js-post-body"})
    all_text = ""
    for res in answer:
        if isinstance(res, Tag):
            all_text += res.text + '\n'
        elif isinstance(res, NavigableString):
            all_text += res + '\n'
    return all_text


def setup_app():
    print("Setting up the app!")
    i = 0
    for que in questions:
        if i >= 5:
            break
        unanswered = que.select_one('.unanswered')
        if(unanswered):
            continue
        link = que.select_one('.question-hyperlink')
        q = link.getText()
        a = "https://stackoverflow.com" + link.get('href')
        vote_count = que.select_one('.vote-count-post').getText()
        views = que.select_one('.views').attrs['title']
        answer = ""
        qdesc = ""

        try:
            desc_html = requests.get(a)
            desc_html.raise_for_status()
            qdesc = get_question_description(desc_html.text)
            answer = get_answer(desc_html.text)
        except requests.exceptions.HTTPError:
            print("The URL {} is invalid!".format(a), file=sys.stderr)
            continue
        questions_data['questions'].append({
            "question_title": q,
            "question_description": qdesc,
            "views": views,
            "vote_count": vote_count,
            "link": a,
            "answer": answer
        })
        i += 1


print(questions_data)


@app.get("/questions")
def get_questions():
    return jsonify(questions_data)


@app.get("/question")
def get_question():
    return jsonify(questions_data["questions"][0])


if __name__ == "__main__":
    setup_app()
    app.run()
