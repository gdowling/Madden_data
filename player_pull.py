import pandas as pd
import requests 
from bs4 import BeautifulSoup
import re

# Getting Basic info and link to Player Page
home_url = "https://www.muthead.com/19/players?page="
page_number = 1
features = ['Name', 'Position', 'Overall', 'Card_set', 'player_page']
data = pd.DataFrame(columns= features)

#Getting all of the player pages
for page_number in range(130):
    url = home_url + str(page_number)
    r = requests.get(url)
    content = r.text
    soup = BeautifulSoup(content)
    table_body = soup.find('tbody')
    for table in table_body.find_all('tr'):
        td = table.find_all('td')
        player_name = td[1].find('a').text.strip()
        position = td[3].text
        overall = td[2].text
        card_set = td[1].find_all('span')[1].text
        player_page = td[1].find('a').get('href')
        basic_info = pd.DataFrame([[player_name, position, overall, card_set, player_page]])
        basic_info.columns = features
        data = data.append(basic_info, ignore_index = True)
      
#Getting skill rating from each players updates page
home_url_2 = 'https://www.muthead.com'
data_2 = pd.DataFrame()

for index, row in data.iterrows():
    skillnames =[]
    player_page = {'player_page' : str(row['player_page'])}
    url = home_url_2 + str(row['player_page']) + '/upgrades'
    r = requests.get(url)
    content = r.text
    soup = BeautifulSoup(content)
    player_stats = soup.find_all('li', {'class': 'player-upgrade-stats__item'})
    for i in range(len(player_stats)):
        skill = []
        ovr = []
        h = player_stats[i].text.strip()
        ovr, skill = h.split('\n')
        skillnames.append(skill)
        player_page[str(skill)] = ovr
    data_temp = pd.DataFrame(player_page, index = [i,])
    data_2 = data_2.append(data_temp)

#Player info from overview page
features_2 = ['Height', 'Weight', 'Team', 'Xbox_price', 'Ps4_price', 'Quick_sell']
data_3 = pd.DataFrame(columns= features_2)

for index, row in data.iterrows():
    url = home_url_2 + str(row['player_page'])
    r = requests.get(url)
    content = r.text
    soup = BeautifulSoup(content)
    height, weight = soup.find('span', {'class' : 'height-weight'}).text.split('\"')
    height = (pd.to_numeric(re.findall(r'(\d)\'', height).pop()) *12) + (pd.to_numeric(re.findall(r'\' (\d+)', height).pop()))
    weight = pd.to_numeric(re.findall(r'\d{3}', weight).pop())
    team = soup.find('span',{'class' : 'team'}).text
    xbox_price, ps4_price = soup.find_all('span', {'class' : 'item-price'})
    xbox_price, xbox_price_var = xbox_price.text.split(" ")
    ps4_price, ps4_price_var = ps4_price.text.split(" ")
    if 'K' in xbox_price:
        xbox_price = pd.to_numeric(re.findall(r'^.*(?=K)',xbox_price).pop()) * 1000
    elif 'M' in xbox_price:
        xbox_price = pd.to_numeric(re.findall(r'^.*(?=M)',xbox_price).pop()) * 1000000
    elif '—' in xbox_price:
        xbox_price = 'Not Actionable'
    else:
        xbox_price = pd.to_numeric(xbox_price.replace(',',''))     
    if 'K' in ps4_price:
        ps4_price = pd.to_numeric(re.findall(r'^.*(?=K)',ps4_price).pop()) * 1000
    elif 'M' in ps4_price:
        ps4_price = pd.to_numeric(re.findall(r'^.*(?=M)',ps4_price).pop()) * 1000000
    elif '—' in ps4_price:
        ps4_price = 'Not Actionable'
    else:
        ps4_price = pd.to_numeric(ps4_price.replace(',',''))   
    try:
        quick_sell = soup.find('div', {'class' : 'quicksell-value'}).text.strip()
        quick_sell = re.findall(r'\ (.*)',quick_sell).pop()
        quick_sell = pd.to_numeric(re.findall(r'\d+',quick_sell.replace(',','')).pop())
    except Exception:
        pass
    temp = pd.DataFrame([[height, weight, team, xbox_price, ps4_price, quick_sell]])
    temp.columns = features_2
    data_3 = data_3.append(temp, ignore_index = True)

#Merging the datasets
data_2 = data_2.reset_index(drop=True)
Merged_data = pd.merge(data, data_2,left_index = True, right_index = True)
Merged_data = pd.merge(Merged_data, data_3,left_index = True, right_index = True)
Merged_data = Merged_data.drop(['player_page_y'], axis = 1)
Merged_data = Merged_data[['Name', 'Position','Team','Height', 'Weight','Overall', 'Card_set', 'player_page_x','SPD',
       'STR', 'AGI', 'ACC', 'AWR', 'CTH', 'JMP', 'STA', 'INJ', 'TRK',
       'ELU', 'BTK', 'BCV', 'SFA', 'SPM', 'JKM', 'CAR', 'SRR', 'MRR',
       'DRR', 'CIT', 'SPC', 'RLS', 'THP', 'TAS', 'TAM', 'TAD', 'TOR',
       'TUP', 'BSK', 'PAC', 'RBK', 'RBP', 'RBF', 'PBK', 'PBP', 'PBF',
       'LBK', 'IBL', 'TAK', 'POW', 'PWM', 'FNM', 'BKS', 'PUR', 'PRC',
       'MCV', 'ZCV', 'PRS', 'KPW', 'KAC', 'KR','Xbox_price', 'Ps4_price', 'Quick_sell']]
Merged_data = Merged_data.rename(columns={'player_page_x' : 'Player_page'})
pd.to_numeric(Merged_data.Xbox_price)

Merged_data.to_csv('Madden_Ultimate_Team.csv')
