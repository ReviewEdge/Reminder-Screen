#! /usr/bin/python3

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import time


# FIX/ADD:


###################################################
#         CLOUD-BASED TO-DO LIST DISPLAY          #
# This program pulls data from a specified Google #
# Sheet, then prints the data as a list to an     #
# attached OLED screen.  The program can be set   #
# to rotate through a specified amount of items,  #
# or statically show the first four items. This   #
# can be configured at the bottom of the script.  #
#                                                 #
# AUTHOR: LOGAN RICHARDSON                        #
# RELEASED: 3/17/19                               #
# CURRENT VERSION: 2.01                           #
# LATEST UPDATE: 3/23/19                          #
###################################################


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of the To-Dos sheet
SAMPLE_SPREADSHEET_ID = 'xxxxx'
SAMPLE_RANGE_NAME = 'A1:A'


def get_todo_data():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    use_value = values[len(values)-1][0]

    use_value_list = []
    counter = 0
    start_index = 0
    for c in use_value:
        counter += 1
        if c == ",":
            check_val = use_value[start_index:counter - 1]
            # change slice value to adjust when repeat items are allowed:
            if check_val not in use_value_list[:8]:
                use_value_list.append(check_val)
            start_index = counter
        elif counter == len(use_value)-1:
            use_value_list.append(use_value[start_index:])

    # Makes oldest at top, delete for oldest at bottom:
    use_value_list.reverse()

    return use_value_list


def make_screen_lines(sheet_values):
    screen_lines = []
    if sheet_values is None:
        return ["No Data Found", "", "", "", "", "", "", "",]
    else:
        for c in sheet_values:
            if c == sheet_values[0]:
                c = "»" + c
            else:
                c = "-" + c
            if len(c) > 20:
                if c[20] == " ":
                    c = c[:20] + c[21:]
            if len(c) > 20:
                screen_lines.append(c[0:20])
                if len(c) > 40:
                    screen_lines.append(c[20:37] + "...")
                else:
                    screen_lines.append(c[20:40])
            else:
                screen_lines.append(c)
    return screen_lines


def assign_screens(list_of_lines):
    screen_lines = list_of_lines
    if len(list_of_lines) > 4:
        grabfrom_indexes = []
        start_val = 0
        end_val = 4
        counter = 0
        for i in range(len(screen_lines) - 3):
            slice_poses = [start_val, end_val]
            grabfrom_indexes.append(slice_poses)
            start_val += 1
            end_val += 1
            counter += 1

    else:
        grabfrom_indexes = [[0, len(screen_lines)]]

    screen_pack_temp = []
    for i in grabfrom_indexes:
        screen = ""
        for cell in screen_lines[i[0]:i[1]]:
            if cell == screen_lines[i[1]-1]:
                screen += cell
            else:
                screen += cell + "\n"
        screen_pack_temp.append(screen)

    return screen_pack_temp


screen_pack = []




# Screen Drawing

import pprint
import requests
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
import time
from PIL import ImageFont, ImageDraw

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, rotate=0)


# Box and text rendered in portrait mode

def draw_screen(screen_display):
    with canvas(device) as draw:
        # draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((0, 0), screen_display, fill="white")




# Programs

def get_screen_update():
    print("GETTING DATA...\n")
    global screen_pack
    screen_pack = assign_screens(make_screen_lines(get_todo_data()))


def screen_rotate_all(refresh_time=60, time_on_start=3.2, time_between=2):
    t_end = time.time() + refresh_time
    get_screen_update()
    while time.time() < t_end:
        for screen in screen_pack:
            draw_screen(screen)
            if screen == screen_pack[0]:
                time.sleep(time_on_start)
            else:
                time.sleep(time_between)
    screen_rotate_all(refresh_time, time_on_start, time_between)


def screen_rotate_range(scrolls=5, refresh_time=60, time_on_start=3.2, time_between=2):
    t_end = time.time() + refresh_time
    get_screen_update()
    if len(screen_pack) < scrolls:
        scrolls = len(screen_pack)
    while time.time() < t_end:
        for screen in screen_pack[:scrolls]:
            draw_screen(screen)
            if screen == screen_pack[0]:
                time.sleep(time_on_start)
            else:
                time.sleep(time_between)
    screen_rotate_range(scrolls, refresh_time, time_on_start, time_between)


def screen_static(refresh_time=60):
    t_end = time.time() + refresh_time
    get_screen_update()
    while time.time() < t_end:
        draw_screen(screen_pack[0])
    screen_static(refresh_time)


# Runs the program:


# To rotate through all items:
#screen_rotate_all()

# To rotate through a set amount of items:
#screen_rotate_range()

# To set screen on first 4 items:
#screen_static()









