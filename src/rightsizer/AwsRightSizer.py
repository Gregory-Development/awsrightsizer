# Standard Library Imports
import logging
from datetime import (
    datetime,
    timedelta,
)

# Third-Party Imports
import boto3
from botocore.exceptions import ClientError

# Local Imports
# Placeholder


class Main:
    def __init__(
            self,
            thresholdAvg,
            thresholdMax,
            queryDays,
            queryPeriod,
            output,
            verbose,
            accessKey=None,
            secretKey=None,
            region=None,
            profile=None,
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
        self.verbosity = verbose
        self.logger = self._init_logger()

    def _init_logger(self):
        l = logging.Logger(__name__)
        l.setLevel(self.verbosity)
        return l

    def _serialize_datetime(self, t):
        """
        A method to serialize AWS datetime objects to be displayed as JSON (future use)
        :param t:
        :return: (string) the datetime object as a str object
        """
        if isinstance(t, datetime):
            return t.__str__()

    def _init_connection(self, service):
        """
        A method to initialize an AWS service connection with access/secret access keys.
        :param service:
        :return: (object) the AWS connection object.
        """
        try:
            s = boto3.Session(
                aws_access_key_id='{}'.format(self.accessKey),
                aws_secret_access_key='{}'.format(self.secretKey),
                region_name='{}'.format(self.region),
            )
            c = s.client('{}'.format(service))
            return c
        except ClientError as e:
            self.logger.error('Error Connecting with the provided credentials. {}'.format(e))
            return []
        except Exception as e:
            self.logger.exception('General Exception ... {}'.format(e))
            return []

    def _init_profile(self, service):
        """
        A method to initialize an AWS service connection with an AWS profile.
        :param service:
        :return: (object) the AWS connection object.
        """
        try:
            s = boto3.Session(
                profile_name='{}'.format(self.profile)
            )
            c = s.client('{}'.format(service))
            return c
        except ClientError as e:
            self.logger.error('Error Connecting with the provided credentials... {}'.format(e))
            return []
        except Exception as e:
            self.logger.exception('General Exception ... {}'.format(e))
            return []

    def getec2suggestions(self):
        """
        A method to suggest the right sizing for AWS EC2 Instances.
        :return: (dictionary) The dictionary result of the logic.
        """
        if self.accessKey is not None:
            cwc = self._init_connection('cloudwatch')
            ec2c = self._init_connection('ec2')
        else:
            cwc = self._init_profile('cloudwatch')
            ec2c = self._init_profile('ec2')
        try:
            response = ec2c.describe_instances()
        except ClientError as e:
            self.logger.error('Failed to describe instances... {}'.format(e))
            return []
        except Exception as e:
            self.logger.exception('General Exception... {}'.format(e))
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
                except KeyError:
                    self.logger.exception('Instance State Undefined')
                    return []
                except Exception as e:
                    self.logger.exception('General Exception ... {}'.format(e))
                    return []

                try:
                    instanceId = base['InstanceId']
                except KeyError:
                    self.logger.exception('Instance Id Undefined')
                    return []
                except Exception as e:
                    self.logger.exception('General Exception ... {}'.format(e))
                    return []

                try:
                    instanceType = base['InstanceType']
                except KeyError:
                    self.logger.exception('Instance Type Undefined')
                    return []
                except Exception as e:
                    self.logger.exception('Gerneral Exception ... {}'.format(e))
                    return []

                if instanceState != 'terminated':
                    try:
                        for c in range(0, len(base['Tags'])):
                            if base['Tags'][c]['Key'] == 'Name':
                                instanceName = base['Tags'][c]['Value']
                    except KeyError:
                        self.logger.info("Instance Name Undefined, Setting to 'Undefined'")
                        instanceName = 'Undefined'
                    try:
                        res = cwc.get_metric_statistics(
                            Namespace='AWS/EC2',
                            MetricName='CPUUtilization',
                            Dimensions=[
                                {
                                    'Name': 'InstanceId',
                                    'Value': '{}'.format(instanceId)
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

                        r5types = [
                            'large',
                            'xlarge',
                            '2xlarge',
                            '4xlarge',
                            '12xlarge',
                            '24xlarge',
                        ]

                        r5dtypes = [
                            'large',
                            'xlarge',
                            '2xlarge',
                            '4xlarge',
                            '12xlarge',
                            '24xlarge',
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

                        z1dtypes = [
                            'large',
                            'xlarge',
                            '2xlarge',
                            '3xlarge',
                            '6xlarge',
                            '12xlarge',
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
                            suggestedType = 't2.{}'.format(t2types[0])

                    # Suggest Instance Types based on AVG CPU usage keeping general instance type class, current gen only
                        if typesplit[0] == 't1':
                            suggestedType = 't2.{}'.format(t2types[0])
                        elif typesplit[0] == 't2':
                            typeindex = t2types.index('{}'.format(typesplit[1]))
                            if totalAvg <=5:
                                suggestedType = '{}.{}'.format(typesplit[0], t2types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex -1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], t2types[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], t2types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], t2types[index])
                                except IndexError:
                                    suggestedType = 'm4.{}'.format(m4types[3])
                        elif typesplit[0] == 'm5':
                            typeindex = m5types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], m5types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex -1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], m5types[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], m5types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], m5types[index])
                                except IndexError:
                                    suggestedType = 'm5.{}'.format(m5types[5])
                        elif typesplit[0] == 'm5d':
                            typeindex = m5dtypes.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], m5dtypes[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], m5dtypes[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], m5dtypes[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], m5dtypes[index])
                                except IndexError:
                                    suggestedType = 'm5d.{}'.format(m5dtypes[5])
                        elif typesplit[0] == 'm4':
                            typeindex = m4types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], m4types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], m4types[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], m4types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], m4types[index])
                                except IndexError:
                                    suggestedType = 'm5.{}'.format(m5types[5])
                        elif typesplit[0] == 'm3': # PrevGen Upgrade to M5
                            typeindex = m3types.index(typesplit[1])
                            if totalAvg <= 5:
                                suggestedType = 't2.{}*'.format(t2types[2])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 2
                                if index < 0:
                                    suggestedType = 't2.{}*'.format(t2types[3])
                                else:
                                    suggestedType = 'm5.{}*'.format(m5types[index])
                            elif totalAvg > 30 <= 80:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = 'm5.{}*'.format(m5types[2])
                                else:
                                    suggestedType = 'm5.{}*'.format(m5types[index])
                            elif totalAvg > 80:
                                try:
                                    suggestedType = 'm5.{}*'.format(m5types[typeindex])
                                except IndexError:
                                    suggestedType = 'm5.{}*'.format(m5types[2])
                        elif typesplit[0] == 'm2': # PrevGen Upgrade to R4
                            typeindex = m2types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = 'r4.{}*'.format(r4types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = 'r4.{}*'.format(r4types[0])
                                else:
                                    suggestedType = 'r4.{}*'.format(r4types[index])
                            elif totalAvg > 30 <= 80:
                                index = typeindex + 1
                                suggestedType = 'r4.{}*'.format(r4types[index])
                            elif totalAvg > 80:
                                index = typeindex + 2
                                try:
                                    suggestedType = 'r4.{}*'.format(r4types[index])
                                except IndexError:
                                    suggestedType = 'r4.{}*'.format(r4types[5])
                        elif typesplit[0] == 'm1': # PrevGen Upgrade to T2
                            typeindex = m1types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = 't2.{}*'.format(t2types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = 't2.{}*'.format(t2types[0])
                                else:
                                    suggestedType = 't2.{}*'.format(t2types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = 't2.{}*'.format(t2types[typeindex])
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = 't2.{}*'.format(t2types[index])
                                except IndexError:
                                    suggestedType = 'm4.{}*'.format(m4types[3])
                        elif typesplit[0] == 'c5':
                            typeindex = c5types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], c5types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], c5types[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], c5types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], c5types[index])
                                except IndexError:
                                    suggestedType = 'c5.{}'.format(c5types[5])
                        elif typesplit[0] == 'c5d':
                            typeindex = c5dtypes.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], c5dtypes[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex -1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], c5dtypes[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], c5dtypes[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], c5dtypes[index])
                                except IndexError:
                                    suggestedType = 'c5d.{}'.format(c5dtypes[5])
                        elif typesplit[0] == 'c4':
                            typeindex = c4types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], c4types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], c4types[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], c4types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], c4types[index])
                                except IndexError:
                                    suggestedType = 'c5.{}'.format(c5types[5])
                        elif typesplit[0] == 'c3': # PrevGen Upgrade to C5
                            typeindex = c3types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = 'c5.{}*'.format(c5types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = 'c5.{}*'.format(c5types[0])
                                else:
                                    suggestedType = 'c5.{}*'.format(c5types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = 'c5.{}*'.format(c5types[typeindex])
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = 'c5.{}*'.format(c5types[index])
                                except IndexError:
                                    suggestedType = 'c5.{}*'.format(c5types[5])
                        elif typesplit[0] == 'cc2': # PrevGen Upgrade to C5
                            typeindex = cc2types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = 'c5.{}*'.format(c5types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = 'c5.{}*'.format(c5types[3])
                                else:
                                    suggestedType = 'c5.{}*'.format(c5types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = 'c5.{}*'.format(c5types[4])
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = 'c5.{}*'.format(c5types[index])
                                except IndexError:
                                    suggestedType = 'c5.{}*'.format(c5types[5])
                        elif typesplit[0] == 'cr1': # PrevGen Upgrade to R4
                            typeindex = m2types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 30:
                                suggestedType = 'r4.{}'.format(r4types[0])
                            elif totalAvg > 30 <= 80:
                                suggestedType = 'r4.{}'.format(r4types[4])
                            elif totalAvg > 80:
                                    suggestedType = 'r4.{}'.format(r4types[5])
                        elif typesplit[0] == 'c1': # PrevGen Upgrade to C5
                            typeindex = c1types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = 'c5.{}*'.format(c5types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = 'c5.{}*'.format(c5types[0])
                                else:
                                    suggestedType = 'c5.{}*'.format(c5types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = 'c5.{}*'.format(c5types[typeindex])
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = 'c5.{}*'.format(c5types[index])
                                except IndexError:
                                    suggestedType = 'c5.{}*'.format(c5types[5])
                        elif typesplit[0] == 'x1':
                            typeindex = x1types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], x1types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], x1types[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], x1types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], x1types[index])
                                except IndexError:
                                    suggestedType = 'x1e.{}'.format(x1etypes[5])
                        elif typesplit[0] == 'x1e':
                            typeindex = x1etypes.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], x1etypes[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex -1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], x1etypes[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], x1etypes[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], x1etypes[index])
                                except IndexError:
                                    suggestedType = 'x1e.{}'.format(x1etypes[5])
                        elif typesplit[0] == 'z1d':
                            typeindex = z1dtypes.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], z1dtypes[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], z1dtypes[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], z1dtypes[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], z1dtypes[index])
                                except IndexError:
                                    suggestedType = 'x1.{}'.format(x1types[0])
                        elif typesplit[0] == 'r5d':
                            typeindex = r5dtypes.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], r5dtypes[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], r5dtypes[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], r5dtypes[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], r5dtypes[index])
                                except IndexError:
                                    suggestedType = 'x1.{}'.format(x1types[0])
                        elif typesplit[0] == 'r5':
                            typeindex = r5types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], r5types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], r5types[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], r5types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], r5types[index])
                                except IndexError:
                                    suggestedType = 'x1.{}'.format(x1types[0])
                        elif typesplit[0] == 'r4':
                            typeindex = r4types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], r4types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], r4types[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], r4types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], r4types[index])
                                except IndexError:
                                    suggestedType = 'r5.{}'.format(r5types[5])
                        elif typesplit[0] == 'r3': # PrevGen Upgrade to R4
                            typeindex = r3types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = 'r4.{}*'.format(r4types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = 'r4.{}*'.format(r4types[0])
                                else:
                                    suggestedType = 'r4.{}*'.format(r4types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = 'r4.{}*'.format(r4types[typeindex])
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = 'r4.{}*'.format(r4types[index])
                                except IndexError:
                                    suggestedType = 'x1.{}*'.format(x1types[0])
                        elif typesplit[0] == 'p2':
                            typeindex = p2types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], p2types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], p2types[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], p2types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], p2types[index])
                                except IndexError:
                                    suggestedType = 'g3.{}'.format(g3types[0])
                        elif typesplit[0] == 'p3':
                            typeindex = p3types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], p3types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], p3types[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], p3types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], p3types[index])
                                except IndexError:
                                    suggestedType = 'g3.{}'.format(g3types[0])
                        elif typesplit[0] == 'g3':
                            typeindex = g3types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], g3types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], g3types[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], g3types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], g3types[index])
                                except IndexError:
                                    suggestedType = 'f1.{}'.format(f1types[1])
                        elif typesplit[0] == 'g2': # PrevGen Upgrade to G3
                            typeindex = g2types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = 'g3.{}*'.format(g3types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = 'g3.{}*'.format(g3types[0])
                                else:
                                    suggestedType = 'g3.{}*'.format(g3types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = 'g3.{}*'.format(typeindex)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = 'g3.{}*'.format(g3types[index])
                                except IndexError:
                                    suggestedType = 'f1.{}*'.format(f1types[1])
                        elif typesplit[0] == 'f1':
                            typeindex = f1types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], f1types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], f1types[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], f1types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], f1types[index])
                                except IndexError:
                                    suggestedType = 'f1.{}'.format(f1types[1])
                        elif typesplit[0] == 'hs1': # PrevGen Upgrade to d2
                            typeindex = hs1types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = 'd2.{}*'.format(d2types[0])
                            elif totalAvg > 5 <= 30:
                                    suggestedType = 'd2.{}*'.format(d2types[1])
                            elif totalAvg > 30:
                                    suggestedType = 'd2.{}*'.format(d2types[3])
                        elif typesplit[0] == 'h1':
                            typeindex = h1types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], h1types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], h1types[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], h1types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], h1types[index])
                                except IndexError:
                                    suggestedType = 'i3.{}'.format(i3types[6])
                        elif typesplit[0] == 'i3':
                            typeindex = i3types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], i3types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], i3types[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], i3types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], i3types[index])
                                except IndexError:
                                    suggestedType = 'i3.{}'.format(i3types[6])
                        elif typesplit[0] == 'i2': # PrevGen Upgread to i3
                            typeindex = i2types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = 'i3.{}*'.format(i3types[0])
                            elif totalAvg > 5 <= 30:
                                try:
                                    suggestedType = 'i3.{}*'.format(i3types[typeindex])
                                except ValueError:
                                    suggestedType = 'i3.{}*'.format(i3types[0])
                            elif totalAvg > 30 <= 80:
                                suggestedType = 'i3.{}*'.format(i3types[typeindex])
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 2
                                    suggestedType = 'i3.{}*'.format(i3types[index])
                                except IndexError:
                                    suggestedType = 'i3.{}*'.format(i3types[6])
                        elif typesplit[0] == 'd2':
                            typeindex = d2types.index('{}'.format(typesplit[1]))
                            if totalAvg <= 5:
                                suggestedType = '{}.{}'.format(typesplit[0], d2types[0])
                            elif totalAvg > 5 <= 30:
                                index = typeindex - 1
                                if index < 0:
                                    suggestedType = '{}.{}'.format(typesplit[0], d2types[0])
                                else:
                                    suggestedType = '{}.{}'.format(typesplit[0], d2types[index])
                            elif totalAvg > 30 <= 80:
                                suggestedType = '{}'.format(instanceType)
                            elif totalAvg > 80:
                                try:
                                    index = typeindex + 1
                                    suggestedType = '{}.{}'.format(typesplit[0], d2types[index])
                                except IndexError:
                                    suggestedType = 'd2.{}'.format(d2types[3])

                    except ClientError as e:
                        self.logger.error('Error getting metrics for instance {}...{}'.format(b, e))
                    except Exception as e:
                        self.logger.exception('General Exception ... {}'.format(e))

                info.append(
                    {
                        'Id': '{}'.format(instanceId),
                        'Name': '{}'.format(instanceName),
                        'AvgCpu': totalAvg,
                        'CurrentType': '{}'.format(instanceType),
                        'SuggestedType': '{}'.format(suggestedType)
                    }
                )

        return info

    def getrdssuggestions(self):
        """
        A method to suggest the right sizing for AWS RDS Instances.
        :return: (dictionary) The dictionary result of the logic.
        """
        if self.accessKey is not None:
            cwc = self._init_connection('cloudwatch')
            rdsc = self._init_connection('rds')
        else:
            cwc = self._init_profile('cloudwatch')
            rdsc = self._init_profile('rds')
        try:
            response = rdsc.describe_db_instances()
        except ClientError as e:
            self.logger.error('Failed to describe rds instances... {}'.format(e))
            return []
        except Exception as e:
            self.logger.exception('General Exception ... {}'.format(e))
            return []

        now = datetime.now()
        sTime = now - timedelta(days=self.queryDays)
        eTime = now.strftime("%Y-%m-%d %H:%M:%S")

        info = []

        for a in range(0, len(response['DBInstances'])):
            base = response['DBInstances'][a]
            try:
                DBInstanceStatus = base['DBInstanceStatus']
            except KeyError:
                self.logger.exception('RDS Instance Statue Undefined')
                return []
            except Exception as e:
                self.logger.exception('General Exception ... {}'.format(e))
                return []

            try:
                DBInstanceIdentifier = base['DBInstanceIdentifier']
            except KeyError:
                self.logger.exception('RDS Instance Id Undefined')
                return []
            except Exception as e:
                self.logger.exception('General Exception ... {}'.format(e))
                return []

            try:
                DBInstanceClass = base['DBInstanceClass']
            except KeyError:
                self.logger.exception('RDS Instance Class Undefined')
                return []
            except Exception as e:
                self.logger.exception('General Exception ... {}'.format(e))
                return []

            try:
                DBEngine = base['Engine']
            except KeyError:
                self.logger.error('RDS DB Engine Undefined')
                DBEngine = 'Undefined'
            except Exception as e:
                self.logger.exception('General Exception ... {}'.format(e))
                return []

            try:
                DBName = base['DBName']
            except KeyError:
                self.logger.info("RDS DB Name Undefined, setting to 'Undefined'")
                DBName = 'Undefined'
            except Exception as e:
                self.logger.exception('General Exception ... {}'.format(e))
                return []
            if DBInstanceStatus == 'available':
                try:
                    res = cwc.get_metric_statistics(
                        Namespace='AWS/RDS',
                        MetricName='CPUUtilization',
                        Dimensions=[
                            {
                                'Name': 'DBInstanceIdentifier',
                                'Value': '{}'.format(DBInstanceIdentifier)
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
                        typeindex = dbt2types.index('{}'.format(typesplit[2]))
                        if totalAvg <= 5:
                            suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbt2types[0])
                        elif totalAvg > 5 <= 30:
                            index = typeindex - 1
                            if index < 0:
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbt2types[0])
                            else:
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbt2types[index])
                        elif totalAvg > 30 <= 80:
                            suggestedType = '{}'.format(DBInstanceClass)
                        elif totalAvg > 80:
                            try:
                                index = typeindex + 1
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbt2types[index])
                            except IndexError:
                                suggestedType = '{}.m4.{}'.format(typesplit[0], dbm4types[3])

                    elif typesplit[1] == 't1': # PrevGen Upgrade to t2
                        suggestedType = '{}.t2.{}*'.format(typesplit[0], dbt2types[0])

                    elif typesplit[1] == 'm4':
                        typeindex = dbm4types.index('{}'.format(typesplit[2]))
                        if totalAvg <= 5:
                            suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbm4types[0])
                        elif totalAvg > 5 <= 30:
                            index = typeindex - 1
                            if index < 0:
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbm4types[0])
                            else:
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbm4types[index])
                        elif totalAvg > 30 <= 80:
                            suggestedType = '{}'.format(DBInstanceClass)
                        elif totalAvg > 80:
                            try:
                                index = typeindex + 1
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbm4types[index])
                            except IndexError:
                                suggestedType = '{}.x1e.{}'.format(typesplit[0], dbx1etypes[4])

                    elif typesplit[1] == 'm3':
                        typeindex = dbm3types.index('{}'.format(typesplit[2]))
                        if totalAvg <= 5:
                            suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbm3types[0])
                        elif totalAvg > 5 <= 30:
                            index = typeindex - 1
                            if index < 0:
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbm3types[0])
                            else:
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbm3types[index])
                        elif totalAvg > 30 <= 80:
                            suggestedType = '{}'.format(DBInstanceClass)
                        elif totalAvg > 80:
                            try:
                                index = typeindex + 1
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbm3types[index])
                            except IndexError:
                                suggestedType = '{}.m4.{}'.format(typesplit[0], dbm4types[3])

                    elif typesplit[1] == 'm2': # PrevGen Upgrade to R3
                        typeindex = dbm2types.index('{}'.format(typesplit[2]))
                        if totalAvg <= 5:
                            suggestedType = '{}.r3.{}'.format(typesplit[0], dbr3types[0])
                        elif totalAvg > 5 <= 30:
                            index = typeindex - 1
                            if index < 0:
                                suggestedType = '{}.r3.{}'.format(typesplit[0], dbr3types[0])
                            else:
                                suggestedType = '{}.r3.{}'.format(typesplit[0], dbr3types[index])
                        elif totalAvg > 30 <= 80:
                            index = typeindex
                            suggestedType = '{}.r3.{}'.format(typesplit[0], dbr3types[index])
                        elif totalAvg > 80:
                            try:
                                index = typeindex + 1
                                suggestedType = '{}.r3.{}'.format(typesplit[0], dbr3types[index])
                            except IndexError:
                                suggestedType = '{}.r3.{}'.format(typesplit[0], dbr3types[4])

                    elif typesplit[1] == 'm1': # PrevGen Upgrade to t2
                        typeindex = dbm1types.index('{}'.format(typesplit[2]))
                        if totalAvg <= 5:
                            suggestedType = '{}.t2.{}'.format(typesplit[0], dbt2types[0])
                        elif totalAvg > 5 <= 30:
                            index = typeindex - 1
                            if index < 0:
                                suggestedType = '{}.t2.{}'.format(typesplit[0], dbt2types[0])
                            else:
                                suggestedType = '{}.t2.{}'.format(typesplit[0], dbt2types[index])
                        elif totalAvg > 30 <= 80:
                            index = typeindex + 1
                            suggestedType = '{}.t2.{}'.format(typesplit[0], dbt2types[index])
                        elif totalAvg > 80:
                            try:
                                index = typeindex + 1
                                suggestedType = '{}.t2.{}'.format(typesplit[0], dbt2types[index])
                            except IndexError:
                                suggestedType = '{}.t2.{}'.format(typesplit[0], dbt2types[3])

                    elif typesplit[1] == 'r4':
                        typeindex = dbr4types.index('{}'.format(typesplit[2]))
                        if totalAvg <= 5:
                            suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbr4types[0])
                        elif totalAvg > 5 <= 30:
                            index = typeindex - 1
                            if index < 0:
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbr4types[0])
                            else:
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbr4types[index])
                        elif totalAvg > 30 <= 80:
                            suggestedType = '{}'.format(DBInstanceClass)
                        elif totalAvg > 80:
                            try:
                                index = typeindex + 1
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbr4types[index])
                            except IndexError:
                                suggestedType = '{}.x1e.{}'.format(typesplit[0], dbx1etypes[4])

                    elif typesplit[1] == 'r3':
                        typeindex = dbr3types.index('{}'.format(typesplit[2]))
                        if totalAvg <= 5:
                            suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbr3types[0])
                        elif totalAvg > 5 <= 30:
                            index = typeindex - 1
                            if index < 0:
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbr3types[0])
                            else:
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbr3types[index])
                        elif totalAvg > 30 <= 80:
                            suggestedType = '{}'.format(DBInstanceClass)
                        elif totalAvg > 80:
                            try:
                                index = typeindex + 1
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbr3types[index])
                            except IndexError:
                                suggestedType = '{}.r4.{}'.format(typesplit[0], dbr4types[5])

                    elif typesplit[1] == 'x1e':
                        typeindex = dbx1etypes.index('{}'.format(typesplit[2]))
                        if totalAvg <= 5:
                            suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbx1etypes[0])
                        elif totalAvg > 5 <= 30:
                            index = typeindex - 1
                            if index < 0:
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbx1etypes[0])
                            else:
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbx1etypes[index])
                        elif totalAvg > 30 <= 80:
                            suggestedType = '{}'.format(DBInstanceClass)
                        elif totalAvg > 80:
                            try:
                                index = typeindex + 1
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbx1etypes[index])
                            except IndexError:
                                suggestedType = '{}.x1e.{}'.format(typesplit[0], dbx1etypes[5])

                    elif typesplit[1] == 'x1':
                        typeindex = dbx1types.index('{}'.format(typesplit[2]))
                        if totalAvg <= 5:
                            suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbx1types[0])
                        elif totalAvg > 5 <= 30:
                            index = typeindex -1
                            if index < 0:
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbx1types[0])
                            else:
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbx1types[index])
                        elif totalAvg > 30 <= 80:
                            suggestedType = '{}'.format(DBInstanceClass)
                        elif totalAvg > 80:
                            try:
                                index = typeindex + 1
                                suggestedType = '{}.{}.{}'.format(typesplit[0], typesplit[1], dbx1types[index])
                            except IndexError:
                                suggestedType = '{}.x1e.{}'.format(typesplit[0], dbx1etypes[5])

                except ClientError as e:
                    self.logger.error('Error getting metrics for instance {}...{}'.format(a, e))
                except Exception as e:
                    self.logger.exception('General Exception ... {}'.format(e))

            info.append(
                {
                    'Id': '{}'.format(DBInstanceIdentifier),
                    'Name': '{}'.format(DBName),
                    'Engine': '{}'.format(DBEngine),
                    'AvgCpu': totalAvg,
                    'CurrentType': '{}'.format(DBInstanceClass),
                    'SuggestedType': '{}'.format(suggestedType)
                }
            )

        return info
