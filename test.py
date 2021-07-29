#!/usr/bin/env python
from bs4 import BeautifulSoup, NavigableString, Tag
import requests
import sys
import urllib
import json
import random
from flask import Flask, request, jsonify


questions_data = {
}

app = Flask(__name__)

def get_question_description(http_page: str) -> str:
    desc_soup = BeautifulSoup(http_page, "lxml")
    desc = desc_soup.find("div", {"class": "js-post-body"})
    all_text = ""
    for res in desc:
        if isinstance(res, Tag):
            all_text += res.text + '\n'
        elif isinstance(res, NavigableString):
            all_text += res + '\n'


    return all_text

def get_answer(http_page: str) -> str:
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


def setup_app(topics: []):
    print("Setting up the app!")
    for arg in topics:
        i = 0
        cur_page = requests.get('https://stackoverflow.com/questions/tagged/'+''.join(arg))
        try:
            cur_page.raise_for_status()
            soup = BeautifulSoup(cur_page.text, "lxml")
            questions = soup.select(".question-summary")

        except requests.exceptions.HTTPError:
            print("Could not get an SO search for {}, skipping.".format(arg))
            continue

        for que in questions:
            # Get the first five questions.
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
            if arg not in questions_data:
                questions_data[arg] = []
            questions_data[arg].append({
                "question_title": q,
                "question_description": qdesc,
                "views": views,
                "vote_count": vote_count,
                "link": a,
                "answer": answer
            })
            i += 1


print(questions_data)

# Get all the questions.
@app.get("/questions")
def get_questions():
    return jsonify(questions_data)


# Get a random question.
@app.get("/random/question")
def get_rnd_question():
    return jsonify(random.choice(list(questions_data.values())))


# Get a specific question.
@app.get("/question/<name>")
def get_question(name):
    if name in questions_data:
        return jsonify(questions_data[name])
    else:
        return jsonify({"error": "no value in questions"})


if __name__ == "__main__":
    setup_app(sys.argv[1:])
    app.run()
