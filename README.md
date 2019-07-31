# Serverless lambda function to calculate aspect scores of a hotel

[![Build Status](https://travis-ci.org/Prasannads/serverless-hotel-aspect-score-calculator.svg?branch=master)](https://travis-ci.org/Prasannads/serverless-hotel-aspect-score-calculator)

# Overview of this Lambda Function.

The purpose of the lambda function is aggregate aspect scores of a hotel whenever there is new/updated/deleted aspect score of a hotel

### Flow

1. It triggers on S3 event
2. Aggregate scores per aspect for a hotel
3. Inserts/updates/deletes the scores in dynamodb

### Architecure

The following resources will be created on deploying the function

1. S3 event notification
2. Lambda Role
3. Lambda Function
4. Dynamodb ( with AutoScaling )
5. Dynamodb Scaling Role

# How to run this application

Note: This project includes AWS Lambda layer as part of the lambda function . Ideally , it is not a good practice to have it tightly coupled with the lambda function.

### Step1 : Download packages which are going to be part of lambda layer 

```
$ cd layers/pandas_boto3
$ ./get_layer_packages.sh
```

This will download the packages required to be part of lambda layer . Please make sure that Docker is installed in your system to run this shell script

### Step2 : Install serverless using npm 

Please make sure that npm is installed.

```
$ npm install -g serverless
```

### Step3 : Deploy lambda function using serverless

Before deploying the lambda function using serverless framework , make sure that `serverless.yml` file is updated with respective AWS account number and S3 bucket names ( or any other infra related )

```
$ sls deploy -v --stage staging
```

This will deploy with lambda function onto AWS and will also create CF for resources mentioned in resources part of serverless.yml file.

It is important to note that serverless has no provision to omit resources during the further deployments ( lets say , we changed some logic in lambda function and deploying the lambda changes ) .In that case, it is going to throw us an error that the resources already exist . So , it would be better to deploy only lambda functions in such cases , using the following command ,

```
$ serverless deploy function --function {function-name} --update-config
```
