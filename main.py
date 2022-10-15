# Code by Steve Hou in 2022
# DO NOT use the code for other purposes except generating ics file.

import http.cookiejar
import requests
import urllib
import re
import time
import uuid
import json
from datetime import date


# Get one day timetable html
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


# Get a student's all timetable, valid until year 2100.
# Hopefully I will update it then.
def get_all_timetable(username, password):
    url = 'https://timetables.liverpool.ac.uk/services/get-events?start=2010-01-01&end=2100-12-31'

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
    lecturer_list = []

    html_json_load = (json.loads(html))

    for one_class in html_json_load:
        try:
            title_list.append(one_class['activitydesc'])
            start_list.append(make_dttime(one_class['start']))
            end_list.append(make_dttime(one_class['end']))
            location_list.append(one_class['locationdesc'])

            try:
                lecturer_info_json = one_class['staffs']
                lecturer_info_formatted = 'Lecturer: ' + lecturer_info_json[0]['FullName'] + '=0D=0AEmail: ' + \
                                          lecturer_info_json[
                                              0]['Email'] + '=0D=0APhone number:' + lecturer_info_json[0]['PhoneNumber']
                lecturer_list.append(lecturer_info_formatted)
            except IndexError:
                lecturer_list.append('')
        except Exception:
            print(
                'An error occurred on one class. The class might near ' + str(
                    start_list[-1]) + ' . Check it with you timetable.')
            continue

    list_list = [title_list, start_list, end_list, location_list, lecturer_list]
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
    for lecturer_i in range(0, module_num):
        list_list[4][lecturer_i] = 'DESCRIPTION;ENCODING=QUOTED-PRINTABLE:' + list_list[4][lecturer_i]

    return list_list


def request_user_info():
    print('This program need your account username and password to run.')
    username = input('Please input your UoL account username : ')
    password = input('Please input your UoL account password : ')

    if get_all_timetable(username, password) == 'password error':
        print('Your username or password is incorrect.')
        return request_user_info()

    info_list = [username, password]
    return info_list


def write_ics(username, password):
    with open('timetable.ics', 'w') as ics:
        head = 'BEGIN:VCALENDAR\nPRODID:Calendar-//Steve Hou//auto-generate-ics//EN\nVERSION:1.0\n'
        ics.write(head)

    info_list = request_user_info()
    username = info_list[0]
    password = info_list[1]

    print('Connecting to university server...')
    if get_all_timetable(username, password) == 'password error':
        print('Your username or password is incorrect.')
        write_ics(username, password)
    else:
        print('Connection success. Starting generate ics file. \nIt may take few seconds.')

        try:
            html = get_all_timetable(username, password)
            list_list = format_ics(extract_information(html))
            module_num = len(list_list[0])
            for i in range(0, module_num):
                with open('timetable.ics', 'a') as ics:
                    ics.write('BEGIN:VEVENT\n')
                    ics.write('CLASS:PUBLIC\n')
                    ics.write('DESCRIPTION:\n')
                    ics.write('DTSTAMP;VALUE=DATE-TIME:20220201T111819\n')
                    ics.write('UID:' + str(uuid.uuid1()) + '\n')
                for list in list_list:
                    with open('timetable.ics', 'a') as ics:
                        ics.write(list[i] + '\n')
                with open('timetable.ics', 'a') as ics:
                    ics.write('TRANSP:TRANSPARENT\n')
                    ics.write('END:VEVENT\n')
        except Exception as e:
            print()
            print('*************************************************************************')
            print('**********   An error occurs. Auto rebooting the progress...   **********')
            print('*************************************************************************')
            print()
            write_ics(username, password)

    with open('timetable.ics', 'a') as ics:
        ics.write('END:VCALENDAR')


def main():
    write_ics('', '')
    print('Finished. Please find your timetable file named "timetable.ics".')


if __name__ == '__main__':
    main()
