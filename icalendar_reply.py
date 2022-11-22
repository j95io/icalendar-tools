#!/usr/bin/python

import argparse
import logging
import datetime
import sys

try:
    import icalendar
except ModuleNotFoundError:
    print("The Python module 'icalendar' is required to run this script", file=sys.stderr)
    sys.exit(1)

description = """
With this tool you can do the following with an iCalendar (ics) invitation file:
Generate a reply in ics format OR query to see if a reply is being demanded from you.
"""

parser = argparse.ArgumentParser(
                    prog = 'icalendar_reply.py',
                    description = description,
                    epilog = 'https://github.com/j95io/icalendar-tools')

parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument(dest='action', choices=['accepted','declined','tentative', 'delegated', 'query'])
parser.add_argument('invitation_filename', help='Name of the file containing the event in iCalendar (ics) format')
parser.add_argument('-e', '--my_email_addresses', dest='my_email_addresses',
                    help="Your email address or multiple of your email adresses separated by ','", required=True)



def get_event(calendar):
    events = [sc for sc in calendar.subcomponents if type(sc) == icalendar.cal.Event]
    match len(events):
        case 0:
            logging.error("No VEVENT found in the calendar file!")
            sys.exit(1)
        case 1:
            return events[0]
        case _:
            logging.error("More than one VEVENT found in the calendar file!")
            sys.exit(1)

def edit_attendee_status(attendee, action):
    attendee.params.pop('RSVP')
    attendee.params['PARTSTAT'] = action
    return attendee


def get_attendees(event):
    if 'ATTENDEE' not in event:
        logging.warning('No attendees found in the event!')
        return []
    attendees = event['ATTENDEE']
    if type(attendees) != list:  # "If only one attendee in invitation file"
        attendees = [attendees]
    return attendees


def is_me(attendee, my_email_addresses):
    for my_email_address in my_email_addresses:
        if my_email_address.lower() in attendee.lower():
            return True
    return False


def get_me_as_an_attendee(attendees, my_email_addresses):
    for attendee in attendees:
        if is_me(attendee, my_email_addresses):
            return attendee


def is_reply_necessary(calendar, my_email_addresses):
    method = calendar['METHOD'].upper()

    if  method != 'REQUEST':
        logging.error(f"The method in the calendar file is {method} and not REQUEST")
        return False

    event = get_event(calendar)
    me_as_an_attendee = get_me_as_an_attendee(get_attendees(event), my_email_addresses)

    if me_as_an_attendee is None:
        logging.error("I'm not listed as an attendee of the event."\
                     +"A reply is not being demanded from me.")
        return False
    if str(me_as_an_attendee.params.get('RSVP')).upper() == 'FALSE':
        logging.info("I'm listed as an attendee, but not asked to reply (no RSVP)")
        return False
    if str(me_as_an_attendee.params.get('PARTSTAT')).upper() != 'NEEDS-ACTION':
        logging.warning("'PARTSTAT' is not set to 'NEEDS-ACTION'...  Have I already accepted?")
        return False

    logging.info("I'm listed as an attendee and I am asked to reply (RSVP)")
    return True

def add_reply_to_calendar(calendar, my_email_addresses, action):

    calendar['METHOD'] = 'REPLY'
    calendar['PRODID'] = 'j95.io'  # Replacing this to make sure recipient (e.g. google/microsoft) doesn't try (and fail) to handle RSVP internally
    event = get_event(calendar)
    me_as_an_attendee = get_me_as_an_attendee(get_attendees(event), my_email_addresses)
    # Make the reply have *only my own* updated attendee information
    event['ATTENDEE'] = edit_attendee_status(me_as_an_attendee, action)

    ts = datetime.datetime.utcnow().replace(microsecond=0).isoformat()\
         .replace(':','').replace('-','') + 'Z'  # e.g. 20221122T000840Z
    event['LAST-MODIFIED'] = ts
    event['DTSTAMP'] = ts

    return calendar


if __name__ == '__main__':

    args = parser.parse_args()

    log_level = logging.INFO if args.verbose else logging.WARNING
    log_format = '%(levelname)s: %(message)s' if args.verbose else '%(message)s'
    logging.basicConfig(format=log_format, level=log_level)

    my_email_addresses = [e for e in args.my_email_addresses.split(',') if e]
    action = args.action.upper()

    # Open the file
    with open(args.invitation_filename, 'rb') as f:
        calendar = icalendar.Calendar.from_ical(f.read())

    if not is_reply_necessary(calendar, my_email_addresses):
        sys.exit(1)
    elif action == 'QUERY':
        sys.exit(0)

    calendar = add_reply_to_calendar(calendar, my_email_addresses, action)
    sys.stdout.write(str(calendar.to_ical().decode('utf-8')))
