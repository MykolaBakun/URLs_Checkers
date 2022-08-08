
import json
import os
import boto3
import requests

urls = json.loads(os.environ['URLs'])
time = int(os.environ['TimeOutMilliseconds']) / 1000 

def lambda_handler(event, context):
    for url in urls:
        try:
            r = requests.get(url, timeout=time)
            if r.status_code < 200 or r.status_code >= 299:
                print('@Unhealthy!', r.status_code, r.reason)
                date = f"Has Unhealthy Status.\n Code:{r.status_code}\n Status: {r.reason}"
                send_mail(r,url)
            else:  
                print('@Healthy!', r.status_code, r.reason)
        except Exception as err:
            date = f"Lambda Exception: {err}"
            print(date)
            send_mail(date,url)

def send_mail(date, url):
    print("####SENT_MAIL####")
    response = boto3.client('sns').publish(
        TopicArn='arn:aws:sns:us-east-1:XXXXXXXXXX:sns-lambda-checker',
        Message=f"Site: {url} ;\n\n{date}",
        Subject='Lambda Nectar Checker Alarm'
    )