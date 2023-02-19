# wallofrecords
Display your Discogs collection in Amazon S3

Prerequisites:
1. Discogs account
2. Discogs collection (the more items the better this will look)
3. Discogs API key
4. An AWS account with `awscli` configured
4. terraform

Instructions:
1. modify `main.tf` such that `resource "aws_lambda_function"` has the correct Discogs `USER_NAME` and `USER_API_KEY`.
2. terraform plan
3. terraform apply

Notes:
I have no clue how much this will cost but the lambda only fires once per day on its default cron schedule.  I set up a cost alarm for my billing tolerance and called it a day.

[Live demo here!](https://album-photos-gvqelm.s3.amazonaws.com/index.html)