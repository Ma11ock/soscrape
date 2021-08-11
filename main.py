#!/usr/bin/env python
"""
A stackoverflow webscraper with a simple RESTful API.
"""
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
    """
    Get a stackoverflow's question description.
    http_page: an HTTP webpage as a string.
    """
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
    """
    Get a stackoverflow's question's top answer.
    http_page: an HTTP webpage as a string.
    """
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


def setup_app(topics: [], maxQs: int = 5):
    """
    Setup the app data. Scrape stackoverflow and write the results to
    questions_data.
    topics: An array of strings to scrape stackoverflow for.
    maxQs: The max number of questions to scrape per topic.
    """
    print("Setting up a group of questions, number is {}".format(maxQs))
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
            if i >= maxQs:
                break
            # Don't even bother if the question is unanswered.
            unanswered = que.select_one('.unanswered')
            if(unanswered):
                continue
            link = que.select_one('.question-hyperlink')
            # Check if the current question is already present. If so, skip.
            # If the topic is not present in the dictionary, create it.
            if arg not in questions_data:
                questions_data[arg] = []
            else:
                for quest in questions_data[arg]:
                    if "link" in quest and quest["link"] == link:
                        continue
            q = link.getText()
            a = "https://stackoverflow.com" + link.get('href')
            vote_count = que.select_one('.vote-count-post').getText()
            views = que.select_one('.views').attrs['title']
            answer = ""
            qdesc = ""

            # Try to get the question's page. It sometimes does not work.
            try:
                desc_html = requests.get(a)
                desc_html.raise_for_status()
                qdesc = get_question_description(desc_html.text)
                answer = get_answer(desc_html.text)
            except requests.exceptions.HTTPError:
                print("The URL {} is invalid!".format(a), file=sys.stderr)
                continue
            questions_data[arg].append({
                "question_title": q,
                "question_description": qdesc,
                "views": views,
                "vote_count": vote_count,
                "link": a,
                "answer": answer
            })
            i += 1


# Get all the questions.
@app.get("/questions")
def get_questions():
    """
    Get all the question data.
    """
    return jsonify(questions_data)



# Get a group of questions about a topic.
@app.get("/question/<name>")
def get_question(name):
    """
    Get a question by topic.
    name: The name of the topic.
    """
    if name not in questions_data:
        setup_app([name])
    if name in questions_data:
        return jsonify(questions_data[name])

    return jsonify({"error": "Value does not exist."})

@app.get("/question/<name>/<number>")
def get_question_num(name, number):
    """
    Get a question by topic and a specific number of them.
    name: The name of the topic.
    number: The number of questions to get for that topic.
    """
    try:
        num = int(number)
    except ValueError:
        msg = "The value {}/{} is invalid.".format(name, number)
        print(msg, file=sys.stderr)
        return jsonify({"error": msg})
    if name not in questions_data:
        setup_app([name])
    if name not in questions_data:
        msg = "The value {} could not be found on Stack Overflow.".format(name)
        print(msg, file=sys.stderr)
        return jsonify({"error": msg})
    return jsonify(questions_data[name][:num])

# Get a random question.
@app.get("/random/question")
def get_rnd_question():
    """
    Get a random question.
    """
    if questions_data:
        return jsonify(random.choice(list(questions_data.values())))
    else:
        return get_question("python")
        



if __name__ == "__main__":
    setup_app(sys.argv[1:])
    app.run()
