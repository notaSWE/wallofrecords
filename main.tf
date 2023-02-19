provider "aws" {
  region = "us-east-1"
}

data "aws_caller_identity" "current" {}

output "aws_account_id" {
  value = data.aws_caller_identity.current.account_id
}

resource "random_string" "bucket_suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "aws_s3_bucket" "album_photos" {
  bucket = "album-photos-${random_string.bucket_suffix.result}"
  tags = {
    Name = "Album Photos"
  }
}

resource "aws_s3_bucket_cors_configuration" "album_photos" {
  bucket = "album-photos-${random_string.bucket_suffix.result}"

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_website_configuration" "album_phtos" {
  bucket = "album-photos-${random_string.bucket_suffix.result}"

  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_object" "thumbs_directory" {
  bucket = aws_s3_bucket.album_photos.id
  key    = "thumbs/"
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "lambda_exec_attach" {
  name       = "lambda_exec_attach"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  roles      = [aws_iam_role.lambda_exec.name]
}

resource "aws_lambda_function" "gather_discogs_collection" {
  filename         = "lambda_function.zip"
  function_name    = "gather-discogs-collection"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "index.handler"
  runtime          = "python3.9"
  timeout          = 60
  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.album_photos.bucket
      USER_NAME = ""
      USER_API_KEY = ""
    }
  }
}

resource "aws_iam_policy" "lambda_s3_policy" {
  name        = "lambda-s3-policy"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "VisualEditor0"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.album_photos.arn}",
          "${aws_s3_bucket.album_photos.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_policy_attachment" {
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
  role       = aws_iam_role.lambda_exec.name
}

resource "aws_cloudwatch_event_rule" "download_albums" {
  name                = "download_albums"
  description         = "Trigger Lambda function every day at Noon UTC"
  schedule_expression = "cron(0 12 * * ? *)" # Noon UTC
}

resource "aws_cloudwatch_event_target" "lambda_trigger" {
  rule      = aws_cloudwatch_event_rule.download_albums.name
  target_id = "GatherDiscogsCollectionTarget"
  arn       = aws_lambda_function.gather_discogs_collection.arn
}

# Grant the CloudWatch Event Rule permission to invoke the Lambda function
resource "aws_lambda_permission" "lambda_permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.gather_discogs_collection.function_name
  principal     = "events.amazonaws.com"

  source_arn = aws_cloudwatch_event_rule.download_albums.arn
}

resource "aws_s3_bucket_policy" "album_photos_policy" {
  bucket = aws_s3_bucket.album_photos.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "AllowLambdaToGetObject"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/lambda-exec-role"
        }
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.album_photos.arn}/*"
      },
      {
        Sid = "AllowAllUsersToReadBucket"
        Effect = "Allow"
        Principal = "*"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.album_photos.arn}/*",
          "${aws_s3_bucket.album_photos.arn}"
        ]
      }
    ]
  })
}
