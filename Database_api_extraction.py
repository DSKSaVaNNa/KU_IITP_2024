# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 12:19:40 2024

@author: DSKIM
"""

import os
from datetime import datetime

import pandas as pd
from openai import OpenAI

# from dotenv import load_dotenv
from sqlalchemy import create_engine

# load_dotenv()


def read_db():
    """
    검색어 임베딩(ex: "copper price")
    :param issue_year: 이슈 년도
    :param issue_month: 이슈 월
    :param journal: 찾을 DB table (mining, reuters, theguardian, usatoday)
    :return:
        df: db table Dataframe
    """
    conn_string = f"mariadb+mariadbconnector://{os.getenv('user')}:{os.getenv('password')}@{os.getenv('server')}:{os.getenv('port')}/{os.getenv('database')}"
    # Creating a sqlalchemy engine
    engine = create_engine(conn_string).connect()

    df = pd.read_sql_table("mining", engine)
    df["date"] = pd.to_datetime(df["date"])
    df = df[
        (df["date"] >= datetime(year=2024, month=1, day=1))
        & (df["date"] < datetime(year=2024, month=6, day=30))
    ]
    return df


def issue_generation():  # 주어진 연/월에서 이슈 추출
    """
     year, month, keyword에 따른 기사 데이터베이스 로딩 후 number만큼 이슈 추출
    :param year: 이슈 추출할 년 (int)
    :param month: 이슈 추출할 월 (int)
    :param keyword: 이슈 추출할 상품( str)
    :param mode: 추출할 언론사 선택 ('all' 일 시 mining, reuters, usatoday, guardian / 아닐 시 mining, reuters만 사용)
    :param number: 추출할 이슈 개수(int)
    :return:
        dep_ : 입력한 월에서 가장 연관성 있는 k개 기사를 선정한 데이터프레임
    """
    # 이슈 연-월 (ex. 2022-01)
    df_ = read_db()

    exclude = [
        "what",
        "how",
        "why",
        "Why",
        "What",
        "How",
        ":",
        "Ranking",
        "ranking",
        "RANKING",
        "RANKED",
        "RANKED:",
        "CHARTS:",
        "EXPLAINER:",
        "Home:",
        "case for",
        "Why",
        "top 10",
        "Romans",
        "Ancient",
        "research",
        "-research",
        "Scientist",
        "scientist",
        "Factbox",
        "Researcher",
        "researcher",
        "Visualizing",
        "Visualization",
    ]
    # df_['True'] = [any([ex in s for ex in exclude]) for s in df_.title]
    # df_ = df_[df_['True'] == False]

    pattern = "|".join([f"(?i){ex}" for ex in exclude])
    # Use str.contains to filter the DataFrame
    dep_ = df_[~df_["title"].str.contains(pattern, regex=True)]

    # 기사 제목 embedding
    # dep_ = df_[['title', 'body', 'date', 'link', 'locations']].reset_index(drop = True)
    return dep_


# data = pd.read_excel('./copper_10years_sim_0.6.xlsx', engine = 'openpyxl', index_col = 0)
os.environ["OPENAI_API_KEY"] = "insert chatgpt api key here"

# 프롬프트는 openai_prompt만 수정하시면 됩니다 !!

openai_prompt = """ Considering the risk factors of the global value chain, extract related events from the following news title.
Raw materials or country names are NOT an event.
An event is a keyword that can affect the price or production of specific raw materials or products, from on a general standpoint.
Below is a list of event examples.

COVID-19 Pandemic
Natural Disasters
Labor Strikes
Logistics Delays
Maritime Transport Disruptions
Port Congestion
Supplier Bankruptcy
War
Factory Fires
Traffic Accidents
Demand Surge
Economic Recovery
Consumer Trend Changes
New Product Launch
Promotional Activities
Seasonal Factors

Product Lifecycle
Partnership Collaboration
R&D Investment
Logistics Infrastructure
Regulatory Changes
Market Accessibility

Answer only the issue requested. Do NOT provide any reasons.
If there is no related issue, reply with 'no related issue'.
"""

# data = issue_generation()
data = pd.read_excel("./mining_rawdata.xlsx", index_col=0)
data["event"] = "a"
data = data[["title", "event", "body", "date", "link", "locations"]]

title_samples = 10  # 샘플링할 기사의 개수를 왼쪽에 적어주세요
data = data.sample(frac=title_samples / len(data)).reset_index(drop=True)
event_count = dict()
issue_list = []

for i in data.index:
    context = data.at[i, "body"]
    message = [
        {"role": "assistant", "content": openai_prompt + context}
    ]  # openai_prompt + context
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    if i % 100 == 0:
        print("")
        print("----------------------")
        print(f"Reached index {i}")
        print("----------------------")
        print("")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=message,
        temperature=0,
        max_tokens=256,
    )

    print(context)
    print(response.choices[0].message.content)
    print("")
    issue_list.append(response.choices[0].message.content)
    data.at[i, "event"] = response.choices[0].message.content

    if data.at[i, "event"] in event_count.keys():
        event_count[data.at[i, "event"]] += 1
    else:
        event_count[data.at[i, "event"]] = 1


issue_list = list(set(issue_list))  # save: "wb", load: "rb" pickle.load()
savefilename1 = "./저장할 엑셀 파일의 이름을 적어주세요"
savefilename2 = "./저장할 이슈 개수 엑셀 파일의 이름을 적어주세요"

data.to_excel(savefilename1 + ".xlsx")

event = pd.DataFrame(columns=["issue"], index=range(len(issue_list)))
event["issue"] = issue_list
event["count"] = event["issue"].map(event_count)
event["ratio"] = event["count"] * 100 / len(data)
event = event.sort_values(by="count", ascending=False).reset_index(drop=True)

event.to_excel(savefilename2 + ".xlsx")
