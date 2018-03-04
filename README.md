# Follow Up Reminder

This program reminds you to follow up to emails you sent but haven't heard back about. It finds the emails you sent 1-2 weeks ago that nobody's responded to, and applies the "Follow Up" label to them.

## Installation

First, generate credentials for the Gmail API by following [these instructions](https://developers.google.com/gmail/api/quickstart/python#step_1_turn_on_the_api_name)

To run the script and find emails from the past 1-2 weeks, you can run:
```
python main.py
```

To make the program run automatically every week, you can set up a cron job to execute the script.