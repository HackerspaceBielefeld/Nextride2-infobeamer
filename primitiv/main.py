"""
Module for the main functionality.
"""

import argparse

from infobeamer_helper import fetch_schedule, get_local_schedule_content
from infobeamer import infobeamer_main



def main(destination: str, seconds: int, content_uri: str, schedule_uri: str):
    """
    Main function to send content to infobeamer screens.

    Args:
        destination (str): The destination IP address.
        seconds (int): The time in seconds the content should be displayed.
        content_uri (str): The URI of the content to be displayed.
        schedule_uri (str): The URI of the schedule.
    """

    print(f"Destination IP: {destination}")
    print(f"seconds: {seconds}")
    print(f"uri: {content_uri}")
    print(f"schedule: {schedule_uri}")

    # Check if schedule_uri is provided and fetch the schedule accordingly
    if schedule_uri:
        if schedule_uri.startswith("http"):
            schedule = fetch_schedule(schedule_uri)
        else:
            schedule = get_local_schedule_content(schedule_uri)
    else:
        schedule = ""

    infobeamer_main(destination, seconds, content_uri, schedule)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sent images or gifs to the nextride screens')
    parser.add_argument('-d', '--dest', default='255.255.255.255', help='Destination IP address')
    parser.add_argument('-s', '--seconds', required=True, type=int, help='Seconds')
    parser.add_argument('-u', '--uri',
        default='https://hackerspace-bielefeld.de/wp-content/uploads/2024/03/flyer-325x325.png',
        help='URI')
    parser.add_argument('-f', '--schedule', help='Specify the schedule URL in XML frab format')

    args = parser.parse_args()

    main(args.dest, args.seconds, args.uri, args.schedule)