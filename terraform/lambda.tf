
resource "aws_s3_bucket" "this" {

    bucket        = "${var.internal_store_s3_bucket_name}"
    acl           = "private"
    force_destroy = true

    versioning {
      enabled = true
    }
    tags {
        Name = "DockerfileGeneratorInternalStore-${var.internal_store_s3_bucket_name}"
        Env  = "Production"
        Serverless  = "True"
    }

}


resource "aws_iam_role" "this" {
  name = "DockerfileGeneratorRole"
  assume_role_policy = <<EOF
{
"Version": "2012-10-17",
"Statement": [
  {
    "Action": "sts:AssumeRole",
    "Principal": {
      "Service": "lambda.amazonaws.com"
    },
    "Effect": "Allow",
    "Sid": ""
  }]
}
EOF
}


resource "aws_iam_role_policy" "s3_bucket_policy" {
  name = "DockefileGeneratorS3BucketPolicyPolicy"
  role = "${aws_iam_role.this.id}"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
      {
          "Sid": "S3BucketReadWriteAllow",
          "Effect": "Allow",
          "Action": [
            "s3:PutObject",
            "s3:GetObject" ],
          "Resource": ["${aws_s3_bucket.this.arn}/*"]
      }
  ]
}
EOF
}

resource "aws_iam_role_policy" "lambda_allow_cloudwatch_logs" {
  name = "DockerfileGeneratorCloudWatchLogsPolicy"
  role = "${aws_iam_role.this.id}"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
      {
          "Effect": "Allow",
          "Action": [
              "logs:CreateLogGroup",
              "logs:CreateLogStream",
              "logs:PutLogEvents"
          ],
          "Resource": "*"
      }
  ]
}
EOF
}


resource "null_resource" "prepare-lambda-zip" {

  triggers {
    value = "${uuid()}"
  }

  provisioner local-exec {
    command = "/bin/sh scripts/setup_lambda_package.sh"
  }

}


data "archive_file" "lambda_zip" {
    depends_on = ["null_resource.prepare-lambda-zip"]
    type = "zip"
    source_dir = "/tmp/dockerfilegenerator"
    output_path = "/tmp/dockerfilegenerator.zip"
}


resource "aws_lambda_function" "this" {
    depends_on        = ["null_resource.prepare-lambda-zip"]
    filename          = "/tmp/dockerfilegenerator.zip"
    function_name     = "DockerfileGenerator"
    role              = "${aws_iam_role.this.arn}"
    handler           = "lambda_function.lambda_handler"
    runtime           = "python3.6"
    source_code_hash  = "${data.archive_file.lambda_zip.output_base64sha256}"
    timeout           = 60
    environment {
       variables = {
         github_access_token = "${var.github_access_token}"
         dockerfile_github_repository = "${var.dockerfile_github_repository}"
         internal_s3_bucket = "${var.internal_store_s3_bucket_name}"
       }
    }
}


resource "aws_cloudwatch_event_rule" "this" {
    description = "CloudWatch Events Periodic Trigger for Dockerfile Generator Lambda "
    name = "cloudwatch-event-schedule-rule"
    schedule_expression = "rate(5 minutes)"
    is_enabled = "${var.enable_periodic_trigger}"
}


resource "aws_cloudwatch_event_target" "this" {
  rule = "${aws_cloudwatch_event_rule.this.name}"
  target_id = "InvokeLambda"
  arn = "${aws_lambda_function.this.arn}"
}


resource "aws_lambda_permission" "scheduled_lambda_cloudwatch_permission" {
  statement_id = "AllowExecutionFromCloudWatch"
  action = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.this.arn}"
  principal = "events.amazonaws.com"
  source_arn = "${aws_cloudwatch_event_rule.this.arn}"
}
