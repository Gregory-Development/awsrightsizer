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

                        # Suggest upgrades for previous generation instances per AWS guidance

                            # If instance is PrevGen t1.micro, suggest t2.nano

                            if instanceType == 't1.micro':
                                suggestedType = f't2.{t2types[0]}*'

                            # If instance is PrevGen m1 class, suggest t2 class

                            if typesplit[0] == 'm1':
                                if typesplit[1] == 'small':
                                    suggestedType = f't2.{t2types[2]}*'
                                elif typesplit[1] == 'medium':
                                    suggestedType = f't2.{t2types[3]}*'
                                elif typesplit[1] == 'large':
                                    suggestedType = f't2.{t2types[4]}*'
                                elif typesplit[1] == 'xlarge':
                                    suggestedType = f't2.{t2types[5]}*'

                            # If instance is PrevGen m3 class, suggest m5 class

                            if typesplit[0] == 'm3':
                                if typesplit[1] == 'medium':
                                    suggestedType = f't2.{t2types[3]}*'
                                elif typesplit[1] == 'large':
                                    suggestedType = f'm5.{m5types[0]}*'
                                elif typesplit[1] == 'xlarge':
                                    suggestedType = f'm5.{m5types[1]}*'
                                elif typesplit[1] == '2xlarge':
                                    suggestedType = f'm5.{m5types[2]}*'

                            # If instance is PrevGen c1 class, suggest c5 class

                            if typesplit[0] == 'c1':
                                if typesplit[1] == 'medium':
                                    suggestedType = f'c5.{c5types[0]}*'
                                elif typesplit[1] == 'xlarge':
                                    suggestedType = f'c5.{c5types[1]}*'

                            # If instnace is PrevGen cc2 class, suggest c5 class

                            if typesplit[0] == 'cc2':
                                if typesplit[1] == '8xlarge':
                                    suggestedType = f'c5.{c5types[4]}*'

                            # If instance is PrevGen c3 class, suggest c5 class

                            if typesplit[0] == 'c3':
                                if typesplit[1] == 'large':
                                    suggestedType = f'c5.{c5types[0]}*'
                                elif typesplit[1] == 'xlarge':
                                    suggestedType = f'c5.{c5types[1]}*'
                                elif typesplit[1] == '2xlarge':
                                    suggestedType = f'c5.{c5types[2]}*'
                                elif typesplit[1] == '4xlarge':
                                    suggestedType = f'c5.{c5types[3]}*'
                                elif typesplit[1] == '8xlarge':
                                    suggestedType = f'c5.{c5types[4]}*'

                            # If instance is PrevGen g2 class, suggest g3 class

                            if typesplit[0] == 'g2':
                                if typesplit[1] == '2xlarge':
                                    suggestedType = f'g3.{g3types[0]}*'
                                elif typesplit[1] == '8xlarge':
                                    suggestedType = f'g3.{g3types[1]}*'

                            # If instance is PrevGen m2 class, suggest r4 class

                            if typesplit[0] == 'm2':
                                if typesplit[1] == 'xlarge':
                                    suggestedType = f'r4.{r4types[0]}*'
                                elif typesplit[1] == '2xlarge':
                                    suggestedType = f'r4.{r4types[1]}*'
                                elif typesplit[1] == '4xlarge':
                                    suggestedType = f'r4.{r4types[2]}*'

                            # If instance is PrevGen cr1 class, suggest r4 class

                            if typesplit[0] == 'cr1':
                                if typesplit[1] == '8xlarge':
                                    suggestedType = f'r4.{r4types[4]}*'

                            # If instance is PrevGen r3 class, suggest r4 class

                            if typesplit[0] == 'r3':
                                if typesplit[1] == 'large':
                                    suggestedType = f'r4.{r4types[0]}*'
                                elif typesplit[1] == 'xlarge':
                                    suggestedType = f'r4.{r4types[1]}*'
                                elif typesplit[1] == '2xlarge':
                                    suggestedType = f'r4.{r4types[2]}*'
                                elif typesplit[1] == '4xlarge':
                                    suggestedType = f'r4.{r4types[3]}*'
                                elif typesplit[1] == '8xlarge':
                                    suggestedType = f'r4.{r4types[4]}*'

                            # If instance is PrevGen i2 class, suggest i3 class

                            if typesplit[0] == 'i2':
                                if typesplit[1] == 'xlarge':
                                    suggestedType = f'i3.{i3types[1]}*'
                                if typesplit[1] == '2xlarge':
                                    suggestedType = f'i3.{i3types[2]}*'
                                if typesplit[1] == '4xlarge':
                                    suggestedType = f'i3.{i3types[3]}*'
                                if typesplit[1] == '8xlarge':
                                    suggestedType = f'i3.{i3types[4]}*'

                            # If instance is PrevGen hs1 class, suggest d2 class

                            if typesplit[0] == 'hs1':
                                if typesplit[1] == '8xlarge':
                                    suggestedType = f'd2.{d2types[2]}*'

                        # Suggest Instance Types based on AVG CPU usage keeping general instance type class, current gen only

                            if typesplit[0] == 't2':
                                typeindex = t2types.index(f'{typesplit[1]}')
                                if totalAvg <=5:
                                    suggestedType = f'{typesplit[0]}.{t2types[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{t2types[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{t2types[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{t2types[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'm4.{m4types[3]}'
                            elif typesplit[0] == 'm5':
                                typeindex = m5types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{m5types[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{m5types[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{m5types[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{m5types[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'm5.{m5types[5]}'
                            elif typesplit[0] == 'm5d':
                                typeindex = m5dtypes.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{m5dtypes[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{m5dtypes[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{m5dtypes[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{m5dtypes[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'm5d.{m5dtypes[5]}'
                            elif typesplit[0] == 'm4':
                                typeindex = m4types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{m4types[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{m4types[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{m4types[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{m4types[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'm5.{m5types[5]}'
                            elif typesplit[0] == 'c5':
                                typeindex = c5types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{c5types[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{c5types[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{c5types[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{c5types[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'c5.{c5types[5]}'
                            elif typesplit[0] == 'c5d':
                                typeindex = c5dtypes.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{c5dtypes[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{c5dtypes[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{c5dtypes[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{c5dtypes[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'c5d.{c5dtypes[5]}'
                            elif typesplit[0] == 'c4':
                                typeindex = c4types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{c4types[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{c4types[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{c4types[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{c4types[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'c5.{c5types[5]}'
                            elif typesplit[0] == 'x1':
                                typeindex = x1types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{x1types[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{x1types[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{x1types[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{x1types[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'x1e.{x1etypes[5]}'
                            elif typesplit[0] == 'x1e':
                                typeindex = x1etypes.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{x1etypes[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{x1etypes[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{x1etypes[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{x1etypes[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'x1e.{x1etypes[5]}'
                            elif typesplit[0] == 'r4':
                                typeindex = r4types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{r4types[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{r4types[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{f4types[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{r4types[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'x1.{x1types[0]}'
                            elif typesplit[0] == 'p2':
                                typeindex = p2types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{p2types[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{p2types[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{p2types[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{p2types[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'g3.{g3types[0]}'
                            elif typesplit[0] == 'p3':
                                typeindex = p3types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{p3types[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{p3types[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{p3types[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{p3types[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'g3.{g3types[0]}'
                            elif typesplit[0] == 'g3':
                                typeindex = g3types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{g3types[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{g3types[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{g3types[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{g3types[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'f1.{f1types[1]}'
                            elif typesplit[0] == 'f1':
                                typeindex = f1types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{f1types[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{f1types[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{f1types[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{f1types[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'f1.{f1types[1]}'
                            elif typesplit[0] == 'h1':
                                typeindex = h1types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{h1types[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{h1types[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{h1types[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{h1types[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'i3.{i3types[6]}'
                            elif typesplit[0] == 'i3':
                                typeindex = i3types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{i3types[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{i3types[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{i3types[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{i3types[typeindex+1]}'
                                    except IndexError:
                                        suggestedType = f'i3.{i3types[6]}'
                            elif typesplit[0] == 'd2':
                                typeindex = d2types.index(f'{typesplit[1]}')
                                if totalAvg <= 5:
                                    suggestedType = f'{typesplit[0]}.{d2types[0]}'
                                elif totalAvg > 5 <= 30:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{d2types[typeindex-1]}'
                                    except ValueError:
                                        suggestedType = f'{typesplit[0]}.{d2types[0]}'
                                elif totalAvg > 30 <= 80:
                                    suggestedType = f'{instanceType}'
                                elif totalAvg > 80:
                                    try:
                                        suggestedType = f'{typesplit[0]}.{d2types[typeindex+1]}'
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

                        # If instance is already t2.nano, keep it the same

                        if DBInstanceClass == 'db.t2.nano':
                            suggestedType = f't2.{dbt2types[0]}'

                        # Suggest upgrades for previous generation instances per AWS guidance

                        # If instance is PrevGen db.t1.micro, suggest db.t2.nano

                        if DBInstanceClass == 'db.t1.micro':
                            suggestedType = f'{typesplit[0]}.t2.{dbt2types[0]}*'

                        # If instance is PrevGen m1 class, suggest t2 class

                        if typesplit[1] == 'm1':
                            if typesplit[2] == 'small':
                                suggestedType = f'{typesplit[0]}.t2.{dbt2types[1]}*'
                            elif typesplit[2] == 'medium':
                                suggestedType = f'{typesplit[0]}.t2.{dbt2types[2]}*'
                            elif typesplit[2] == 'large':
                                suggestedType = f'{typesplit[0]}.t2.{dbt2types[3]}*'
                            elif typesplit[2] == 'xlarge':
                                suggestedType = f'{typesplit[0]}.t2.{dbt2types[4]}*'

                        # If instance is PrevGen m2 class, suggest r3 class

                        if typesplit[1] == 'm2':
                            if typesplit[2] == 'xlarge':
                                suggestedType = f'{typesplit[0]}.t2.{dbr3types[2]}*'
                            elif typesplit[2] == '2xlarge':
                                suggestedType = f'{typesplit[0]}.t2.{dbr3types[3]}*'
                            elif typesplit[2] == '4xlarge':
                                suggestedType = f'{typesplit[0]}.t2.{dbr3types[4]}*'

                        # Suggest Instance Types based on AVG CPU usage keeping general instance type class
                        # current gen only

                        if typesplit[1] == 't2':
                            typeindex = dbt2types.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbt2types[0]}'
                            elif totalAvg > 5 <= 30:
                                try:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbt2types[typeindex-1]}'
                                except ValueError:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbt2types[0]}'
                            elif totalAvg > 30 <= 80:
                                suggestedType = f'{DBInstanceClass}'
                            elif totalAvg > 80:
                                try:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbt2types[typeindex+1]}'
                                except IndexError:
                                    suggestedType = f'{typesplit[0]}.m4.{dbm4types[3]}'

                        if typesplit[1] == 'm4':
                            typeindex = dbm4types.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm4types[0]}'
                            elif totalAvg > 5 <= 30:
                                try:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm4types[typeindex-1]}'
                                except ValueError:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm4types[0]}'
                            elif totalAvg > 30 <= 80:
                                suggestedType = f'{DBInstanceClass}'
                            elif totalAvg > 80:
                                try:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm4types[typeindex+1]}'
                                except IndexError:
                                    suggestedType = f'{typesplit[0]}.x1e.{dbx1etypes[4]}'

                        if typesplit[1] == 'm3':
                            typeindex = dbm3types.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm3types[0]}'
                            elif totalAvg > 5 <= 30:
                                try:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm3types[typeindex-1]}'
                                except ValueError:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm3types[0]}'
                            elif totalAvg > 30 <= 80:
                                suggestedType = f'{DBInstanceClass}'
                            elif totalAvg > 80:
                                try:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbm3types[typeindex+1]}'
                                except IndexError:
                                    suggestedType = f'{typesplit[0]}.m4.{dbm4types[3]}'

                        if typesplit[1] == 'r4':
                            typeindex = dbr4types.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr4types[0]}'
                            elif totalAvg > 5 <= 30:
                                try:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr4types[typeindex-1]}'
                                except ValueError:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr4types[0]}'
                            elif totalAvg > 30 <= 80:
                                suggestedType = f'{DBInstanceClass}'
                            elif totalAvg > 80:
                                try:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr4types[typeindex+1]}'
                                except IndexError:
                                    suggestedType = f'{typesplit[0]}.x1e.{dbx1etypes[4]}'

                        if typesplit[1] == 'r3':
                            typeindex = dbr3types.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr3types[0]}'
                            elif totalAvg > 5 <= 30:
                                try:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr3types[typeindex-1]}'
                                except ValueError:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr3types[0]}'
                            elif totalAvg > 30 <= 80:
                                suggestedType = f'{DBInstanceClass}'
                            elif totalAvg > 80:
                                try:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbr3types[typeindex+1]}'
                                except IndexError:
                                    suggestedType = f'{typesplit[0]}.r4.{dbr4types[5]}'

                        if typesplit[1] == 'x1e':
                            typeindex = dbx1etypes.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1etypes[0]}'
                            elif totalAvg > 5 <= 30:
                                try:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1etypes[typeindex-1]}'
                                except ValueError:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1etypes[0]}'
                            elif totalAvg > 30 <= 80:
                                suggestedType = f'{DBInstanceClass}'
                            elif totalAvg > 80:
                                try:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1etypes[typeindex+1]}'
                                except IndexError:
                                    suggestedType = f'{typesplit[0]}.x1e.{dbx1etypes[5]}'

                        if typesplit[1] == 'x1':
                            typeindex = dbx1types.index(f'{typesplit[2]}')
                            if totalAvg <= 5:
                                suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1types[0]}'
                            elif totalAvg > 5 <= 30:
                                try:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1types[typeindex]-1}'
                                except ValueError:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1types[0]}'
                            elif totalAvg > 30 <= 80:
                                suggestedType = f'{DBInstanceClass}'
                            elif totalAvg > 80:
                                try:
                                    suggestedType = f'{typesplit[0]}.{typesplit[1]}.{dbx1types[typeindex+1]}'
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
        extra = {
            'Id': '* - AWS Suggested Upgrade',
            'Name': '',
            'App': '',
            'AvgCpu': '',
            'CurrentType': '',
            'SuggestedType': ''
        }
        with open(self.output, 'w', newline='') as f:
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
            for r in self.getrdssuggestions():
                w.writerow(r)
            csv.writer(f).writerow('')
            w.writerow(extra)
