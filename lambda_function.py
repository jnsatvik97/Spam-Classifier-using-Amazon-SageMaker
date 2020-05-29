import json
import boto3

import email

s3 = boto3.client('s3')

from botocore.exceptions import ClientError
ses = boto3.client('ses')

def lambda_handler(event, context):
    
    
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    print("The bucket is",bucket)
    print("The key is", key)
    
    response = s3.get_object(Bucket=bucket, Key=key)
    
    print("The response is",response)
    
    emailcontent = response['Body'].read().decode('utf-8')
    
    b = email.message_from_string(emailcontent)
    
    #print("The mail is ", b)
    
    bbb = b['from']
    ccc = b['to']
    sss = b['subject']
    ddd = b['date']
    
    print(" The incoming mail is from", bbb)
    print("The incoming mail is to", ccc)
    print("Subject of incoming mail is", sss)
    print("The date of the mail is", ddd)
    
    body_mail = ''
    
    if b.is_multipart():
        print("Mail is multi-part")
        count = 0
        for payload in b.get_payload():
            #print("Reaches here")
            #print(payload.get_payload())
            #print(type(payload.get_payload()))
            if count == 0:
                body_mail += payload.get_payload()
            count += 1
            #body_mail = payload.get_payload()
    
    else:
        print("Mail is not multi-part")
        print(b.get_payload())
        print(type(b.get_payload()))
        #body_mail = b.get_payload()
        
    
    print("Type of the mail body is", type(body_mail))
    print("The mail body is ", body_mail)
    
    #new_body_mail = body_mail.replace('\n','')
    #new_body_mail = new_body_mail.replace('\r','')
    
    body = json.dumps(body_mail)
    
    body = body.strip('\r\n')
    #body = body.replace('\r','') 
    
    print("The type of json object being inserted is ", type(body))
    print("The json object being inserted is ", body)
    
    
    # THIS IS THE SAGEMAKER PREDICTION PART - WORKING FINE 
    
    

    endpoint_name = 'sms-spam-classifier-mxnet-2020-05-07-00-34-35-823'
    runtime = boto3.Session().client(service_name='sagemaker-runtime', region_name='us-east-2')
    
    response = runtime.invoke_endpoint(EndpointName=endpoint_name, ContentType='application/json',Body=body)
    
    # Output probability shown is corresponding to sigmoid for spam
    
    print(response)
    print(type(response))
    
    response_new = json.loads(response['Body'].read())
    
    print(response_new)
    print(type(response_new))
    
    prediction_label = response_new['predicted_label']
    print(prediction_label)
    prediction_probability = response_new['predicted_probability']
    print(prediction_probability)
    
    output_label = prediction_label[0][0]
    print(type(output_label))
    print(output_label)
    
    output_prediction = prediction_probability[0][0]
    print(type(output_prediction))
    print(output_prediction)
    
    mail_label = None
    
    if output_label == 0.0:
        mail_label = 'Ham'
        
    else:
        mail_label = 'Spam'
        
    mail_confidence = None
    
    if output_prediction < 0.5:
        mail_confidence = str((1 - output_prediction)*100)
        
    else:
        mail_confidence = str((output_prediction)*100)
        
    
    print("The output label is", mail_label)
    print("The confidence is", mail_confidence)
    
    
    
    #email_from = 'satvikjain@kartikparnami.com'
    email_from = ccc
    #email_to = 'sj2995@columbia.edu'
    email_to = bbb
    email_subject = sss
    #print(type(email_subject))
    email_date = ddd
    
    
    
    email_body = """We received your email sent at """ + ddd + """ with the subject """ + email_subject + """
    
Here is a sample of the mail body:
    
    
""" + body_mail + """



The email was classified as """ + mail_label + """  with """ + mail_confidence + """ confidence."""


    print(email_body)
    
    
    
    
    
    # THIS IS THE EMAIL SENDING PART
    
    #email_from = 'satvikjain@kartikparnami.com'
    #email_to = 'sj2995@columbia.edu'
    #email_subject = 'Test subject'
    
    #email_body = 'Hello how are you?'
    
    
    response = ses.send_email(
        Source = email_from,
        Destination={
            'ToAddresses': [
                email_to,
            ],
        },
        Message={
            'Subject': {
                'Data': email_subject
            },
            'Body': {
                'Text': {
                    'Data': email_body
                }
            }
        }
    )
    
    '''
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    '''