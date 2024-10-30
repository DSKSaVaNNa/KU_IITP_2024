# -*- coding: utf-8 -*-
import os

import google.generativeai as genai
import pandas as pd
import vertexai


def sentiment(key):
    if "Positive" in key:
        return "positive"
    elif "Negative" in key:
        return "negative"
    else:
        return "neutral"


def price_translate(key):
    if "Up" in key:
        return "price_up"
    elif "Down" in key:
        return "price_down"
    else:
        return "neutral"


def production_translate(key):
    if "Up" in key:
        return "production_up"
    elif "Down" in key:
        return "production_down"
    else:
        return "neutral"


location = "asia-northeast3"
project_id = "iitp-api"
vertexai.init(project=project_id, location=location)

model = genai.GenerativeModel("gemini-pro")

prompt = """
How will these issues affect the price and production of batteries? Will they go up or down?
How would it affect the sentiment of battery consumers? Will it be positive or negative or neutral?
Provide only one answer for each question.
Give seperate answers for price, production and sentiment.
Seperate each answer, reason with '/'. Attach '/' at end of every answer.
If there is no reason, print '/ No reason /'
If the issue is not relevant, answer with 'Neutral'.
Your answer should follow the following format:

Price: Up / Reason: context /
Production: Down / Reason: context /
Sentiment: Positive / Reason: context /

"""

# api 답안 포맷 맞출 수 있는지 확인
# 답안 형식 예시 줘보기?


base = pd.read_csv(
    "./4. Keywords(2024-)/2024 Labeling/gpt_labeling_test.csv",
    index_col=0,
)
base["google_price"] = "a"
base["google_price_reason"] = "a"
base["google_production"] = "a"
base["google_production_reason"] = "a"
base["google_sentiment"] = "a"
base["google_sentiment_reason"] = "a"

for i in base.index:
    response = model.generate_content(prompt + base["title"][i])
    print("Response", i, "\n")
    # print(response.text)
    test = response.text.split("/")
    base.at[i, "google_price"] = price_translate(test[0])
    base.at[i, "google_price_reason"] = test[1]
    base.at[i, "google_production"] = production_translate(test[2])
    base.at[i, "google_production_reason"] = test[3]
    base.at[i, "google_sentiment"] = sentiment(test[4])
    base.at[i, "google_sentiment_reason"] = test[5]

    print(response.text, "\n")

base = base[
    [
        "title",
        "gpt_price",
        "gpt_price_reason",
        "google_price",
        "google_price_reason",
        "gpt_production",
        "gpt_production_reason",
        "google_production",
        "google_production_reason",
        "gpt_sentiment",
        "gpt_sentiment_reason",
        "google_sentiment",
        "google_sentiment_reason",
    ]
]
# base.to_csv('./4. Keywords(2024-)/2024 Labeling/genai_labeling_test.csv')
# base.to_excel('./4. Keywords(2024-)/2024 Labeling/genai_labeling_test.xlsx')


# aasdf = response.text.split('/')
