# AWS S3 Setup Instructions for Image Uploads

## Overview
 uses AWS S3 for storing article images. When users create articles and upload images, they are automatically stored in your S3 bucket.

## Prerequisites
- AWS Account
- AWS S3 bucket created
- IAM user with S3 permissions

## Step 1: Create S3 Bucket

1. Log in to AWS Console
2. Navigate to S3 service
3. Click "Create bucket"
4. Bucket name: `-images` (or your preferred name)
5. Region: Choose your preferred region (e.g., `us-east-1`)
6. **Block Public Access**: Uncheck "Block all public access" (or configure bucket policy for public read)
7. Click "Create bucket"

## Step 2: Configure Bucket Policy (for Public Read Access)

If you want images to be publicly accessible, add this bucket policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::-images/*"
        }
    ]
}
```

**Note**: Replace `-images` with your actual bucket name.

## Step 3: Create IAM User for S3 Access

1. Go to IAM Console → Users → Add users
2. Username: `-s3-user`
3. Access type: "Programmatic access"
4. Click "Next: Permissions"
5. Attach policies: Select "AmazonS3FullAccess" (or create custom policy with only necessary permissions)
6. Click "Next" → "Create user"
7. **IMPORTANT**: Save the Access Key ID and Secret Access Key

## Step 4: Configure .env File

Update your `backend/.env` file with S3 credentials:

```env
# AWS S3 Configuration (for image storage)
AWS_ACCESS_KEY_ID=your_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
AWS_S3_BUCKET_NAME=-images
AWS_S3_REGION=us-east-1
AWS_S3_CUSTOM_DOMAIN=  # Optional: CloudFront distribution domain
```

## Step 5: Test the Setup

1. Start your backend server
2. Login as admin
3. Go to "Create Article" page
4. Try uploading an image
5. Check your S3 bucket - you should see the uploaded image

## Optional: CloudFront Setup (for CDN)

For better performance and lower costs:

1. Create CloudFront distribution
2. Origin: Your S3 bucket
3. Get the CloudFront domain URL
4. Add to `.env`: `AWS_S3_CUSTOM_DOMAIN=your-cloudfront-domain.cloudfront.net`

## Security Best Practices

1. **Never commit `.env` file** to version control
2. Use IAM roles instead of access keys when possible (for EC2/ECS)
3. Limit IAM user permissions to only S3 bucket access
4. Enable S3 bucket versioning for backup
5. Set up S3 lifecycle policies to manage old images

## Troubleshooting

### Error: "S3 is not configured"
- Check that all S3 environment variables are set in `.env`
- Verify credentials are correct
- Ensure bucket name matches exactly

### Error: "Access Denied"
- Check IAM user has S3 permissions
- Verify bucket policy allows uploads
- Check bucket region matches `AWS_S3_REGION`

### Images not displaying
- Verify bucket policy allows public read access
- Check image URLs are correct
- Verify CORS settings if accessing from different domain

## Custom IAM Policy (Minimal Permissions)

Instead of full S3 access, use this custom policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::-images/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::-images"
        }
    ]
}
```

Replace `-images` with your bucket name.
