
import json
import boto3
import requests

lambda_client = boto3.client('lambda')

def get_prefix(url):
    prefix = ""
    if (url == 'https://google.com'):
        prefix = "google"
    elif (url == 'https://stackoverflow.com/'):
        prefix = "stackoverflow"
    elif (url == 'https://www.linkedin.com/'):
        prefix = 'linkedin'
    return prefix

def lambda_handler(event, context):
    full_json = lambda_client.get_function_configuration(
        FunctionName="lambda-nectar-checker"
    )
    variables_json = full_json['Environment']['Variables']
    for url in json.loads(variables_json['URLs']):
        try:
            r = requests.get(url, timeout=(int(variables_json['TimeOutMilliseconds']) / 1))
            prefix = get_prefix(url)
            count = int(variables_json[prefix])
            
            if r.status_code < 200 or r.status_code >= 299:
                print('@Unhealthy!', r.status_code, r.reason)
                date = f"Has Unhealthy Status.\n Code:{r.status_code}\n Status: {r.reason}"
                if(count >= 3):
                    send_mail(date,url)
                    count = 0
                else:
                    count = count + 1
                variables_json.update({prefix:str(count)})
            else:  
                count = 0
                variables_json.update({prefix:str(count)})
                print('@Healthy!', r.status_code, r.reason)
        except Exception as err:
            date = f"Lambda Exception: {err}"
            print(date)
            if(count >= 3):
                send_mail(date,url)
                count = 0
            else:
                count = count + 1
            variables_json.update({prefix:str(count)})
    lambda_client.update_function_configuration(
        FunctionName="lambda-nectar-checker",
        Environment={"Variables":variables_json}
    )

def send_mail(date, url):
    print("####SENT_MAIL####")
    response = boto3.client('sns').publish(
        TopicArn='arn:aws:sns:us-east-1:XXXXXX:sns-lambda-checker',
        Message=f"Site: {url} ;\n\n{date}",
        Subject='Lambda Nectar Checker Alarm'
    )

