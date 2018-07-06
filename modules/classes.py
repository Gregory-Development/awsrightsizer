import csv
import boto3
from datetime import datetime
from datetime import timedelta
from botocore.exceptions import ClientError
from rightsizer import args
from . import logger


class Main:
    def __init__(
            self,
            accessKey=args.accessKey,
            secretKey=args.secretKey,
            region=args.region,
            profile=args.profile,
            thresholdAvg=args.threshold[0],
            thresholdMax=args.threshold[1],
            queryDays=args.query[0],
            queryPeriod=args.query[1],
    ):
        self.accessKey = accessKey
        self.secretKey = secretKey
        self.region = region
        self.profile = profile
        self.threasholdAvg = thresholdAvg
        self.threasholdMax = thresholdMax
        self.queryDays = queryDays
        self.queryPeriod = queryPeriod

    def serializedatetime(self, t):
        if isinstance(t, datetime):
            return t.__str__()

    def initconnection(self, service):
        try:
            s = boto3.Session(
                aws_access_key_id=f'{self.accessKey}',
                aws_secret_access_key=f'{self.secretKey}',
                region_name=f'{self.region}',
            )
            c = s.client(f'{service}')
            return c
        except ClientError as e:
            logger.error(f'Error Connecting with the provided credentials. {e}')
            return []
        except:
            logger.exception(f'General Exception')
            return []

    def initprofile(self, service):
        try:
            s = boto3.Session(
                profile_name=f'{self.profile}'
            )
            c = s.client(f'{service}')
            return c
        except ClientError as e:
            logger.error(f'Error Connecting with the provided credentials. {e}')
            return []
        except:
            logger.exception(f'General Exception')
            return []

    def getcpustats(self):
        if self.accessKey is not None:
            cwc = self.initconnection('cloudwatch')
            ec2c = self.initconnection('ec2')
        else:
            cwc = self.initprofile('cloudwatch')
            ec2c = self.initprofile('ec2')
        try:
            response = ec2c.describe_instances()
        except ClientError as e:
            logger.error(f'Failed to describe instances... {e}')
            return []
        except:
            logger.exception(f'General Exception')
            return []

        now = datetime.now()
        sTime = now - timedelta(days=self.queryDays)
        eTime = now.strftime("%Y-%m-%d %H:%M:%S")

        info = []

        for a in range(0, len(response['Reservations'])):
            for b in range(0, len(response['Reservations'][a]['Instances'])):
                base = response['Reservations'][a]['Instances'][b]
                try:
                    instanceState = base['State']['Name']
                    instanceId = base['InstanceId']
                    instanceType = base['InstanceType']
                    if instanceState != 'terminated':
                        try:
                            for c in range(0, len(base['Tags'])):
                                if base['Tags'][c]['Key'] == 'ApplicationID':
                                    appId = base['Tags'][c]['Value']
                                if base['Tags'][c]['Key'] == 'Name':
                                    instanceName = base['Tags'][c]['Value']
                        except KeyError:
                            appId = 'Unknown'
                            instanceName = 'Unknown'
                        try:
                            res = cwc.get_metric_statistics(
                                Namespace='AWS/EC2',
                                MetricName='CPUUtilization',
                                Dimensions=[
                                    {
                                        'Name': 'InstanceId',
                                        'Value': f'{instanceId}'
                                    }
                                ],
                                StartTime=sTime,
                                EndTime=eTime,
                                Period=self.queryPeriod,
                                Statistics=[
                                    'Average',
                                ],
                                Unit='Percent'
                            )
                            for x in range(0, len(res['Datapoints'])):
                                metrics = []
                                cwbase = res['Datapoints'][x]
                                Average = cwbase['Average']
                                metrics.append(Average)

                            totalAvg = round((sum(metrics)/len(metrics)), 2)

                        except ClientError as e:
                            logger.error(f'Error getting metrics for instance {b}...{e}')
                        except:
                            logger.exception(f'General Exception')

                    if totalAvg <= 1:
                        suggestedType = 't2.small'
                    elif totalAvg > 1 <= 5:
                        suggestedType = 't2.medium'
                    elif totalAvg > 5 <= 50:
                        suggestedType = 'm5.large'
                    elif totalAvg > 50 <= 80:
                        suggestedType = 'm5.xlarge'
                    elif totalAvg > 80 <= 100:
                        suggestedType = 'm5.2xlarge'

                    info.append(
                        {
                            'Id': f'{instanceId}',
                            'Name': f'{instanceName}',
                            'App': f'{appId}',
                            'AvgCpu': totalAvg,
                            'CurrentType': f'{instanceType}',
                            'SuggestedType': f'{suggestedType}'
                        }
                    )

                except KeyError as e:
                    logger.error(f'Error accessing instance {b}...{e}')
                except:
                    logger.exception(f'General Exception')

        return info

    def main(self):
        today = datetime.date(datetime.now())
        with open(f'report_{today}.csv', 'w', newline='') as f:
            fieldnames = [
                'Id',
                'Name',
                'App',
                'AvgCpu',
                'CurrentType',
                'SuggestedType'
            ]
            w = csv.DictWriter(f, fieldnames)
            w.writeheader()
            for r in self.getcpustats():
                w.writerow(r)
