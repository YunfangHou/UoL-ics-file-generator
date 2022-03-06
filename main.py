# Code by Steve Hou in 2022
# DO NOT use the code for other purposes except generating ics file.

import http.cookiejar
from urllib.error import URLError, HTTPError
import requests
import urllib
import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys
import io


def get_one_day_timetable_html(year, month, day):
    year_str = str(year)
    if month < 10:
        month_str = '0' + str(month)
    else:
        month_str = str(month)
    if day < 10:
        day_str = '0' + str(day)
    else:
        day_str = str(day)

    # User need to use the browser tools to find his/her own identity_num and cookie
    identity_num = '1111111111'
    url = 'https://timetables.liverpool.ac.uk/services/get-events?start=' + year_str + '-' + month_str + '-' + day_str + '&end=' + year_str + '-' + month_str + '-' + day_str + '&_=' + identity_num
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15',
        'Cookie': ''
    }
    session = requests.Session()

    response = session.get(url, headers=headers)

    return response.text


def simulate_login(username, password, year, month, day):
    year_str = str(year)
    if month < 10:
        month_str = '0' + str(month)
    else:
        month_str = str(month)
    if day < 10:
        day_str = '0' + str(day)
    else:
        day_str = str(day)

    url = 'https://timetables.liverpool.ac.uk/services/get-events?start=' + year_str + '-' + month_str + '-' + day_str + '&end=' + year_str + '-' + month_str + '-' + day_str

    data = {'Username': username,
            'Password': password}
    post_data = urllib.parse.urlencode(data).encode('utf-8')

    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

    login_url = 'https://timetables.liverpool.ac.uk/account?returnUrl=%2F'

    req = urllib.request.Request(login_url, headers=headers, data=post_data)

    cookie = http.cookiejar.CookieJar()

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))

    try:
        resp = opener.open(req)
    except Exception:
        print('There might be some problem with your network.')
        print('Check you network setting and rerun the program.')
        quit()

    req = urllib.request.Request(url, headers=headers)

    resp = opener.open(req)

    result = resp.read().decode('utf-8')
    if 'Username:' in result:
        result = 'password error'

    return result


def extract_information(html):
    title_list = []
    start_list = []
    end_list = []
    location_list = []
    teacher_list = []

    match_obj = re.match('.*?"title":"(.*?)(","start":.*)', html)
    while match_obj != None:
        if len(match_obj.group(1)) != 7:
            title = re.match('.*?"activitydesc":"(.*?)(","activitytype":.*)', html)
            title_list.append(title.group(1))
        else:
            title_list.append(match_obj.group(1))
        html = match_obj.group(2)

        match_obj = re.match('.*?"start":"(.*?)(","end":.*)', html)
        start_list.append(make_dttime(match_obj.group(1)))
        html = match_obj.group(2)

        match_obj = re.match('.*?"end":"(.*?)(","eventtimetext":.*)', html)
        end_list.append(make_dttime(match_obj.group(1)))
        html = match_obj.group(2)

        match_obj = re.match('.*?"locationdesc":"(.*?)(","hovertext":.*)', html)
        if match_obj.group(1) == '':
            location_list.append('Online')
        else:
            location_list.append(match_obj.group(1))
        html = match_obj.group(2)

        match_obj = re.match('.*?"FullName":"(.*?)(",.*)', html)
        try:
            teacher_list.append(match_obj.group(1))
            html = match_obj.group(2)
        except AttributeError:
            teacher_list.append('N/A')

        match_obj = re.match('.*?"title":"(.*?)(","start":.*)', html)

    list_list = [title_list, start_list, end_list, location_list, teacher_list]
    # print(list_list)
    return list_list


def make_dttime(time):
    match_obj = re.match('(....)-(..)-(..)T(..):(..)', time)
    dttime = match_obj.group(1) + match_obj.group(2) + match_obj.group(3) + 'T' + match_obj.group(4) + match_obj.group(
        5) + '00'
    return dttime


def format_ics(list_list):
    module_num = len(list_list[0])
    for title_i in range(0, module_num):
        list_list[0][title_i] = 'SUMMARY;LANGUAGE=en-us:' + list_list[0][title_i]
    for start_i in range(0, module_num):
        list_list[1][start_i] = 'DTSTART;VALUE=DATE-TIME:' + list_list[1][start_i]
    for end_i in range(0, module_num):
        list_list[2][end_i] = 'DTEND;VALUE=DATE-TIME:' + list_list[2][end_i]
    for location_i in range(0, module_num):
        list_list[3][location_i] = 'LOCATION:' + list_list[3][location_i]
    for teacher_i in range(0, module_num):
        list_list[4][teacher_i] = 'DESCRIPTION:Teacher: ' + list_list[4][teacher_i]

    return list_list


def write_ics():
    with open('timetable.ics', 'w') as ics:
        head = 'BEGIN:VCALENDAR\nPRODID:Calendar-//Steve Hou//auto-generate-ics//EN\nVERSION:1.0\n'
        ics.write(head)

    print('This program need your account username and password to run.')
    username = input('Please input your UoL account username : ')
    password = input('Please input your UoL account password : ')

    start_year = 0
    end_year = 0
    while (not start_year):
        try:
            start_year = int(input('Please input start year : '))
        except ValueError:
            print('The content you input is not valid')
    while (not end_year):
        try:
            end_year = int(input('Please input end year : '))
        except ValueError:
            print('The content you input is not valid')

    if simulate_login(username, password, start_year, 3, 3) == 'password error':
        print('Your username or password is incorrect.')
        write_ics()
    else:
        print('Start generating ics file from ' + str(start_year) + '.01.01 to ' + str(end_year) + '.12.31.')
        if start_year == end_year:
            end_year += 1
        for year in range(start_year, end_year):
            for month in range(1, 13):
                for day in range(1, 32):
                    try:
                        progress = float(((end_year - year) * (month - 1) * 30 + day) / ((end_year - start_year) * 365))
                        print('Progress ' + str(round(progress, 6) * 100)[0:5] + ' %')
                        html = simulate_login(username, password, year, month, day)
                        list_list = format_ics(extract_information(html))
                        module_num = len(list_list[0])
                        for i in range(0, module_num):
                            with open('timetable.ics', 'a') as ics:
                                ics.write('BEGIN:VEVENT\n')
                                ics.write('CLASS:PUBLIC\n')
                                ics.write('DESCRIPTION:\n')
                                ics.write('DTSTAMP;VALUE=DATE-TIME:20220201T111819\n')
                            for list in list_list:
                                with open('timetable.ics', 'a') as ics:
                                    ics.write(list[i] + '\n')
                            with open('timetable.ics', 'a') as ics:
                                ics.write('TRANSP:TRANSPARENT\n')
                                ics.write('END:VEVENT\n')
                    except Exception as e:
                        if (e.code == 500):
                            continue
                        else:
                            print()
                            print('*************************************************************************')
                            print('**********   An error occurs. Auto rebooting the progress...   **********')
                            print('*************************************************************************')
                            print()
                            redo_write_ics(username, password, start_year, end_year)


def redo_write_ics(username, password, start_year, end_year):
    with open('timetable.ics', 'w') as ics:
        head = 'BEGIN:VCALENDAR\nPRODID:Calendar-//Steve Hou//auto-generate-ics//EN\nVERSION:1.0\n'
        ics.write(head)

    print('Start generating ics file from ' + str(start_year) + '.01.01 to ' + str(end_year) + '.12.31.')
    for year in range(start_year, end_year):
        for month in range(1, 13):
            for day in range(1, 32):
                try:
                    progress = float(((end_year - year) * (month - 1) * 30 + day) / ((end_year - start_year) * 365))
                    print('Progress ' + str(round(progress, 6) * 100)[0:5] + ' %')
                    list_list = format_ics(extract_information(simulate_login(username, password, year, month, day)))
                    module_num = len(list_list[0])
                    for i in range(0, module_num):
                        with open('timetable.ics', 'a') as ics:
                            ics.write('BEGIN:VEVENT\n')
                            ics.write('CLASS:PUBLIC\n')
                            ics.write('DESCRIPTION:\n')
                            ics.write('DTSTAMP;VALUE=DATE-TIME:20220201T111819\n')
                        for list in list_list:
                            with open('timetable.ics', 'a') as ics:
                                ics.write(list[i] + '\n')
                        with open('timetable.ics', 'a') as ics:
                            ics.write('TRANSP:TRANSPARENT\n')
                            ics.write('END:VEVENT\n')
                except Exception as e:
                    if (e.code == 500):
                        continue
                    else:
                        print()
                        redo_write_ics(username, password, start_year, end_year)


def main():
    start_time = time.perf_counter()
    write_ics()
    end_time = time.perf_counter()
    duration = end_time - start_time
    print('Progress 100.0 %')
    print('Finish. Spend ' + str(int(duration)) + ' seconds')


if __name__ == '__main__':
    main()
