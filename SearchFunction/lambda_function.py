import boto3
import requests
from requests_aws4auth import AWS4Auth
import base64
import urllib.parse
import json

region = 'us-east-2'
service = 'es'

credentials = boto3.Session().get_credentials()

awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token
)

host = 'https://vpc-project2-search-pp5hmyb6p57g5ar4ilpm4djrwy.us-east-2.es.amazonaws.com'
index = 'documents'
url = host + '/' + index + '/_search'


def get_from_Search(query):

    headers = {"Content-Type": "application/json"}

    r = requests.get(
        url,
        auth=awsauth,
        headers=headers,
        data=json.dumps(query)
    )

    print("OpenSearch response:", r.text)

    return r.text


def lambda_handler(event, context):

    try:

        print("Event is", event)

        #
        # Handle API Gateway body correctly
        #
        if event.get('isBase64Encoded', False):
            body_data = base64.b64decode(event['body']).decode('utf-8')
        else:
            body_data = event['body']

        print("Body data:", body_data)

        formDict = urllib.parse.parse_qs(body_data)

        term = formDict.get('searchTerm')

        print("Term:", term)

        if not term:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "message": "searchTerm not provided"
                })
            }

        query = {
            "size": 25,
            "query": {
                "multi_match": {
                    "query": term[0],
                    "fields": [
                        "Title",
                        "Author",
                        "Date",
                        "Body"
                    ]
                }
            },
            "fields": [
                "Title",
                "Author",
                "Date",
                "Summary"
            ]
        }

        print("Sending query to OpenSearch")

        response_text = get_from_Search(query)

        response_json = json.loads(response_text)

        final_response = response_json["hits"]["hits"]

        print("Final response:", json.dumps(final_response))

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(final_response)
        }

    except Exception as e:

        print("Exception is", str(e))

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "status": False,
                "message": str(e)
            })
        }