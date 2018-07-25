import sys
import csv
import argparse
from datetime import datetime
from . import logger
from .AwsRightSizer import Main


def main():
    """
    The primary method that provides two CSV output files (EC2/RDS) with suggestions.
    :return: (none): This method does not return anything, it only creates the two CSV file objects.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--profile',
        dest='profile',
        help='AWS Credentials Profile',
        default='default',
        required=False
    )
    parser.add_argument(
        '-k', '--access-key',
        dest='accessKey',
        help='AWS Access Key Id',
        default=None,
        required=False
    )
    parser.add_argument(
        '-s', '--secret-key',
        dest='secretKey',
        help='AWS Secret Access Key',
        default=None,
        required=False
    )
    parser.add_argument(
        '-r', '--region',
        dest='region',
        help='AWS Region',
        default=None,
        required=False
    )
    parser.add_argument(
        '-t', '--threshold',
        nargs=2,
        dest='threshold',
        help='The Cloudwatch [average, max] CPU usage threshold',
        default=[5, 30],
        required=False
    )
    parser.add_argument(
        '-q', '--query-config',
        dest='query',
        help='The amount of [days, period] to query Cloudwatch for',
        default=[30, 1800],
        required=False
    )
    parser.add_argument(
        '-o', '--output',
        dest='output',
        help='The name/location of the csv file to output',
        default='report_{}.csv'.format(datetime.date(datetime.now()))
    )
    parser.add_argument(
        '-e', '--ec2-only',
        action='store_true',
        dest='ec2only',
        help='Run this tool against EC2 Instances only',
    )
    parser.add_argument(
        '-d', '--rds-only',
        action='store_true',
        dest='rdsonly',
        help='Run this tool against RDS Instances only',
    )
    args = parser.parse_args()

    x = Main(
        accessKey=args.accessKey,
        secretKey=args.secretKey,
        region=args.region,
        profile=args.profile,
        thresholdAvg=args.threshold[0],
        thresholdMax=args.threshold[1],
        queryDays=args.query[0],
        queryPeriod=args.query[1],
        output=args.output
    )
    if args.ec2only:
        if args.profile:
            pf = args.profile
        else:
            pf = args.region
        extra = {
            'Id': '* - AWS Suggested Upgrade'
        }
        with open('{}_ec2_'+'{}'.format(pf, x.output), 'w', newline='') as f:
            fieldnames = [
                'Id',
                'Name',
                'AvgCpu',
                'CurrentType',
                'SuggestedType'
            ]
            w = csv.DictWriter(f, fieldnames)
            w.writeheader()
            for r in x.getec2suggestions():
                w.writerow(r)
            csv.writer(f).writerow('')
            w.writerow(extra)
    elif args.rdsonly:
        if args.profile:
            pf = args.profile
        else:
            pf = args.region
        extra = {
            'Id': '* - AWS Suggested Upgrade'
        }
        with open('{}_rds_'+'{}'.format(pf, x.output), 'w', newline='') as f:
            fieldnames = [
                'Id',
                'Name',
                'Engine',
                'AvgCpu',
                'CurrentType',
                'SuggestedType'
            ]
            w = csv.DictWriter(f, fieldnames)
            w.writeheader()
            for r in x.getrdssuggestions():
                w.writerow(r)
            csv.writer(f).writerow('')
            w.writerow(extra)
    else:
        if args.profile:
            pf = args.profile
        else:
            pf = args.region
        extra = {
            'Id': '* - AWS Suggested Upgrade'
        }

        with open('{}_ec2_' + '{}'.format(pf, x.output), 'w', newline='') as f:
            fieldnames = [
                'Id',
                'Name',
                'AvgCpu',
                'CurrentType',
                'SuggestedType'
            ]
            w = csv.DictWriter(f, fieldnames)
            w.writeheader()
            for r in x.getec2suggestions():
                w.writerow(r)
            csv.writer(f).writerow('')
            w.writerow(extra)

        with open('{}_rds_' + '{}'.format(pf, x.output), 'w', newline='') as f:
            fieldnames = [
                'Id',
                'Name',
                'Engine',
                'AvgCpu',
                'CurrentType',
                'SuggestedType'
            ]
            w = csv.DictWriter(f, fieldnames)
            w.writeheader()
            for r in x.getrdssuggestions():
                w.writerow(r)
            csv.writer(f).writerow('')
            w.writerow(extra)