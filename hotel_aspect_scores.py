from __future__ import print_function
import json
import boto3
import io
import pandas as pd
from log import getLogger
from dynamodb_client import _ddb_obj
from aggregate_aspect_scores import AggregateAspectScores

s3 = boto3.client('s3')
LOG = getLogger(__name__)


class CalculateScore(object):
    def __init__(self, df):
        self.df = df

    def process(self):

        LOG.info("Aggregating Scores..")
        df = AggregateAspectScores(self.df).aggregateScores()

        newScores = json.loads(df.to_json(orient="records"))

        LOG.info("Loading Dynamodb scores table..")
        LOG.info("Updating/Inserting scores..")
        for item in newScores:
            _ddb_obj.upSertScore(item)

        LOG.info("Deleting scores..")
        _ddb_obj.deleteScores(newScores)

        LOG.info("Scores processed successfully..")


def lambda_handler(event, context):

    LOG.info("Received Event")

    s3_bucket_name = event['Records'][0]['s3']['bucket']['name']
    s3_object_key = event['Records'][0]['s3']['object']['key']

    obj = s3.get_object(Bucket=s3_bucket_name, Key=s3_object_key)
    df = pd.read_csv(io.BytesIO(obj['Body'].read()), sep=',')

    LOG.info("Begin calculating scores..")

    CalculateScore(df).process()
    return
