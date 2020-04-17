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

for i in range(delta.days + 1):
    date = (sdate + timedelta(days=i))
    url = date.strftime('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-%Y%m%d.csv')        
    path = date.strftime('/tmp/dpc-covid19-ita-regioni-%Y%m%d.csv')        
    
    if not os.path.exists(path):
        r = requests.get(url)
        if r.status_code == 404:
            break

        open(path, 'wb').write(r.content)

regions = dict()

for i in range(delta.days + 1):    
    date = (sdate + timedelta(days=i))
    path = date.strftime('/tmp/dpc-covid19-ita-regioni-%Y%m%d.csv')

    if not os.path.exists(path):
        break  

    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            date = datetime.datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%S')
            date_str = date.strftime('%Y-%m-%d')
            region_code = row[2]
            test_count = row[16]

            current_values = regions.get(region_code, [])
            current_values.append(test_count)
            regions[region_code] = current_values    

for key in regions:
    test_counts = regions[key]

    if key != "04":
        index = len(test_counts) - 1
        while index > 0:
            test_counts[index] = str(int(test_counts[index]) - int(test_counts[index - 1]))
            if int(test_counts[index]) < 0 and index < len(test_counts) - 1:
                test_counts[index] = test_counts[index + 1]
            index -= 1

    test_counts = [int(numeric_string) for numeric_string in test_counts]
    regions[key] = test_counts

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
            region_code = row[2]

            region_tests = regions[region_code]
            region_tests_day = region_tests[i]
            if region_tests_day == 0:
                index = i
                while index < len(region_tests) and region_tests_day == 0:
                    region_tests_day = region_tests[index]
                    index += 1

            max_region_tests = max(region_tests)

            normalized_cases = int(float(cases) / float(region_tests_day) * float(max_region_tests))

            if cases.isnumeric() and "aggiornamento" not in location:
                lines.append("{},{},{},{},{},{},{},{}".format(date_str,location,fips,cases,deaths,region_tests_day,max_region_tests,normalized_cases))

lines.insert(0, "date,state,fips,cases,deaths,tests,max_tests,normalized_cases")

with open('/tmp/joined.csv', 'w') as f:
    for line in lines:
        f.write("%s\n" % line)
