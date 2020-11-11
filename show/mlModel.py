import requests
import json


def get_spider_json(sentence):
    access_url = "https://aip.baidubce.com/oauth/2.0/token"
    try:
        access_data = {
            'grant_type': 'client_credentials',
            'client_id': 'iZ18XUkeFhCDRg2QgNskoj4Y',
            'client_secret': 'uMospclnjHxeDkpi0GgxGlcZAzTxVsWB',
        }
        response = requests.post(url=access_url, data=access_data)
        token_json = response.json()
        token = token_json['access_token']
        headers = {
            'content-type': 'application/json',
        }
        data = {
            'data': sentence
        }
        url = 'https://aip.baidubce.com/rpc/2.0/kg/v1/cognitive/entity_annotation?access_token='
        res = requests.post(url=url + token, data=json.dumps(data), headers=headers)
        return res.json()
    except:
        return json.dumps({'error_code': '1'})
