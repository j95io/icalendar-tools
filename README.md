# icalendar-tools

Generate a reply to an iCalendar invitation file.

More tools, e.g., for cancelling appointments as an organizer may come in the future.

## Dependencies

- Python >= 3.10
- [icalendar](https://pypi.org/project/icalendar/) >= 5.0  (Can be installed via pip)

## Replying to an _iCalendar_ Invitation

Use `icalendar_reply.py` to generate a reply to a calendar invitation in iCalendar format (.ics)

- You can accept, decline, or tentatively accept an invitation.  
  --> Prints reply in ics format to stdout.   
  Use this text as an inline attachment in a response email to let an organizer know if you are available for their event.
  
- You can also just query the invitation file to check whether a reply is needed from you.  
  --> Exits with no error if reply is needed from you, otherwise exits with an error.
  
### Usage

```
python icalendar_reply.py [-h] [-v] -e MY_EMAIL_ADDRESSES {accept,decline,tentative,query} invitation_filename
```

__Examples:__

```python icalendar_reply.py --help``` 

```python icalendar_reply.py -e me@mail.com accept invite.ics``` 

```python icalendar_reply.py -e me@mail.com,also_me@email.org tentative invite.ics``` 

```python icalendar_reply.py -e me@mail.com,also_me@email.org query invite.ics```

