# Follow Up Reminder

This program reminds you to follow up to emails you sent but haven't heard back about

## Roadmap

1. Access email using Gmail API
2. Store threads where the last email is one that user has sent. Store the email id and date it was sent in an external file)
3. Iterate through emails in external file: delete ones that have received replies, and store ones that were sent more than x days ago (x should be defined by user, default to 7)
4. Iterate through new stored emails and notify the user to follow up (how? Another email?)
5. Set up a cron job to do steps 1-4 every day
