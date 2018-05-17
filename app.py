#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import json
import pygal
from pygal.style import DefaultStyle
import random
from flask import (Flask, jsonify, render_template, url_for, request)

app = Flask(__name__)
dashboard_df = pd.read_csv('static/dashboard.tsv', sep='\t', encoding='utf-8')


@app.route('/', methods=['GET'])
def index():
    """
    Route that maps to index.html
    """
    print(dashboard_df)
    total_points = dashboard_df['driving_points'].sum()
    total_drive = dashboard_df['driving'].sum()
    most_points = dashboard_df['driving_points'].max()
    most_row = dashboard_df[dashboard_df['driving_points'] == most_points]
    print(most_row)
    most_date = most_row['date'].values
    print(most_date)

    return render_template('index.html', most_date=most_date[0], most_points=most_points,
                            total_points=total_points, total_drive=total_drive)

@app.route('/friends', methods=['GET'])
def friends():
    return render_template('friends.html')

@app.route('/activitylog', methods=['GET'])
def activitylog():
    return render_template('activitylog.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Generates dashboard for week selected
    """
    graphStyle =DefaultStyle(
                  label_font_family='googlefont:Roboto Condensed',
                  label_font_size=20,
                  label_colors=('black'),
                  value_font_family='googlefont:Roboto Condensed',
                  value_font_size=15,
                  value_colors=('black'))
    weeks = dashboard_df['week'].tolist()
    weeks = list(set(weeks))
    search_term = request.args.get("week")
    print(search_term)
    print(type(search_term))
    if search_term is None:
        search_term = weeks[-1]
        results = dashboard_df[dashboard_df['week'] == search_term]
    else:
        search_term = int(search_term)
        print(search_term)
        print(type(search_term))
        results = dashboard_df[dashboard_df['week'] == int(search_term)]
        print(results)
    total_points = results['total_points'].sum()
    total_drive = results['driving'].sum()
    results['timestamp'] = pd.to_datetime(results['date'], dayfirst=True)
    week_days = results['week_day'].unique()
    week_dates = results['date'].tolist()

    #build drive chart
    drive_bar = pygal.Bar(show_legend=False, print_labels=True, print_values=True)
    drive_bar.title = 'Driving hours logged'
    drive_bar.x_title = 'Days'
    drive_bar.y_title = 'Hours'
    drive_values = results['driving'].tolist()
    values = list(zip(week_dates, drive_values,week_days))
    for item in values:
        drive_bar.add(item[0].upper() , [{'value': item[1], 'label': "{0}".format(item[2].upper())}])
    drive_chart = drive_bar.render_data_uri()

    #build points chart
    points_line = pygal.StackedLine(fill=True, legend_at_bottom=True)
    points_line.title = 'Points Distribution'
    points_line.x_labels = map(str, week_dates)
    points_line.add('Driving Points', results['driving_points'].tolist())
    chart = points_line.render_data_uri()
    return render_template('dashboard.html', weeks=weeks, selected_week=search_term, 
                            chart=chart, drive_chart=drive_chart,
                            total_drive=total_drive, total_points=total_points)




if __name__ == '__main__':
    app.run(debug=True)
