import boto3
import itertools
import json
import os
from dynamodb_json import json_util as dynamodb_json
from logging import getLogger

LOG = getLogger(__name__)


class CreateUpdateAndDeleteAspectScore(object):

    def __init__(self, table_name):
        self.dynamodb = None
        self.tableName = table_name
        self.createDynamodbClient()

    def createDynamodbClient(self):
        self.dynamodb = boto3.client('dynamodb', region_name="ap-southeast-1")
        return self.dynamodb

    def createTable(self, table_name):
        try:
            response = self.dynamodb.describe_table(TableName=table_name)
        except self.dynamodb.exceptions.ResourceNotFoundException:
            response = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'hotel_id',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'aspect',
                        'KeyType': 'RANGE'  # Sort key
                    },
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'hotel_id',
                        'AttributeType': 'N'
                    },
                    {
                        'AttributeName': 'aspect',
                        'AttributeType': 'S'
                    }
                ],
                LocalSecondaryIndexes=[
                    {
                        'IndexName': 'PostsByDate',
                        'KeySchema': [
                            {
                                'AttributeName': 'hotel_id',
                                'KeyType': 'HASH'  # Partition key
                            },
                            {
                                'AttributeName': 'aspect',
                                'KeyType': 'RANGE'  # Sort key
                            },
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 50,
                    'WriteCapacityUnits': 50,
                }
            )
        return response

    def upSertScore(self, item):
        item = json.loads(dynamodb_json.dumps(item))
        try:
            response = self.dynamodb.update_item(
                TableName=self.tableName,
                Key={
                    'hotel_id': item['hotel_id'],
                    'aspect': item['aspect']
                },
                UpdateExpression="set score = :score",
                ExpressionAttributeValues={
                    ':score': item['score']
                }
            )
        except Exception as e:
            LOG.error("Error updating/inserting Scores table : " + str(e))
            raise Exception(str(e))   

        return response

    def deleteScores(self, newScores):
        pe = "hotel_id, aspect, score"

        try:
            response = self.dynamodb.scan(
                TableName=self.tableName,
                ProjectionExpression=pe
            )
            self.ddbScores = dynamodb_json.loads(response['Items'])
            if len(response['Items']) > 0:
                while 'LastEvaluatedKey' in response:
                        response = self.dynamodb.scan(
                            TableName=self.tableName,
                            ProjectionExpression=pe,
                            ExclusiveStartKey=response['LastEvaluatedKey']
                        )
                        for item in response['Items']:
                            self.ddbScores.extend(dynamodb_json.loads(item))
        except Exception as e:
            LOG.error("Error scanning Scores table : " + str(e))
            raise Exception(str(e))

        new_scores = [{'hotel_id': item['hotel_id'],
                       'aspect':item['aspect']} for item in newScores]
        ddb_scores = [{'hotel_id': item['hotel_id'],
                       'aspect':item['aspect']} for item in self.ddbScores]

        removed_scores = list(itertools.filterfalse(
            lambda x: x in new_scores, ddb_scores))

        if len(removed_scores) > 0:
            for score in removed_scores:
                score = json.loads(dynamodb_json.dumps(score))
                try:
                    self.dynamodb.delete_item(
                        TableName=self.tableName,
                        Key={
                            'hotel_id': score['hotel_id'],
                            'aspect': score['aspect'],
                        },
                    )
                except Exception as e:
                    LOG.error(
                        "Error deleting scores in Scores table : " + str(e))
                    raise Exception(str(e))


_table_name = os.environ['DYNAMODB_TABLE']

_ddb_obj = CreateUpdateAndDeleteAspectScore(_table_name)
_ddb_obj.createTable(_table_name)
