# wallofrecords
Display your Discogs collection in Amazon S3

## Prerequisites:
1. Discogs account
2. Discogs collection (the more items the better this will look)
3. Discogs API key
4. An AWS account with `awscli` configured
4. terraform

## Instructions:
1. modify `main.tf` such that `resource "aws_lambda_function"` has the correct Discogs `USER_NAME` and `USER_API_KEY`.
2. `cd lambda_functions`
3. `pip install -r requirements.txt -t .`
4. `zip -r lambda_function.zip .`
5. `cd ..`
2. terraform plan
3. terraform apply

## Local Option (no terraform/AWS required)
1. Add Discogs Username/API key to `local_option/get_collection.py`
2. `python3 local_option/get_collection.py`
3. `python3 -m http.server`
4. Browse to `127.0.0.1:8000/index.html` in a browser

Notes:
I have no clue how much the AWS infrastructure will cost but the lambda only fires once per day on its default cron schedule.  I set up a cost alarm for my billing tolerance and called it a day.

[Live demo here!](https://album-photos-1o92pn.s3.amazonaws.com/index.html)