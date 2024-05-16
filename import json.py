import json


def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    words = message['messageBody']
    number = message['originationNumber']
    return {
        'statusCode': 200,
        'body': json.dumps("Phone number: {}\nMessage Text: {}".format(number, words))
    }