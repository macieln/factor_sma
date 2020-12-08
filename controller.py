# Module: controller.py
# Author: Nahum Maciel
# Email: nahumamaciel@gmail.com
# Date: 2020-12-03

"""
| APP |

    Manages systems/parts data & WOs(work orders) of the same. 
    It also generates various reports based on that data.


| THIS MODULE - THE CONTROLLER |

    [TERMS]

    WO - work order or orders(WOs). A task performed on equipment.

    [WO DATA MODEL]

    --------------------------------------------------------------------------------------
    | PARAMETER |   VALUE TYPE |   DESCRIPTION                                           |
    --------------------------------------------------------------------------------------

     -------------------------------------------------------------------------------------
    | id        |   int        |   Primary key for work order. This is the same as       | 
    |           |              |     vendor WO id & it is saved in first column of       |
    |           |              |     REPORT.                                             |
    --------------------------------------------------------------------------------------
    |           |              |                                                         | 
    |           |              |                                                         |
    |           |              |                                                         |
    --------------------------------------------------------------------------------------

    [DESCRIPTION]

    Main point of exection. Opens the daily WOs REPORT file & processes data, this is saved as 'REPORT.CSV' in same
    directory as app bundle.

    [OBJECTIVES]

        1. Open - daily WOs REPORT file. Should be in CSV-utf8 format with start/end dates formated to yyy/mm/dd hh:mm prior to converting to CSV-utf8.
            otherwise datetime conversion will not be correct. 
        
        2. Serialize - data from REPORT into CSV iterable object based on user prompted initial date to scrape WOs from REPORT. Else, initial scrape date 
            will be 2 days prior from execution date.

        2. Format - into dictionary var using the WO model with data serialized from report.

        3. Save - WOs dictionary in JSON in file. This will not the temporary WOs record, bu the review queue. Orders in this file will be up for review & 
            edit by technical support engineer. 
    """

import os 
import csv
from datetime import datetime
import json

def intervalConverter(intervalStr):

    if not intervalStr:
        return 0.0
    dateStr = (intervalStr.split(' ')[0]).strip()
    month = int(dateStr.split('/')[0])
    day = int(dateStr.split('/')[1])
    year = int(dateStr.split('/')[2])

    timeStr = (intervalStr.split(' ')[1]).strip()
    hrs = int(timeStr.split(':')[0])
    mins = int(timeStr.split(':')[1])

    if year <= 0 or year < 1999:
        year += 2000

    if month <= 0 or month >= 32:
        month = 1

    if day <= 0:
        day = 1

    return datetime(year, month, day, hrs, mins)

# [1] ------------------------------------------------------------------
reportFile = "REPORT.csv"
reportWOs = []
formatedWOs = []

with open(reportFile) as report:    
    reportWOs = csv.reader(report)

# [2] ------------------------------------------------------------------
    userInput = ""
    inputValidation = False
    initialDayCount = 0

    while not inputValidation:        
        userInput = input("\nEnter intial WOs scraping date in format 'YYYY-MM-DD' or leave blank to scrape 2 days before today: ")

        if not userInput:
            inputValidation = True
            initialDayCount = 15
        else:
            try:
                datetime.fromisoformat(userInput)                
            except:
                print("Incorrect input!\n")
            else:
                inputValidation = True
                initialDayCount = datetime.now() - datetime.fromisoformat(userInput)
        
        if initialDayCount < 1:
            initialDayCount = 1

        print(f"\n\nScrap Days: {initialDayCount}\n\n")
                
    header = False
    woModel = {}

    for order in reportWOs:
        if not header:
            header = True
        elif initialDayCount <= 0:
            break
        else:
            woModel = {
                "tool": order[2],
                "chamber": order[9], 
                "type": (order[10].title()).strip(), 
                "mode": order[13].strip(), 
                "root": "",
                "corrective": order[12].strip(),
                "start": intervalConverter(order[25].strip()),
                "end": intervalConverter(order[26].strip()),
                "downTime": woModel["end"] - woModel["start"],
                "delayTotal": 0.0,
                "totalTime": 0.0,
                "techs": [order[14].strip(), order[30].strip()], 
                "notes": order[21].strip(),
                "repeat": {},
                "delays": [],
                "exchanges": [],
                "uptime": False,
                "review": False
            }

            woModel["start"] = str(intervalConverter(order[25]))
            woModel["end"] = str(intervalConverter(order[26]))

            formatedWOs.append({str(order[0]): woModel})

            initialDayCount -= 1
    
    # formatedWOs = formatedWOs[1:]

#[3] ------------------------------------------------------------------
with open("reviewReport.json", "w") as reviewReport:
    reviewReport.write(json.dumps(formatedWOs, indent="     "))

# for number in range(0, 16):
#     print(  
#             f"Scrape Count: {number}", " ",
#             formatedWOs[number]["id"], " ",
#             formatedWOs[number]["tool"], " ",
#             formatedWOs[number]["chamber"], " ",
#             formatedWOs[number]["type"], " ",
#             formatedWOs[number]["mode"], " ",
#             formatedWOs[number]["root"], " ",
#             formatedWOs[number]["corrective"], " ",
#             formatedWOs[number]["start"], " ",
#             formatedWOs[number]["end"], " ",
#             formatedWOs[number]["downTime"], " ",
#             formatedWOs[number]["delayTotal"], " ",
#             formatedWOs[number]["totalTime"], " ",
#             formatedWOs[number]["techs"], " ",
#             formatedWOs[number]["notes"], " ",
#             formatedWOs[number]["repeat"], " ",
#             formatedWOs[number]["delays"], " ",
#             formatedWOs[number]["exchanges"], " \n"
#     )