from __future__ import print_function
import ast
import boto3
import json
import os
import re

def EXTINF(imdb_id):
    key = "{}/omdb.json".format(imdb_id)
    body = json.loads(
        boto3.client('s3').get_object(Bucket=os.environ["MOVIES_BUCKET"], Key=key)["Body"].read()
    )

    return "{},{}".format(
      int(re.sub("[^0-9]", "", body["Runtime"])) * 60,
      body["Title"],
    )

def strm(imdb_id):
    extinf = "#EXTINF:{}".format(EXTINF(imdb_id))
    url = "https://{}/movie/{}/stream|User-Agent={}".format(
        os.environ["API_GATEWAY_DOMAIN"],
        imdb_id,
        os.environ["API_KEY"],
    )

    body = "\n".join([extinf, url])
    key = '{}/kodi.strm'.format(imdb_id)
    s3 = boto3.resource('s3')
    s3.Bucket(os.environ["MOVIES_BUCKET"]).put_object(Key=key, Body=body, ACL="private")

def lambda_handler(event, context):
    for record in event["Records"]:
        for y in ast.literal_eval(record["Sns"]["Message"])["Records"]:
            key = y["s3"]["object"]["key"]
            imdb_id = key.split("/")[0]
            print("generating strm for {}".format(imdb_id))
            strm(imdb_id)

    return True

if __name__ == "__main__":
    with open('sample_event/tt0000000.json', 'r') as myfile:
        sample_event_json=myfile.read()
    event = json.loads(sample_event_json)
    lambda_handler(event, {})
    s3 = boto3.client('s3')
    print("\nThe Document is:\n")
    print(
        s3.get_object(Bucket=os.environ["MOVIES_BUCKET"], Key="tt0000000/kodi.strm")["Body"].read()
    )
