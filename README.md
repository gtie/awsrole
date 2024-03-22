Easy login to AWS through the command-line.

## Usage
The project assumes you have:
  1. An IAM account and credentials present in your environment (e.g. `~/.aws/credentials`)
  2. Permissions for the IAM account to assume a given role
  3. The name of the role you want to assume

With the above in place you can get temporary credentials and a web UI login link,
granting you all of the powers of the assumed role by running:
```
$ awsrole MyRole
# Export following vars in your shell for API/CLI access:
    export AWS_ACCESS_KEY_ID=ASI...
    export AWS_SECRET_ACCESS_KEY=10q2I...
    export AWS_SESSION_TOKEN=Fwo......

# Login URL: https://signin.aws.amazon.com/federation?Action=login......
```
Clicking on/opening the URL in the browser will land you in a preauthenticated session. Copy/pasting
the export commands in your shell would enable CLI utilities from using the role's credentials.

The temporary credentials would be valid for up to 12h (max and default value)

There is no separate argument for using a non-default AWS login profile, but that can be easily
configured by overriding the `AWS_PROFILE` variable on the command line as in:
```
$ AWS_PROFILE=profile2 awsrole MyRole
```
## Installation
```
pip install awsrole
```

## Help
```
$ awsrole --help
usage: awsrole [-h] [-a ACCOUNT] [-t TIME] role

Generate temporary credentials and Login URL for a given AWS role.

positional arguments:
  role                  Role to assume

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT, --account ACCOUNT
                        Specify an account ID, instead of auto-discovering it
  -t TIME, --time TIME  Temp credentials validity in seconds (default: 43200)
```

