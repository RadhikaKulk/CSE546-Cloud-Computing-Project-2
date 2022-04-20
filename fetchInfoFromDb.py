import json
import boto3
import time

dynamoDbClient = boto3.client('dynamodb')
sqsClient = boto3.client('sqs')
outputQueueUrl = sqsClient.get_queue_url(QueueName = 'Output.fifo', QueueOwnerAWSAccountId = '900633973354')

def getDeduplicationId(result):
  timestamp = str(time.time()).split('.')[0]
  messageDeduplicationId = (result.split(", ")[0]).split(" ")[0] + str(timestamp)
  return messageDeduplicationId

def lambda_handler(event, context):
  key = event["Records"][0]["body"]
  
  row = dynamoDbClient.get_item(
    TableName = 'student-academic-info',
    Key = {
        'name': {'S': key}
    })
  
  result = ""
  if "Item" not in row:
    result = "Not Found"
  else:
    result = row["Item"]["name"]["S"] + ", " + row["Item"]["major"]["S"] + ", " + row["Item"]["year"]["S"]

  messageDeduplicationId = getDeduplicationId(result)
  res = sqsClient.send_message(
    QueueUrl = outputQueueUrl["QueueUrl"],
    MessageBody = result,
    MessageGroupId = "results",
    MessageDeduplicationId = messageDeduplicationId)
  
  return res