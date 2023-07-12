import boto3
import json
import os
from botocore.exceptions import BotoCoreError, ClientError

# Obtain bucket name from environment variable
bucket_name = os.getenv('BUCKET_NAME')

def lambda_handler(event, context):
    try:
        # Initialize boto3 clients
        ec2 = boto3.client('ec2')
        s3 = boto3.client('s3')

        # Collect metrics
        volumes_response = ec2.describe_volumes(
            Filters=[
                {'Name': 'status', 'Values': ['available']},
                {'Name': 'encrypted', 'Values': ['false']}
            ]
        )

        snapshots_response = ec2.describe_snapshots(
            OwnerIds=['self'],
            Filters=[{'Name': 'encrypted', 'Values': ['false']}]
        )

        metrics = {
            'volumes': [],
            'snapshots': [],
        }

        for volume in volumes_response['Volumes']:
            metrics['volumes'].append({
                'VolumeId': volume['VolumeId'],
                'Size': volume['Size'],
                'State': volume['State'],
                'Encrypted': volume['Encrypted']
            })

        for snapshot in snapshots_response['Snapshots']:
            metrics['snapshots'].append({
                'SnapshotId': snapshot['SnapshotId'],
                'VolumeSize': snapshot['VolumeSize'],
                'Encrypted': snapshot['Encrypted']
            })

        # Write metrics to S3
        s3.put_object(
            Body=json.dumps(metrics),
            Bucket=bucket_name,
            Key='your_file_name.json'
        )

        return {
            'statusCode': 200,
            'body': json.dumps('Metrics successfully written to S3')
        }

    except ClientError as e:
        print("Unexpected error: %s" % e)
        return {
            'statusCode': 500,
            'body': json.dumps('Error while collecting metrics')
        }
