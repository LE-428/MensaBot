# MensaBot

### Get a mail when your favorite meals are on the menu of your local cantina

## Setup

You need to have the following values ready as environment variables:
+ SENDER

Mail address of the sending account

+ PASSWORD

Password or API-key of the mail-sending account

+ RECIPIENT

Mail address of the receiving account

+ MAIL_SERVER
+ MAIL_PORT

Mail host address (e.g. "live.smtp.mailtrap.io", "smtp-mail.outlook.com", ...)
and the port of the mail server (e.g. 587)

+ USER

Only needed if you log in with an API key, otherwise your sender address will be copied;
when using Mailtrap.io, set to "api"

+ DOC_ID

Google Doc ID, this is the place where you store your wishes as csv, must be set to publicly accessible

+ PROJECT_ID
+ PRIVATE_KEY_ID
+ PRIVATE_KEY
+ CLIENT_EMAIL
+ CLIENT_ID
+ CLIENT_URL

These are values from the service_account_credentials.json file that you get when you create an API key under a Google service account