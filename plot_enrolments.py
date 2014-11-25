#!/usr/bin/env python

'''
A program to plot a graph of student enrolments over a period of
time, based on data downloaded from the University of Melbourne LMS system.

The LMS allows you to download a history of student enrolments as a CSV file.
Rows in the file have the format:

    DATE,STUDENT_NAME,STUDENT_NUMBER,STUDENT_USERNAME,ACTION

Dates are in the format:

    21-Sep-2014 21:47

Actions are one of:
    - Removed
    - Added

The rows of the file are in reverse chronological order: the most
recent event is on the first line, the oldest event is on the last line.

The count of students enrolled is incremented when a student is added, and
decremented when a student is removed.

The program accepts an "epoch" date as one of its command line arguments. This
specifies a certain date (such as the start of semester) against which all
other dates are compared. Dates are plotted on the x-axis as offsets in
days from the epoch. Days before the epoch are negative and days after
the epoch are positive.

usage: plot_enrolments.py [-h] --epoch EPOCH [--output OUTPUT] [--title TITLE]
                          [--low LOW] [--high HIGH]
                          csv_filename

Plot a graph of student enrolments given CSV file downloaded from the LMS

positional arguments:
  csv_filename     CSV file downloaded from the LMS

optional arguments:
  -h, --help       show this help message and exit
  --epoch EPOCH    Date from which all other days are compared, eg start of
                   semester, such as 28-JUL-2014
  --output OUTPUT  Name of output file for graph in PNG format, must end in
                   .png
  --title TITLE    Title text for output graph
  --low LOW        Lower bound of days before epoch to start counting
  --high HIGH      Upper bound of days before epoch to end counting

Example:

plot_enrolments.py --epoch '28-JUL-2014' --title "MySubject Semester 2 2014" \
                --output enrolments.png --low 28 enrolments.csv 

In the example above, the semester starts on 28-JUL-2014, which is given
as the "epoch". The title of the graph will be "MySubject Semester 2 2014".
The output file will be written to "enrolments.png". The graph will be
cut off at the lower end 28 days before the epoch.
'''

import matplotlib.pyplot as plt
import csv
from argparse import ArgumentParser
import time
from collections import namedtuple

DESCRIPTION = 'Plot a graph of student enrolments given CSV file downloaded from the LMS'
DATE_FORMAT = '%d-%b-%Y %H:%M'
DEFAULT_OUTPUT_FILE = 'enrolments.png'
DEFAULT_TITLE = 'Student enrolments over time'
DEFAULT_LOW_BOUND = 50
DEFAULT_HIGH_BOUND = 100
SECONDS_PER_DAY = 60 * 60 * 24
LAST_MINUTE_OF_DAY = '23:59'

Record = namedtuple('Record', ['time', 'action'])

def parse_args():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--epoch', type=str, required=True,
        help='Date from which all other days are compared, eg start of semester, such as 28-JUL-2014'),
    parser.add_argument('--output', type=str, default=DEFAULT_OUTPUT_FILE,
        help='Name of output file for graph in PNG format, must end in .png'),
    parser.add_argument('--title', type=str, default=DEFAULT_TITLE,
        help='Title text for output graph'),
    parser.add_argument('--low', type=int, default=DEFAULT_LOW_BOUND,
        help='Lower bound of days before epoch to start counting')
    parser.add_argument('--high', type=int, default=DEFAULT_HIGH_BOUND,
        help='Upper bound of days before epoch to end counting')
    parser.add_argument('csv_filename', type=str, 
        help='CSV file downloaded from the LMS')
    return parser.parse_args()

def plot_data(days, num_students, title, output_filename):
    plt.ylabel("number of enrolled students")
    plt.xlabel("day")
    plt.title(title)
    plt.plot(days, num_students)
    plt.savefig(output_filename)
    plt.close()

def parse_date_time(date_time_str):
    return time.mktime(time.strptime(date_time_str, DATE_FORMAT))

def days_difference(time_recent, time_older):
    '''Most recent time is specified first'''
    return int((time_recent - time_older) / SECONDS_PER_DAY)

def main():
    args = parse_args()
    records = []
    with open(args.csv_filename) as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if len(row) == 6:
                time_of_event_str, action = row[0], row[-1]
                time_of_event = parse_date_time(time_of_event_str)
                record = Record(time=time_of_event, action=action)
            records.append(record)

    if records:
        # The CSV file is in reverse temporal order (youngest date on first line).
        # We reverse them to put them in normal temporal order.
        records = list(reversed(records))
        num_students = 0
        histogram = {}
        epoch = parse_date_time(args.epoch.strip() + ' ' + LAST_MINUTE_OF_DAY)
        for record in records:
            #day = int((record.time - epoch) / SECONDS_PER_DAY)
            day = days_difference(record.time, epoch)
            if record.action == 'Added':
                num_students += 1
            elif record.action == 'Removed':
                num_students -= 1
            else:
                print("Unrecogonised action, skipping record: {}".format(record))
            histogram[day] = num_students
        days, num_students = [], []
        for day, num in sorted(histogram.items()):
            if -args.low <= day <= args.high:
                # Only plot days within the specified bounds.
                days.append(day)
                num_students.append(num)
        plot_data(days, num_students, args.title, args.output)
        max_num_students = max(num_students)
        current_num_students = num_students[-1]
        print("Maximum enrolled students = {}".format(max_num_students))
        print("Current enrolled students = {}".format(current_num_students))

if __name__ == '__main__':
    main()