# Question: if BART trains could start opening doors as they roll into a station stop and cut five second off each stop, how much time would be saved total?
# Data source: https://www.bart.gov/about/reports/ridership
# Instructions: Download the 2016 data nd upset to the ridership_2016 folder in the project directory

import openpyxl
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
# Update these lines depending on your system
os.chdir('/Users/michaelgoff/Desktop/BART')
sys.path.append(os.path.abspath("/Users/michaelgoff/Desktop/BART"))

months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
day_categories = ["Weekday OD","Saturday OD","Sunday OD"]
# days_by_month is a list of lists. The [i][j] entry tells us how many days of type j there are in month i in 2016. j = 0,1,2 are weekdays, Saturdays, Sundays
# Holidays are classified as Saturday or Sunday, depending on the schedule, as given here: https://www.bart.gov/guide/holidays
# This does not appear to be exactly right, since this holiday adjustment still doesn't give integral numbers of rides
days_by_month = [[19,6,6],[20,5,4],[23,4,4],[21,5,4],[21,4,6],[22,4,4],[20,5,6],[23,4,4],[21,4,5],[21,5,5],[21,4,5],[21,5,5]]

total_trips = {}
for month_num in range(len(months)):
    filename = "ridership_2016/Ridership_" + months[month_num] + "2016.xlsx"
    monthly_wb = openpyxl.load_workbook(filename)
    for cat_num in range(len(day_categories)):
        page = monthly_wb[day_categories[cat_num]]
        raw = [[i.value for i in j] for j in page['A2':'AU48']] # Raw speadsheet values
        # The following is a dictionary that counts trips
        daily_trip_dict = {str(raw[0][i]):
            {str(raw[j][0]):raw[j][i] for j in range(1,len(raw))}
            for i in range(1,len(raw[0]))}
        # For the first page, set up the total_trips dictionary, assuming the station names are the same for all pages
        if month_num == 0 and cat_num == 0:
            total_trips = {str(raw[0][i]):
                {str(raw[j][0]):0 for j in range(1,len(raw))}
                for i in range(1,len(raw[0]))}
        for exit_station in daily_trip_dict:
            for entry_station in daily_trip_dict[exit_station]:
                total_trips[exit_station][entry_station] += daily_trip_dict[exit_station][entry_station] * days_by_month[month_num][cat_num]
    
# A list of parents in the station tree structure, with Embarcadaro as the root
tree_root = "EM"
parents = {"RM":"EN","EN":"EP","EP":"NB","NB":"BK","BK":"AS","AS":"MA","MA":"19","19":"12","12":"OW","LM":"OW","FV":"LM","CL":"FV","SL":"CL",
    "BF":"SL","HY":"BF","SH":"HY","UC":"SH","FM":"UC","CN":"PH","PH":"WC","WC":"LF","LF":"OR","OR":"RR","RR":"MA","OW":"EM","EM":"","MT":"EM",
    "PL":"MT","CC":"PL","16":"CC","24":"16","GP":"24","BP":"GP","DC":"BP","CM":"DC","CV":"BF","ED":"WD","NC":"CN","WP":"NC","SS":"CM",
    "SB":"SS","SO":"SB","MB":"SB","WD":"CV","OA":"CL","WS":"FM"}
def get_root_path(station):
    path = []
    cur_node = station
    iterations = 0
    while len(cur_node) > 0:
        path.append(cur_node)
        cur_node = parents[cur_node]
        iterations += 1
    if iterations > 100:
        print "Error in tree structure: infinite recursion"
        return []
    return path
def get_distance(s1,s2): # Get the number of stops between stations s1 and s2
    p1 = get_root_path(s1)
    p2 = get_root_path(s2)
    distance = len(p1)+len(p2)
    for i in range(min(len(p1),len(p2))):
        if p1[-1-i] == p2[-1-i]:
            distance -= 2
    return distance
    
passenger_stops = 0
for exit_station in total_trips:
    for entry_station in total_trips[exit_station]:
        passenger_stops += total_trips[exit_station][entry_station] * get_distance(exit_station,entry_station)
        
hours_saved = passenger_stops / 720 # Assuming five seconds could be shaved off every stop
# Wage data: http://www.governing.com/gov-data/economy-finance/salaries-wages-by-job-type-industry-for-metro-areas.html
# The following figure estimates wages by assuming 2000 working hours per year
# The wage data is from 2013 figures, so a bit too low, but on the other hand BART riders might earn less than the average worker
value_per_hour = 67410/2000.

print "The value of saving 5 seconds for every stop on BART is estimated to be $" + str(int(hours_saved*value_per_hour)) + " per year."