import requests
from datetime import date, timedelta
import os.path
from os import path
import csv
import datetime

sdate = date(2020, 2, 24)
edate = date(2020, 12, 31)

delta = edate - sdate

for i in range(delta.days + 1):
    date = (sdate + timedelta(days=i))
    url = date.strftime('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-%Y%m%d.csv')        
    path = date.strftime('/tmp/dpc-covid19-ita-province-%Y%m%d.csv')        
    
    if not os.path.exists(path):
        r = requests.get(url)
        if r.status_code == 404:
            break

        open(path, 'wb').write(r.content)


lines = []

for i in range(delta.days + 1):
    date = (sdate + timedelta(days=i))
    path = date.strftime('/tmp/dpc-covid19-ita-province-%Y%m%d.csv')     

    if not os.path.exists(path):
        break  

    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            date = datetime.datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%S')
            date_str = date.strftime('%Y-%m-%d')
            location = row[5]
            fips = 1
            cases = row[9]
            deaths = 0

            if cases.isnumeric() and "aggiornamento" not in location:
                lines.append("{},{},{},{},{}".format(date_str,location,fips,cases,deaths))

lines.insert(0, "date,state,fips,cases,deaths")

with open('/tmp/joined.csv', 'w') as f:
    for line in lines:
        f.write("%s\n" % line)
