# -*- coding: utf-8 -*-
import os
import pandas as pd
import anthropic

def sentiment(key):
    if 'Positive' in key:
        return 'positive'
    elif 'Negative' in key:
        return 'negative'
    else:
        return 'neutral'

def price_translate(key):
    if 'Up' in key:
        return 'price_up'
    elif 'Down' in key:
        return 'price_down'
    else:
        return 'neutral'

def production_translate(key):
    if 'Up' in key:
        return 'production_up'
    elif 'Down' in key:
        return 'production_down'
    else:
        return 'neutral'

os.environ['CLAUDE_API_KEY'] = # Add key

base = pd.read_csv("./4. Keywords(2024-)/2024 Labeling/battery_2022_2023.csv",
                   index_col = 0)[:30]

prompt = '''How will these issues affect the price and production of batteries? Will they go up or down?
How would it affect the sentiment of battery consumers? Will it be positive or negative or neutral?
Provide only one answer for each question.
Give seperate answers for price, production and sentiment.
Seperate each answer, reason with '/'. Attach '/' at end of every answer.
If there is no reason, print '/ No reason /'
If the issue is not relevant, answer with 'Neutral'.

'''

record = pd.read_csv('./claude_test.csv', index_col = 0)


for i in range(25, 30):
    msg = [{"role": "user", "content": prompt + base['title'][i]}]

    client = anthropic.Anthropic(
        api_key = os.environ.get("CLAUDE_API_KEY"))

    response = client.messages.create(
        model = "claude-3-opus-20240229",
        messages = msg,
        temperature = 0,
        max_tokens = 1000,
        system='''Your answer should follow the following format:
                  Price: Up / Reason: context /
                  Production: Down / Reason: context /
                  Sentiment: Positive / Reason: context /
          ''',
        )

    print('Response', i, '\n')
    print(response.content[0].text, '\n')

    test = response.content[0].text.split('/')
    record.at[i, 'title'] = base['title'][i]
    record.at[i, 'claude_price'] = price_translate(test[0])
    record.at[i, 'claude_price_reason'] = test[1]
    record.at[i, 'claude_production'] = production_translate(test[2])
    record.at[i, 'claude_production_reason'] = test[3]
    record.at[i, 'claude_sentiment'] = sentiment(test[4])
    record.at[i, 'claude_sentiment_reason'] = test[5]

record.to_csv('./claude_test.csv')
