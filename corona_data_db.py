# corona_stats ( date_time text, total_infected integer, dead integer, recovered integer )
import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November',
          'December']


def get_data():
    def numSplit(num):
        num = str(num)
        num_len = len(num)
        commaCount = 0
        if num_len % 3 == 0:
            commaCount = (num_len // 3) - 1
        else:
            commaCount = num_len // 3
        poss = [(x*4)+3 for x in range(commaCount)]
        num = list(num)[::-1]
        for i in range(commaCount):
            num.insert(poss[i], " ")

        return "".join(num[::-1])

    covid_stats_url = 'https://www.worldometers.info/coronavirus/'

    # get actual TIME & DATE
    dateTime = str(datetime.now()).split()
    date = dateTime[0].split("-")[::-1]
    date[0], date[1] = date[1], date[0]
    date[0] = MONTHS[int(date[0])-1]
    date = " ".join(date)
    time = dateTime[1][:dateTime[1].index('.')]


    # gather numbers of cases
    req = requests.get(covid_stats_url)
    covid_stats_page = BeautifulSoup(req.content, 'html.parser')
    covid_stats = list(covid_stats_page.findAll(class_='maincounter-number'))

    total_infected = list(covid_stats[0].find('span'))[0]
    total_infected = total_infected.split(',')
    total_infected = int(''.join(total_infected))

    total_dead = list(covid_stats[1].find('span'))[0]
    total_dead = total_dead.split(',')
    total_dead = int(''.join(total_dead))

    total_recovered = list(covid_stats[2].find('span'))[0]
    total_recovered = total_recovered.split(',')
    total_recovered = int(''.join(total_recovered))

    # save in database
    conn = sqlite3.connect('corona_stats.db')
    c = conn.cursor()

    c.execute('SELECT * FROM corona_stats')
    data = c.fetchall()
    if data[-1][1] != total_infected or data[-1][2] != total_dead or data[-1][3] != total_recovered:
        c.execute('insert into corona_stats Values(:date_time, :total_infected, :dead, :recovered)',
                  {
                      'date_time': f'{date}, {time}', 'total_infected': total_infected,
                      'dead': total_dead, 'recovered': total_recovered
                  })
    conn.commit()

    conn.close()

    # output
    active = total_infected-total_dead-total_recovered
    active_last = data[-1][1] - data[-1][2] - data[-1][3]
    diff = active - active_last
    diff = f'+{numSplit(diff)}' if diff > 0 else f'{numSplit(diff)}'
    print(f'{date} @ {time}:\n'
          f' Infected: {numSplit(total_infected)}  /  +{numSplit(total_infected - data[-1][1])}\n'
          f' Dead: {numSplit(total_dead)}  /  +{numSplit(total_dead - data[-1][2])}\n'
          f' Recovered: {numSplit(total_recovered)}  /  +{numSplit(total_recovered - data[-1][3])}\n'
          f' Active: {numSplit(active)}  /  {diff}')


print("*** Covid - 19 Actual Stats ***")
get_data()
sleep(5)
