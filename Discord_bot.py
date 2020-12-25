import discord
from discord.ext import commands
from discord.utils import get
import os
import json
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import copy
import random

# :)


server_id = 695708185318916157
bot_prefix = "!"
token = "Njk1NzA4NTY2NzEwOTExMDQ3.XoeHKw.yTShB0I21QwlaisGA3llgKQjOg8"
bot = commands.Bot(command_prefix=bot_prefix)
all_players_stats = []


def give_point_to_json(pick):
    with open('D:/Namizje/Discord_bot/players.json', 'r') as json_file:
        data = json.load(json_file)
        for user in data:
            if (data[str(user)]['ign']) == pick:
                data[str(user)]['n_honors'] += 1
    with open('D:/Namizje/Discord_bot/players.json', 'w') as json_file:
        json.dump(data, json_file)

def draw_winner(rool_list, players_point_score):
    print(rool_list)
    all_text = ""
    pick = ""
    for player in players_point_score:
        while True:
            random.shuffle(rool_list)
            pick = str(rool_list[0])
            if pick != str(player[0]):
                all_text += str(player[0]) + "  --------->  " + str(pick) + "\n"
                give_point_to_json(pick)
                break
    return all_text


def make_rool_list(players_point_score, n_players):
    rool_list = []
    print(players_point_score)
    for player in players_point_score:
        for i in range(int(n_players)*3):
            rool_list.append(player[0])
        for j in range(player[1]):
            rool_list.append(player[0])
    return rool_list
    

def compare_player_data(tmp, scores, i):
    if i == 1 or i >= 3 or i <= 5:
        scores = list(map(int, scores))
        naj = max(scores)
        ind = []
        if scores:
            for index, el in enumerate(scores):
                if el == naj:
                    ind.append(index)
        return ind
    elif i == 2:
        scores = list(map(int, scores))
        naj = min(scores)
        ind = []
        if scores:
            for index, el in enumerate(scores):
                if el == naj:
                    ind.append(index)
        return ind
    else:
        print("BAD")


def calculate_honor(all_stats):
    tmp = []
    for el in all_stats:
        tmp.append([el[0], 0])
    
    i = 1
    while i < 6:
        t = []
        for player in all_stats:
            t.append(player[i])

        best_ind = list(compare_player_data(tmp, t, i))

        if best_ind:
            for bi in best_ind:
                tmp[bi][1] += (len(all_stats)//len(best_ind)) #//2
        else:
            tmp[bi][1] += (len(all_stats)//len(best_ind)) #//2

        i = i + 1

    return tmp


def update_button(url):
    driver = webdriver.Firefox()
    driver.get(url)
    update_but = driver.find_element_by_id("SummonerRefreshButton")
    update_but.click()
    driver.quit()


def clean_data(data):
    if data == "MVP" or data == "ACE":
        return 1
    else:
        niz = ""
        for k in data:
            if k.isdigit():
                niz += k
        return niz


def get_data(url, sum_name):
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'lxml')
    op_gg_data = soup.find(class_="GameItemWrap")
    mvp = 0
    if op_gg_data.find(class_="Badge"):
        mvp = clean_data(str(op_gg_data.find(class_="Badge").get_text()))
    kills = clean_data(str(op_gg_data.find(class_="Kill").get_text()))
    deaths = clean_data(str(op_gg_data.find(class_="Death").get_text()))
    assist = clean_data(str(op_gg_data.find(class_="Assist").get_text()))
    killparticipation = clean_data(str(op_gg_data.find(class_="CKRate tip").get_text()))
    stats = [sum_name, kills, deaths, assist, killparticipation, mvp]
    print("get_data", stats)
    return stats


def get_players_data(members_list):
    all_player_stats = []
    print("member_list ", members_list)
    with open('D:/Namizje/Discord_bot/players.json', 'r') as json_file:
        data = json.load(json_file)
        for user in data:
            if (data[str(user)]['discn']) in members_list:
                url = ("https://eune.op.gg/summoner/userName="+str(data[str(user)]['ign'])).replace(" ", "%20")
                update_button(url)
                all_player_stats.append(get_data(url, str(data[str(user)]['ign'])))
    return all_player_stats


@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name)


@bot.command(pass_context=True, aliases=['a', 'add_player'])
async def add(ctx, data_in: str):
    data_in = data_in.split(';')
    await ctx.send("Adding user")
    with open('D:/Namizje/Discord_bot/players.json', 'r') as json_file:
        data = json.load(json_file)
    irln = data_in[0]
    ign = data_in[1]
    discn = data_in[2]
    data[str(irln)] = {
            'ign': str(ign),
            'discn': str(discn),
            'n_honors': 0
            }
    with open('D:/Namizje/Discord_bot/players.json', 'w') as f:
        json.dump(data, f)


@bot.command(pass_context=True, aliases=['r', 'honor'])
async def rool(ctx):
    members_list = []
    command_author = ctx.author
    voice_channel = command_author.voice
    all_members = voice_channel.channel.members
    for member in all_members:
        members_list.append(str(member.name + '#' + member.discriminator).lower())

    all_players_stats = get_players_data(members_list)
    players_point_score = calculate_honor(all_players_stats)
    print(players_point_score)
    rool_list = make_rool_list(players_point_score, len(all_players_stats))
    await ctx.send("Honors")
    await ctx.send(draw_winner(rool_list, players_point_score))
    print("\n")


bot.run(token)
