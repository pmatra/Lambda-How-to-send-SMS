# Lamda-Send SMS messages

Read https://mkdev.me/posts/how-to-send-sms-messages-with-aws-lambda-sns-and-python-3

Clipped from: https://mkdev.me/posts/how-to-send-sms-messages-with-aws-lambda-sns-and-python-3 



AUTHOR: PHILIP KIELY  

Philip Kiely is a programmer, writer, and entrepreneur from the United States. He mostly works in web development.  


Introduction 

This article discusses how to send and receive SMS with AWS. We will start by building a message logger, which will receive messages and record their sender and contents. Then, we will create a message echo application, which will reply to any message with the same text. Finally, we will schedule a daily message to a specified phone number. We will be using SMS with a variety of AWS services. Please note that in this article we do only "ClickOps:" we interact with these services through their web interfaces. Actual production applications would manage the code and services using version control, continuous integration/continuous delivery, and infrastructure as code like Terraform or AWS CloudFormation. However, the interactive AWS console will be sufficient to practice using these services. 

Amazon Web Services (AWS) offers Lambda, a serverless computing environment that lets programmers run discrete functions without provisioning a server. Writing and deploying an AWS Lambda function is a quick process and they don't need the same maintenance as an application running on a virtual server like EC2. Lambda functions are cheap; Amazon usually charges 20 cents per million requests (every time the function executes counts as a request) with the first million requests per month free for all customers indefinitely. AWS offers a variety of methods for launching these cheap, easy functions, and this article explains how to use AWS Lambda to send and receive SMS Messages. 

SMS (Short Message Service) is a decades-old protocol used by billions of mobile devices worldwide. It has some attributes that are strange compared to internet protocols. The biggest is that there is a region code associated with every phone number. This article uses AWS services in the United States and uses a United States phone number with the +1 region code. This legacy infrastructure also means that unlike AWS Lambda, using SMS is fairly expensive. After a handful of free messages, it costs $0.0075 to receive an SMS and $0.00645 to send an SMS. While the free tier will provide enough messages to test the functions in this article, it is important to consider if SMS is right for your production application given the cost. For example, an application that sends just one SMS to 1000 users every day would need to pay almost $200 per month in SMS costs alone. 

Receiving SMS 

First, you'll need an AWS account. This account will give you access to all AWS services as well as the free tier, which lets you test most products and even run small applications for cheap or free. Once you're in your AWS account, navigate to Lambda and create a new function. 

Create a Lambda Function
The function name can be whatever is meaningful to you. For the runtime, select Python 3.7, the most recent stable release of Python 3. AWS operates all of its services using role-based permissions, a system outside the scope of this article (though we will revisit it briefly later). For this function, select the "Create a new role with basic Lambda permissions" and AWS will take care of it for you. Once you have configured the settings, click "Create Function". This will bring you to the function editing page. 

Design a Lambda Function
This window has a few important buttons at the top. Most importantly, "Save" lets you save any changes to the Lambda function, while "Test" lets you write and execute tests for your function. Changes to your function will not be live until you save them using the "Save" button. 

The AWS Lambda function designer panel lets you select which services can trigger the function and which services the function can access while running. We're going to use SNS (Simple Notification Service) and CloudWatch Events as triggers with Amazon Pinpoint and Amazon CloudWatch Logs during execution. To add a service to a function, just click on it in the list to the left of the designer. Start by adding SNS as a trigger. You will have to allow SNS on the Lambda execution role (AWS will prompt you for this), then save your function. Reload the page, then scroll down to see the function code. 

Code a Lambda Function
AWS offers an online development environment for programming Lambda functions. You can import libraries and write your own methods. However, the lambda_handler() function is what actually runs when the Lambda function is triggered. This main method takes event and context as parameters. event is a large dictionary that the function can access, while context stores, well, context about the execution. We will only need to reference event. Our first function will be incredibly basic: it just takes the phone number and the text of a given message and writes it to your CloudWatch logs. 

import json 
 
 <code>
def lambda_handler(event, context): 
    message = json.loads(event['Records'][0]['Sns']['Message']) 
    words = message['messageBody'] 
    number = message['originationNumber'] 
    return { 
        'statusCode': 200, 
        'body': json.dumps("Phone number: {}\nMessage Text: {}".format(number, words)) 
    } 
 
</code>
message is a dictionary that we load from event. We extract the message body, which is the actual text of the message, and the origination number, which is the number that sent the SMS. For now, we are just dumping this information to CloudWatch. To test this, we can to send an SMS to a number associated with the function. For that, we'll need to activate AWS Pinpoint. If you want to skip this part, I'll explain how to test this function using Lambda's built-in testing mechanism, but pinpoint will be necessary later for sending messages. 

Create a Pinpoint Project
After activating your first pinpoint project, click "Manage" under "SMS and Voice" on the settings screen. 

Set up a Pinpoint Project
Get a long code
Then, request a long code. This is a dedicated phone number for your project. These cost one dollar per month, so be sure to get rid of this project once you're done testing it. Set the target country to your preferred location and the default call type to "Promotional." Once you have a phone number, you'll need to add Pinpoint to the IAM role associated with the lambda function by adding the following permission to the role in the IAM console. 

Pinpoint permissions
Now, you should be able to send text messages to your lambda function. However, you can instead simulate this using Lambda's test feature. Select "Amazon SNS Topic Notification" as the template and name the event whatever you would like. Paste the following string as the value associated with the Message key as shown in the image. 

Configure a test event
<code>
"{\"originationNumber\": \"+19997771111\",\"messageBody\": \"This is the test message\",\"inboundMessageId\": \"EXAMPLE\",\"previousPublishedMessageId\": \"EXAMPLE\",\"messageKeyword\": \"keyword_example\",\"destinationNumber\": \"+10120120123\"}" 
</code> 

Remember that event is just a dictionary, which is why we can test the Lambda function by creating our own event. After saving the test, press the "Test" button in the upper right corner of the screen to execute the Lambda function. Once execution succeeds, the console will show you what the function returned. 

Sending SMS 

Now that we can receive SMS, we turn our attention to sending them. Unlike receiving, this step does require the earlier setup of AWS Pinpoint to test. To demonstrate SMS sending and receiving, we will set up a simple echo service: you send a message it responds with the same text. 

<code>
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
 
</code>
Importing boto3 lets us initialize a pinpoint object to send messages. The message will be sent from the long code number you set up earlier. The only configuration this requires is pasting in your pinpoint application's ID. 

We can use this system to build a chat bot by SMS, for example, a virtual customer support line (although web-based chat is orders of magnitude cheaper at scale). Another application of this system is sending scheduled text messages. By changing the trigger from SMS to CloudWatch events, we can create an application to message your boss every morning with an excuse for being late. Click on the "CloudWatch Events" option on the left menu and configure the settings as shown. 

Configure a test event
import json 
import boto3 
import random 
 
 
pinpoint = boto3.client('pinpoint') 
 
 
def lambda_handler(event, context): 
    messages = ['Sorry! I\'m stuck in traffic.', 
                'Be there in a bit, I had car trouble this morning', 
                'My son was sick this morning', 
                'I stayed up too late working on the contract last night'] 
    pinpoint.send_messages( 
        ApplicationId='YOUR_PINPOINT_APPLICATION_ID', 
        MessageRequest={ 
            'Addresses': { 
                'BOSS_PHONE_NUMBER': {'ChannelType': 'SMS'} 
            }, 
            'MessageConfiguration': { 
                'SMSMessage': { 
                    'Body': random.choice(messages), 
                    'MessageType': 'PROMOTIONAL' 
                } 
            } 
        } 
    ) 
 

Coming up with better excuses and setting the AWS Pinpoint number as your contact number in your boss's phone are both left as exercises to the reader. I of course cannot endorse actually using this application. 

Now you know how to send and receive SMS using AWS Lambda. AWS Lambda functions are powerful and versatile; you can do quite a bit besides text messaging. For applications that need it, SMS is easy to set up and use, but the cost and message latency may be prohibitive for many applications. However, for some systems like phone number verification, it is the best choice, and SMS is already integrated with voice assistants like Siri and Alexa. If an SMS integration is what you want to give your users a premium experience, then AWS Lambda is a great way to add it to your project. 

To review, we used: 

Lambda for serverless functions, 

SNS for receiving notifications and SMS, 

Pinpoint for sending SMS and provisioning a fixed phone number, 

IAM for managing access and permissions, and 

CloudWatch for monitoring, logging, and triggering processes. 