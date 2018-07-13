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
            output=args.output
    ):
        self.accessKey = accessKey
        self.secretKey = secretKey
        self.region = region
        self.profile = profile
        self.threasholdAvg = thresholdAvg
        self.threasholdMax = thresholdMax
        self.queryDays = queryDays
        self.queryPeriod = queryPeriod
        self.output = output

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

    def suggestinstancetype(self):
        pass

    def getec2suggestions(self):
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

                            # General Purpose Instance Types

                            t1types = [
                                'micro',
                            ]

                            t2types = [
                                'nano',
                                'micro',
                                'small',
                                'medium',
                                'large',
                                'xlarge',
                                '2xlarge',
                            ]

                            m1types = [
                                'small',
                                'medium',
                                'large',
                                'xlarge',
                            ]

                            m3types = [
                                'medium',
                                'large',
                                'xlarge',
                                '2xlarge',
                            ]

                            m4types = [
                                'large',
                                'xlarge',
                                '2xlarge',
                                '4xlarge',
                                '10xlarge',
                                '16xlarge',
                            ]

                            m5types = [
                                'large',
                                'xlarge',
                                '2xlarge',
                                '4xlarge',
                                '12xlarge',
                                '24xlarge',
                            ]

                            m5dtypes = [
                                'large',
                                'xlarge',
                                '2xlarge',
                                '4xlarge',
                                '12xlarge',
                                '24xlarge',
                            ]

                            # Compute Optimized Instance Types

                            c1types = [
                                'medium',
                                'xlarge',
                            ]

                            cc2types = [
                                '8xlarge',
                            ]

                            c3types = [
                                'large',
                                'xlarge',
                                '2xlarge',
                                '4xlarge',
                                '8xlarge',
                            ]

                            c4types = [
                                'large',
                                'xlarge',
                                '2xlarge',
                                '4xlarge',
                                '8xlarge',
                            ]

                            c5types = [
                                'large',
                                'xlarge',
                                '2xlarge',
                                '4xlarge',
                                '9xlarge',
                                '18xlarge',
                            ]

                            c5dtypes = [
                                'large',
                                'xlarge',
                                '2xlarge',
                                '4xlarge',
                                '9xlarge',
                                '18xlarge',
                            ]

                            # Memory Optimized Instance Types

                            cr1types = [
                                '8xlarge',
                            ]

                            m2types = [
                                'xlarge',
                                '2xlarge',
                                '4xlarge',
                            ]

                            r3types = [
                                'large',
                                'xlarge',
                                '2xlarge',
                                '4xlarge',
                                '8xlarge',
                            ]

                            r4types = [
                                'large',
                                'xlarge',
                                '2xlarge',
                                '4xlarge',
                                '8xlarge',
                                '16xlarge',
                            ]

                            x1types = [
                                '16xlarge',
                                '32xlarge'
                            ]

                            x1etypes = [
                                'xlarge',
                                '2xlarge',
                                '4xlarge',
                                '8xlarge',
                                '16xlarge',
                                '32xlarge',
                            ]

                            # GPU/Accelerated Compute Optimized Instance Types

                            g2types = [
                                '2xlarge',
                                '8xlarge',
                            ]

                            g3types = [
                                '4xlarge',
                                '8xlarge',
                                '16xlarge',
                            ]

                            p2types = [
                                'xlarge',
                                '8xlarge',
                                '16xlarge',
                            ]

                            p3types = [
                                '2xlarge',
                                '8xlarge',
                                '16xlarge',
                            ]

                            f1types = [
                                '2xlarge',
                                '16xlarge',
                            ]

                            # Storage Optimized Instance Types

                            i2types = [
                                'xlarge',
                                '2xlarge',
                                '4xlarge',
                                '8xlarge',
                            ]

                            i3types = [
                                'large',
                                'xlarge',
                                '2xlarge',
                                '4xlarge',
                                '8xlarge',
                                '16xlarge',
                                'metal',
                            ]

                            h1types = [
                                '2xlarge',
                                '4xlarge',
                                '8xlarge',
                                '16xlarge',
                            ]

                            hs1types = [
                                '8xlarge',
                            ]

                            d2types = [
                                'xlarge',
                                '2xlarge',
                                '4xlarge',
                                '8xlarge',
                            ]

                            typesplit = instanceType.split('.')

                            # If instance is already t2.nano, keep it the same

                            if instanceType == 't2.nano':
                                suggestedType = f't2.{t2types[0]}'

                        # Suggest Instance Types based on AVG CPU usage keeping general instance type class, current gen only
                            if typesplit[0] == 't1':
                                suggestedType = f't2.{t2types[0]}'
                            elif typesplit[0] == 't2':
                                typeindex = t2types.index(f'{typesplit[1]}')
                                if totalAvg <=5:
                                    suggestedType = f'{typesplit[0]}.{t2types[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex -1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{t2types[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{t2types[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{t2types[index]}'
                                    except IndexError:
                                        suggestedType = f'm4.{m4types[3]}'
                            elif typesplit[0] == 'm5':
                                typeindex = m5types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{m5types[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex -1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{m5types[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{m5types[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{m5types[index]}'
                                    except IndexError:
                                        suggestedType = f'm5.{m5types[5]}'
                            elif typesplit[0] == 'm5d':
                                typeindex = m5dtypes.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{m5dtypes[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{m5dtypes[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{m5dtypes[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{m5dtypes[index]}'
                                    except IndexError:
                                        suggestedType = f'm5d.{m5dtypes[5]}'
                            elif typesplit[0] == 'm4':
                                typeindex = m4types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{m4types[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{m4types[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{m4types[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{m4types[index]}'
                                    except IndexError:
                                        suggestedType = f'm5.{m5types[5]}'
                            elif typesplit[0] == 'm3': # PrevGen Upgrade to M5
                                typeindex = m3types.index(typesplit[1])
                                if totalAvg <= 5:
                                    suggestedType = f't2.{t2types[2]}*'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 2
                                    if index < 0:
                                        suggestedType = f't2.{t2types[3]}*'
                                    else:
                                        suggestedType = f'm5.{m5types[index]}*'
                                elif totalAvg > 30 <= 80:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'm5.{m5types[2]}*'
                                    else:
                                        suggestedType = f'm5.{m5types[index]}*'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'm5.{m5types[typeindex]}*'
                                    except IndexError:
                                        suggestedType = f'm5.{m5types[2]}*'
                            elif typesplit[0] == 'm2': # PrevGen Upgrade to R4
                                typeindex = m2types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'r4.{r4types[0]}*'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'r4.{r4types[0]}*'
                                    else:
                                        suggestedType = f'r4.{r4types[index]}*'
                                elif totalAvg > 30 <= 80:
                                    index = typeindex + 1
                                    suggestedType = f'r4.{r4types[index]}*'
                                elif totalAvg > 80:
                                    index = typeindex + 2
                                    try:
                                        suggestedType = f'r4.{r4types[index]}*'
                                    except IndexError:
                                        suggestedType = f'r4.{r4types[5]}*'
                            elif typesplit[0] == 'm1': # PrevGen Upgrade to T2
                                typeindex = m1types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f't2.{t2types[0]}*'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f't2.{t2types[0]}*'
                                    else:
                                        suggestedType = f't2.{t2types[index]}*'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f't2.{t2types[typeindex]}*'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f't2.{t2types[index]}*'
                                    except IndexError:
                                        suggestedType = f'm4.{m4types[3]}*'
                            elif typesplit[0] == 'c5':
                                typeindex = c5types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{c5types[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{c5types[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{c5types[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{c5types[index]}'
                                    except IndexError:
                                        suggestedType = f'c5.{c5types[5]}'
                            elif typesplit[0] == 'c5d':
                                typeindex = c5dtypes.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{c5dtypes[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex -1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{c5dtypes[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{c5dtypes[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{c5dtypes[index]}'
                                    except IndexError:
                                        suggestedType = f'c5d.{c5dtypes[5]}'
                            elif typesplit[0] == 'c4':
                                typeindex = c4types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{c4types[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{c4types[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{c4types[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{c4types[index]}'
                                    except IndexError:
                                        suggestedType = f'c5.{c5types[5]}'
                            elif typesplit[0] == 'c3': # PrevGen Upgrade to C5
                                typeindex = c3types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'c5.{c5types[0]}*'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'c5.{c5types[0]}*'
                                    else:
                                        suggestedType = f'c5.{c5types[index]}*'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'c5.{c5types[typeindex]}*'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'c5.{c5types[index]}*'
                                    except IndexError:
                                        suggestedType = f'c5.{c5types[5]}*'
                            elif typesplit[0] == 'cc2': # PrevGen Upgrade to C5
                                typeindex = cc2types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'c5.{c5types[0]}*'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'c5.{c5types[3]}*'
                                    else:
                                        suggestedType = f'c5.{c5types[index]}*'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'c5.{c5types[4]}*'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'c5.{c5types[index]}*'
                                    except IndexError:
                                        suggestedType = f'c5.{c5types[5]}*'
                            elif typesplit[0] == 'cr1': # PrevGen Upgrade to R4
                                typeindex = m2types.index(f'{typesplit[1]}')
                                if totalAvg <= 30:
                                    suggestedType = f'r4.{r4types[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'r4.{r4types[4]}'
                                elif totalAvg > 80:
                                        suggestedType = f'r4.{r4types[5]}'
                            elif typesplit[0] == 'c1': # PrevGen Upgrade to C5
                                typeindex = c1types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'c5.{c5types[0]}*'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'c5.{c5types[0]}*'
                                    else:
                                        suggestedType = f'c5.{c5types[index]}*'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'c5.{c5types[typeindex]}*'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'c5.{c5types[index]}*'
                                    except IndexError:
                                        suggestedType = f'c5.{c5types[5]}*'
                            elif typesplit[0] == 'x1':
                                typeindex = x1types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{x1types[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{x1types[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{x1types[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{x1types[index]}'
                                    except IndexError:
                                        suggestedType = f'x1e.{x1etypes[5]}'
                            elif typesplit[0] == 'x1e':
                                typeindex = x1etypes.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{x1etypes[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex -1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{x1etypes[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{x1etypes[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{x1etypes[index]}'
                                    except IndexError:
                                        suggestedType = f'x1e.{x1etypes[5]}'
                            elif typesplit[0] == 'r4':
                                typeindex = r4types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{r4types[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{r4types[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{r4types[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{r4types[index]}'
                                    except IndexError:
                                        suggestedType = f'x1.{x1types[0]}'
                            elif typesplit[0] == 'r3': # PrevGen Upgrade to R4
                                typeindex = r3types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'r4.{r4types[0]}*'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'r4.{r4types[0]}*'
                                    else:
                                        suggestedType = f'r4.{r4types[index]}*'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'r4.{r4types[typeindex]}*'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'r4.{r4types[index]}*'
                                    except IndexError:
                                        suggestedType = f'x1.{x1types[0]}*'
                            elif typesplit[0] == 'p2':
                                typeindex = p2types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{p2types[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{p2types[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{p2types[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{p2types[index]}'
                                    except IndexError:
                                        suggestedType = f'g3.{g3types[0]}'
                            elif typesplit[0] == 'p3':
                                typeindex = p3types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{p3types[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{p3types[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{p3types[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{p3types[index]}'
                                    except IndexError:
                                        suggestedType = f'g3.{g3types[0]}'
                            elif typesplit[0] == 'g3':
                                typeindex = g3types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{g3types[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{g3types[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{g3types[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{g3types[index]}'
                                    except IndexError:
                                        suggestedType = f'f1.{f1types[1]}'
                            elif typesplit[0] == 'g2': # PrevGen Upgrade to G3
                                typeindex = g2types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'g3.{g3types[0]}*'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'g3.{g3types[0]}*'
                                    else:
                                        suggestedType = f'g3.{g3types[index]}*'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'g3.{typeindex}*'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'g3.{g3types[index]}*'
                                    except IndexError:
                                        suggestedType = f'f1.{f1types[1]}*'
                            elif typesplit[0] == 'f1':
                                typeindex = f1types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{f1types[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{f1types[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{f1types[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{f1types[index]}'
                                    except IndexError:
                                        suggestedType = f'f1.{f1types[1]}'
                            elif typesplit[0] == 'hs1': # PrevGen Upgrade to d2
                                typeindex = hs1types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'd2.{d2types[0]}*'
                                elif totalAvg > 5 <= 30:
                                        suggestedType = f'd2.{d2types[1]}*'
                                elif totalAvg > 30:
                                        suggestedType = f'd2.{d2types[3]}*'
                            elif typesplit[0] == 'h1':
                                typeindex = h1types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{h1types[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{h1types[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{h1types[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{h1types[index]}'
                                    except IndexError:
                                        suggestedType = f'i3.{i3types[6]}'
                            elif typesplit[0] == 'i3':
                                typeindex = i3types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{i3types[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{i3types[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{i3types[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{i3types[index]}'
                                    except IndexError:
                                        suggestedType = f'i3.{i3types[6]}'
                            elif typesplit[0] == 'i2': # PrevGen Upgread to i3
                                typeindex = i2types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'i3.{i3types[0]}*'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'i3.{i3types[typeindex]}*'
                                    except ValueError:
                                        suggestedType = f'i3.{i3types[0]}*'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'i3.{i3types[typeindex]}*'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 2
                                        suggestedType = f'i3.{i3types[index]}*'
                                    except IndexError:
                                        suggestedType = f'i3.{i3types[6]}*'
                            elif typesplit[0] == 'd2':
                                typeindex = d2types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{d2types[0]}'
                                elif totalAvg > 5 <= 30:
                                    index = typeindex - 1
                                    if index < 0:
                                        suggestedType = f'{typesplit[0]}.{d2types[0]}'
                                    else:
                                        suggestedType = f'{typesplit[0]}.{d2types[index]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        index = typeindex + 1
                                        suggestedType = f'{typesplit[0]}.{d2types[index]}'
                                    except IndexError:
                                        suggestedType = f'd2.{d2types[3]}'

                        except ClientError as e:
                            logger.error(f'Error getting metrics for instance {b}...{e}')
                        except:
                            logger.exception(f'General Exception')

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

    def getrdssuggestions(self):
        if self.accessKey is not None:
            cwc = self.initconnection('cloudwatch')
            rdsc = self.initconnection('rds')
        else:
            cwc = self.initprofile('cloudwatch')
            rdsc = self.initprofile('rds')
        try:
            response = rdsc.describe_db_instances()
        except ClientError as e:
            logger.error(f'Failed to describe rds instances... {e}')
            return []
        except:
            logger.exception(f'General Exception')
            return []

        now = datetime.now()
        sTime = now - timedelta(days=self.queryDays)
        eTime = now.strftime("%Y-%m-%d %H:%M:%S")

        info = []

        for a in range(0, len(response['DBInstances'])):
            base = response['DBInstances'][a]
            try:
                DBInstanceStatus = base['DBInstanceStatus']
                DBInstanceIdentifier = base['DBInstanceIdentifier']
                DBInstanceClass = base['DBInstanceClass']
                DBInstnaceArn = base['DBInstanceArn']
                DBEngine = base['Engine']
                if DBInstanceStatus == 'available':
                    try:
                        tags = rdsc.list_tags_for_resource(
                            ResourceName=f'{DBInstnaceArn}',
                        )
                        for b in range(0, len(tags['TagList'])):
                            tagbase = tags['TagList'][b]
                            if tagbase['Key'] == 'ApplicationID':
                                appId = tagbase['Value']
                            else:
                                appId = 'Unassigned'
                            if tagbase['Key'] == 'Name':
                                instanceName = tagbase['Value']
                            else:
                                instanceName = DBInstanceIdentifier
                    except ClientError as e:
                        logger.error(f'Failed to list rds tags... {e}')
                        return []
                    try:
                        res = cwc.get_metric_statistics(
                            Namespace='AWS/RDS',
                            MetricName='CPUUtilization',
                            Dimensions=[
                                {
                                    'Name': 'DBInstanceIdentifier',
                                    'Value': f'{DBInstanceIdentifier}'
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

                        # General Purpose DB Instance Types

                        dbm4types = [
                            'large',
                            'xlarge',
                            '2xlarge',
                            '4xlarge',
                            '10xlarge',
                            '16xlarge',
                        ]

                        dbm3types = [
                            'medium',
                            'large',
                            'xlarge',
                            '2xlarge',
                        ]

                        dbm1types = [
                            'small',
                            'medium',
                            'large',
                            'xlarge',
                        ]

                        # Memory Optimized DB Instance Types

                        dbm2types = [
                            'xlarge',
                            '2xlarge',
                            '4xlarge',
                        ]

                        dbr4types = [
                            'large',
                            'xlarge',
                            '2xlarge',
                            '4xlarge',
                            '8xlarge',
                            '16xlarge',
                        ]

                        dbr3types = [
                            'large',
                            'xlarge',
                            '2xlarge',
                            '4xlarge',
                            '8xlarge',
                        ]

                        dbx1etypes = [
                            'xlarge',
                            '2xlarge',
                            '4xlarge',
                            '8xlarge',
                            '16xlarge',
                            '32xlarge',
                        ]

                        dbx1types = [
                            '16xlarge',
                            '32xlarge',
                        ]

                        # Burstable DB Instance Types

                        dbt1types = [
                            'micro'
                        ]

                        dbt2types = [
                            'micro',
                            'small',
                            'medium',
                            'large',
                            'xlarge',
                            '2xlarge',
                        ]

                        typesplit = DBInstanceClass.split('.')

                        # Suggest Instance Types based on AVG CPU usage keeping general instance type class

                        if typesplit[1] == 't2':
                            typeindex = dbt2types.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbt2types[0]}'
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbt2types[0]}'
                                else:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbt2types[index]}'
                            elif totalAvg > 30 <= 80:
                                suggestedType = f'{DBInstanceClass}'
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbt2types[index]}'
                                except IndexError:
                                    suggestedType = f'{typesplit[0]}.m4.{dbm4types[3]}'

                        elif typesplit[1] == 't1': # PrevGen Upgrade to t2
                            suggestedType = f'{typesplit[0]}.t2.{dbt2types[0]}*'

                        elif typesplit[1] == 'm4':
                            typeindex = dbm4types.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm4types[0]}'
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm4types[0]}'
                                else:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm4types[index]}'
                            elif totalAvg > 30 <= 80:
                                suggestedType = f'{DBInstanceClass}'
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm4types[index]}'
                                except IndexError:
                                    suggestedType = f'{typesplit[0]}.x1e.{dbx1etypes[4]}'

                        elif typesplit[1] == 'm3':
                            typeindex = dbm3types.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm3types[0]}'
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm3types[0]}'
                                else:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm3types[index]}'
                            elif totalAvg > 30 <= 80:
                                suggestedType = f'{DBInstanceClass}'
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm3types[index]}'
                                except IndexError:
                                    suggestedType = f'{typesplit[0]}.m4.{dbm4types[3]}'

                        elif typesplit[1] == 'm2': # PrevGen Upgrade to R3
                            typeindex = dbm2types.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.r3.{dbr3types[0]}'
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = f'{typesplit[0]}.r3.{dbr3types[0]}'
                                else:
                                    suggestedType = f'{typesplit[0]}.r3.{dbr3types[index]}'
                            elif totalAvg > 30 <= 80:
                                index = typeindex
                                suggestedType = f'{typesplit[0]}.r3.{dbr3types[index]}'
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = f'{typesplit[0]}.r3.{dbr3types[index]}'
                                except IndexError:
                                    suggestedType = f'{typesplit[0]}.r3.{dbr3types[4]}'

                        elif typesplit[1] == 'm1': # PrevGen Upgrade to t2
                            typeindex = dbm1types.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.t2.{dbt2types[0]}'
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = f'{typesplit[0]}.t2.{dbt2types[0]}'
                                else:
                                    suggestedType = f'{typesplit[0]}.t2.{dbt2types[index]}'
                            elif totalAvg > 30 <= 80:
                                index = typeindex + 1
                                suggestedType = f'{typesplit[0]}.t2.{dbt2types[index]}'
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = f'{typesplit[0]}.t2.{dbt2types[index]}'
                                except IndexError:
                                    suggestedType = f'{typesplit[0]}.t2.{dbt2types[3]}'

                        elif typesplit[1] == 'r4':
                            typeindex = dbr4types.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr4types[0]}'
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr4types[0]}'
                                else:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr4types[index]}'
                            elif totalAvg > 30 <= 80:
                                suggestedType = f'{DBInstanceClass}'
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr4types[index]}'
                                except IndexError:
                                    suggestedType = f'{typesplit[0]}.x1e.{dbx1etypes[4]}'

                        elif typesplit[1] == 'r3':
                            typeindex = dbr3types.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr3types[0]}'
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr3types[0]}'
                                else:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr3types[index]}'
                            elif totalAvg > 30 <= 80:
                                suggestedType = f'{DBInstanceClass}'
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr3types[index]}'
                                except IndexError:
                                    suggestedType = f'{typesplit[0]}.r4.{dbr4types[5]}'

                        elif typesplit[1] == 'x1e':
                            typeindex = dbx1etypes.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1etypes[0]}'
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1etypes[0]}'
                                else:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1etypes[index]}'
                            elif totalAvg > 30 <= 80:
                                suggestedType = f'{DBInstanceClass}'
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1etypes[index]}'
                                except IndexError:
                                    suggestedType = f'{typesplit[0]}.x1e.{dbx1etypes[5]}'

                        elif typesplit[1] == 'x1':
                            typeindex = dbx1types.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1types[0]}'
                            elif totalAvg > 5 <= 30:
                                index = typeindex -1
                                if index < 0:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1types[0]}'
                                else:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1types[index]}'
                            elif totalAvg > 30 <= 80:
                                suggestedType = f'{DBInstanceClass}'
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1types[index]}'
                                except IndexError:
                                    suggestedType = f'{typesplit[0]}.x1e.{dbx1etypes[5]}'

                    except ClientError as e:
                        logger.error(f'Error getting metrics for instance {a}...{e}')
                    except:
                        logger.exception(f'General Exception')

                info.append(
                    {
                        'Id': f'{DBInstanceIdentifier}',
                        'Name': f'{instanceName}',
                        'Engine': f'{DBEngine}',
                        'App': f'{appId}',
                        'AvgCpu': totalAvg,
                        'CurrentType': f'{DBInstanceClass}',
                        'SuggestedType': f'{suggestedType}'
                    }
                )

            except KeyError as e:
                logger.error(f'Error accessing instance...{e}')
            except:
                logger.exception(f'General Exception')

        return info

    def main(self):
        if args.ec2only:
            extra = {
                'Id': '* - AWS Suggested Upgrade'
            }
            with open('ec2_'+f'{self.output}', 'w', newline='') as f:
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
                for r in self.getec2suggestions():
                    w.writerow(r)
                csv.writer(f).writerow('')
                w.writerow(extra)
        elif args.rdsonly:
            extra = {
                'Id': '* - AWS Suggested Upgrade'
            }
            with open('rds_'+f'{self.output}', 'w', newline='') as f:
                fieldnames = [
                    'Id',
                    'Name',
                    'Engine',
                    'App',
                    'AvgCpu',
                    'CurrentType',
                    'SuggestedType'
                ]
                w = csv.DictWriter(f, fieldnames)
                w.writeheader()
                for r in self.getrdssuggestions():
                    w.writerow(r)
                csv.writer(f).writerow('')
                w.writerow(extra)
        else:
            extra = {
                'Id': '* - AWS Suggested Upgrade'
            }
            with open('ec2_' + f'{self.output}', 'w', newline='') as f:
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
                for r in self.getec2suggestions():
                    w.writerow(r)
                csv.writer(f).writerow('')
                w.writerow(extra)

            with open('rds_' + f'{self.output}', 'w', newline='') as f:
                fieldnames = [
                    'Id',
                    'Name',
                    'Engine',
                    'App',
                    'AvgCpu',
                    'CurrentType',
                    'SuggestedType'
                ]
                w = csv.DictWriter(f, fieldnames)
                w.writeheader()
                for r in self.getrdssuggestions():
                    w.writerow(r)
                csv.writer(f).writerow('')
                w.writerow(extra)