import json
import os
import datetime


def creation_status():
    return {"status": "success"}

def date_time_now():
    date, time = str(datetime.datetime.now()).split()
    return date, time

def calculate_invoice(price, server_uptime):
        weekly_price = price / 4
        daily_price = weekly_price / 7
        hour_price = daily_price / 24
        minute_price = hour_price / 60
        total_price = minute_price * server_uptime
        return '{:.20f}'.format(total_price)


def args_in_form(args, request_form):
    for arg in args:
        if not arg in request_form:
            return False
    return True

