# AWS EC2/RDS Instance Right-Sizer

This tool is designed and written in Python 3.6.5 to help you determine the right AWS EC2/RDS instance type for your servers based on historical usage.

## Usage:

```
usage: rightsizer.py [-h] [-p PROFILE] [-k ACCESSKEY] [-s SECRETKEY]
                     [-r REGION] [-t THRESHOLD THRESHOLD] [-q QUERY]
                     [-o OUTPUT] [-e] [-d]

optional arguments:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        AWS Credentials Profile
  -k ACCESSKEY, --access-key ACCESSKEY
                        AWS Access Key Id
  -s SECRETKEY, --secret-key SECRETKEY
                        AWS Secret Access Key
  -r REGION, --region REGION
                        AWS Region
  -t THRESHOLD THRESHOLD, --threshold THRESHOLD THRESHOLD
                        The Cloudwatch [average, max] CPU usage threshold
  -q QUERY, --query-config QUERY
                        The amount of [days, period] to query Cloudwatch for
  -o OUTPUT, --output OUTPUT
                        The name/location of the csv file to output
  -e, --ec2-only        Run this tool against EC2 Instances only
  -d, --rds-only        Run this tool against RDS Instances only

```

## Installation:
A pip package is available for this tool. This is the recommended way to install and run the tool. Download and run the tool using the steps below:

1. ```python3 -m pip install awsrightsizer --user```

2. ```rightsizer [OPTIONS]```

## Source Installation:
This tool is best run in a virtual environment. You may need to install a virtual environment tool such as python3-venv or python3-virutalenv via your package manager and/or install one via pip by running ```pip install virtualenv --user```.

1. ```git clone https://github.com/gregoryjordanm/awsrightsizer.git```

2. ```cd ./awsrightsizer```

3. ```python3 -m venv venv``` or ```virtualenv -p python3 venv```

4. ```. ./venv/bin/activate```

5. ```pip install -r requirements```

6. ```python rightsizer.py [OPTIONS]```

## Running Example:

Lets assume for a second that you have already installed the AWS CLI tools for your distribution...

Lets also assume that you have already run the ```aws configure``` command and have a profile named "dev" on your system that you have already tested and is functioning :)

To run this tool with your working profile, simply do the following:

```rightsizer -p dev```

The tool will output a "report_*date*.csv" file in the directory you ran it in.

Lets now assume that you hate my report name, simply run:

```rightsizer -p dev -o your_awesome_new_csv.csv```

The tool will now use your_awesome_new_csv.csv is the output file.

If you don't have an AWS profile set up for some reason (it really does make life easier), then you can use the -k, -s. and -r flags to provide the necessary info.

```rightsizer -k XXXXXXXXXXXX -s XXXXXXXXXXXXXXXXXXXXXXXX -r us-east-1```

If you don't want to have the tool pull 30 days worth of data, or if you don't want the data periods to be 30 minutes, use the -q flag like so:

```rightsizer -p dev -q 15,900```

This will tell the tool to query 15 days at 15 minute intervals.

To run against just your EC2 assets, just issue the -e flag.

To run against just your RDS assets, just issue the -d flag.

If you are running this via the source, you will need to add ```python rightsizer.py``` to your command instead of just ```rightsizer```. 

Let me know if you find bugs :)

### Attribution:

This tools is loosely based on the [awsstats](https://github.com/FittedCloud/awsstats) tool by [FittedCloud](https://www.fittedcloud.com/).

