# VenmoGroupRequest
Version 1.0.0
2019 Jared Kreppein


A small command line tool to send Venmo requests to a every user in a csv file.
Requires the [Venmo module](https://pypi.org/project/venmo) - [Zach Hsi 2017](https://github.com/zackhsi).


### USAGE:
send requests from default csv file:
    $ VenmoGroupRequest 5 'party friday'

send requests using a different csv file:
    $ VenmoGroupRequest 25 't-shirts for event' -f otherfile.csv

send requests that will write a new csv if Venmo's request limit is reached
    $ VenmoGroupRequest 5 'party' -write
    
    
#### example.csv:
a template for the csv file format. First column is first name, second column is last name, and third column is the venmo username (without the '@' symbol).


#### CSV_Splitter:
a small command line tool to split apart large csv files. Useful when csv files are larger than Venmo's 50 requests per day limit


#### spreadsheet_scripts.gs:
allows a google spreadsheet to parse a gmail account and update based on Venmo email notifications
