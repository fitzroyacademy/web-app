sudo apt-get install -y jq awscli
unset AWS_SESSION_TOKEN
assumed_role=$(aws sts assume-role --role-arn "arn:aws:iam::593798515196:role/CircleCICrossAccountRole" --role-session-name "circleci-sandbox")
export AWS_ACCESS_KEY_ID=$(echo $assumed_role | jq -r .Credentials.AccessKeyId)
export AWS_SECRET_ACCESS_KEY=$(echo $assumed_role | jq -r .Credentials.SecretAccessKey)
export AWS_SESSION_TOKEN=$(echo $assumed_role | jq -r .Credentials.SessionToken)