# VenmoGroupRequest
Version 1.0.0
2019 Jared Kreppein

A small command line tool to send Venmo requests to a every user in a csv file.
Requires the Venmo module (https://pypi.org/project/venmo) - Zach Hsi 2017.

USAGE:
send requests from default csv file:
    $ VenmoGroupRequest 5 'party friday'

send requests using a different csv file:
    $ VenmoGroupRequest 25 't-shirts for event' -f otherfile.csv

send requests that will write a new csv if Venmo's request limit is reached
    $ VenmoGroupRequest 5 'party' -write
