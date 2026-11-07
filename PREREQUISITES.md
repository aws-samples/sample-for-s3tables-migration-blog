## Prerequisites

For this walkthrough, you must have the following prerequisites:

- An AWS account with permissions to create Amazon S3 buckets, S3 table buckets, IAM roles and policies, AWS CloudFormation stacks, Amazon EMR Serverless application, and AWS Glue Data Catalog databases and tables. 
- The AWS Command Line Interface (AWS CLI) version 2.39.4 or later, installed and configured. Earlier versions don't include the s3tables migration commands. 
- Access to Amazon EMR Serverless and Amazon Athena in the us-east-1 AWS Region.
- An S3 bucket for the data-generation script, passed to the CloudFormation stack as `ScriptBucketName`. The stack also writes the data bucket's server access logs to this bucket. Set it up as follows.

### Prepare the script bucket

Create the bucket in the same account and Region as the stack, and upload the Spark script:

```bash
export ACCOUNT_ID=<your-account-id>
export AWS_REGION=us-east-1
export SCRIPT_BUCKET="migration-blog-src-${ACCOUNT_ID}"

aws s3 mb "s3://${SCRIPT_BUCKET}" --region "${AWS_REGION}"

aws s3api put-public-access-block --bucket "${SCRIPT_BUCKET}" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

aws s3 cp emr-s-create-tpcds-parquet-datasets.py \
  "s3://${SCRIPT_BUCKET}/scripts/emr-s-create-tpcds-parquet-datasets.py"
```

The bucket must use SSE-S3 encryption (the default for new buckets), because server access logging doesn't support SSE-KMS on the destination bucket.

Allow S3 log delivery to write the data bucket's access logs under the `data-bucket/` prefix, and deny requests that don't use TLS. This command replaces the bucket's whole policy, so check for an existing one first:

```bash
aws s3api get-bucket-policy --bucket "${SCRIPT_BUCKET}" 2>&1
```

If that returns a policy, add the two statements below to it rather than overwriting it. If it returns `NoSuchBucketPolicy`, apply this policy:

```bash
cat > /tmp/script-bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::${SCRIPT_BUCKET}",
        "arn:aws:s3:::${SCRIPT_BUCKET}/*"
      ],
      "Condition": { "Bool": { "aws:SecureTransport": false } }
    },
    {
      "Sid": "AllowS3ServerAccessLogDelivery",
      "Effect": "Allow",
      "Principal": { "Service": "logging.s3.amazonaws.com" },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::${SCRIPT_BUCKET}/data-bucket/*",
      "Condition": {
        "ArnLike": { "aws:SourceArn": "arn:aws:s3:::migration-blog-testdata-${ACCOUNT_ID}" },
        "StringEquals": { "aws:SourceAccount": "${ACCOUNT_ID}" }
      }
    }
  ]
}
EOF

aws s3api put-bucket-policy --bucket "${SCRIPT_BUCKET}" \
  --policy file:///tmp/script-bucket-policy.json && rm /tmp/script-bucket-policy.json
```

Pass the bucket to the stack with `--parameter-overrides ScriptBucketName="${SCRIPT_BUCKET}"`. The bucket isn't deleted with the stack, so the access logs remain after teardown. Remove the bucket yourself when you no longer need the script or the logs.
