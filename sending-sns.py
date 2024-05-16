import json
import boto3


pinpoint = boto3.client('pinpoint')


def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    pinpoint.send_messages(
        ApplicationId='YOUR_PINPOINT_APPLICATION_ID',
        MessageRequest={
            'Addresses': {
                message['originationNumber']: {'ChannelType': 'SMS'}
            },
            'MessageConfiguration': {
                'SMSMessage': {
                    'Body': message['messageBody'],
                    'MessageType': 'PROMOTIONAL'
                }
            }
        }
    )