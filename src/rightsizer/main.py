# Standard Library Imports
import csv
import sys
from logging import DEBUG, WARNING
from datetime import datetime

# Third-party Imports
import click

# Local Imports
from .AwsRightSizer import Main


def print_help(ctx, param, value):
    if value is False:
        return
    click.echo(ctx.get_help())
    ctx.exit()

@click.command()
@click.option('--profile', '-p', 'profile', default='default', required=False, help='Your AWS Credentials Profile.')
@click.option('--access-key', '-k', 'accessKey', default=None, required=False, help='Your AWS Access Key ID.')
@click.option('--secret-key', '-s', 'secretKey', default=None, required=False, help='Your AWS Secret Access Key ID.')
@click.option('--region', '-r', 'region', default=None, required=False, help='The AWS Region to query.')
@click.option('--threshold', '-t', 'threshold', nargs=2, type=int, default=[5, 30], required=False, help='The Cloudwatch [average, max] CPU usage threshold.')
@click.option('--query-config', '-q', 'query', nargs=2, type=int, default=[30, 1800], required=False, help='The amount of [days, period] to query Cloudwatch for.')
@click.option('--output', '-o', 'output', default='report_()'.format(datetime.date(datetime.now())), help='The Name/Location of the file to output.')
@click.option('--ec2-only', '-e', 'ec2only', is_flag=True)
@click.option('--rds-only', '-d', 'rdsonly', is_flag=True)
@click.option('--verbose', '-v', 'verbose', is_flag=True)
@click.option('--help', '-h', is_flag=True, expose_value=False, is_eager=False, callback=print_help, help='Print help message')
@click.pass_context
def main(ctx, profile, accessKey, secretKey, region, threshold, query, output, ec2only, rdsonly, verbose):
    """
    rightsizer takes user input and provides an output CSV of suggestions.
    """
    if len(sys.argv) <= 1:
        print_help(ctx, None, value=True)

    if verbose:
        v = DEBUG
    else:
        v = WARNING

    x = Main(
        accessKey=accessKey,
        secretKey=secretKey,
        region=region,
        profile=profile,
        thresholdAvg=threshold[0],
        thresholdMax=threshold[1],
        queryDays=query[0],
        queryPeriod=query[1],
        output=output,
        verbose=v)

    if ec2only:

        if profile:
            pf = profile

        else:
            pf = region

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

    elif rdsonly:

        if profile:

            pf = profile

        else:

            pf = region

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

        if profile:

            pf = profile

        else:

            pf = region

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