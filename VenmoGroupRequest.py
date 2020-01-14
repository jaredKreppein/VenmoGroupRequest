# !/anaconda3/condabin/conda
#
# Venmo Group Request Command Line Tool
#
# Version 1.0.0
# August 31st, 2019
# Python 3.7.0
#


import argparse
import datetime
import logging
import venmo
import csv
import sys
from colored import fg, attr


class LogTracker:
    """
    captures the output of the Venmo API logger and saves error logs
    to a list to track unsuccessful requests
    """

    def __init__(self, method):
        self.method = method
        self.names_list = []

    def __call__(self, *args, **kwargs):
        # strips rests of log and saves username without the '@' char
        user = str(*args)[21:]
        self.names_list.append(user)
        return self.method(*args, **kwargs)


class User:
    """ represents a single user: first name, last name, username """

    def __init__(self, first, last, username):
        self.first = first
        self.last = last
        self.username = username


def read_from_file(filename):
    """
    reads a .csv file and returns a list of Users

    :param filename: name of csv file
    :return: list of Users (see class 'User' for more info)
    """

    users_list = []
    try:
        next(filename)  # ignore headers row
        csv_reader = csv.reader(filename)
        for row in csv_reader:
            users_list.append(User(row[0], row[1], row[2]))
        return users_list
    except IOError:
        print("Error: could not open {}".format(filename))


def send_all_requests(users_list, amount, message):
    """
    sends Venmo requests to all users in users_list

    Venmo has a request limit of 50 requests per 24 hours. If users_list reaches this limit,
    save the remaining users into [remaining]

    :param users_list: list of Venmo users
    :param amount: $ amount requested, rounded to 2 decimal points
    :param message: request message, maximum 2000 characters (cannot be empty)
    :return: tuple containing 4 lists ([successful], [failed], [no-account], [remaining])
    """

    success_list = []
    failure_list = []
    no_account_list = []
    remaining_list = []

    limit_count = 0
    for user in users_list:
        # request limit is reached
        if limit_count >= 50:
            remaining_list.append(user)
        else:
            # no account
            if user.username == "no-account":
                no_account_list.append(user)
                print("Skipping {} {}...".format(user.first, user.last))
            else:
                venmo.payment.charge('@' + user.username, amount, message)
                # failed request
                if user.username in logging.error.names_list:
                    failure_list.append(user)
                    # venmo.payment prints an error message if request fails
                else:
                    # successful request
                    success_list.append(user)
                    limit_count += 1
                    # venmo.payment prints a success message if request succeeds
    return success_list, failure_list, no_account_list, remaining_list


def write_to_file(remaining):
    """
    writes remaining users to new csv file in case request limit is reached

    :param remaining: list of users that were not sent requests
    :return: NONE, but writes a new csv file to the current directory
    """

    filename = "{}-remainders.csv".format(datetime.datetime.now())
    with open(filename, 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['FIRST_NAME', 'LAST_NAME', 'VENMO'])
        for user in remaining:
            csv_writer.writerow([user.first, user.last, user.username])


def main(amount, message, filename, write_to):
    """
    main method - sends Venmo requests to all users in the csv file
    logs successful/unsuccessful request attempts

    :param amount: $ amount requested, rounded to 2 decimal points
    :param message: request message, maximum 2000 characters (cannot be empty)
    :param filename: .csv file of people's names and usernames
    :param write_to: if True will write remainders to a new file
    :return: NONE
    """

    # checks if access token is valid, if not, prompt for credentials
    venmo.auth.ensure_access_token()

    if len(message) > 2000:
        raise ValueError("message must be less than 2000 chars (Venmo max limit)")
    if message is '' or message.isspace():
        raise ValueError("message cannot be empty")
    amount = round(amount, 2)

    response = input("""
        you have entered the following:
        amount:    ${}
        message:   {}
        file:      {}
        write_to:  {}

        Is this correct? (y or n) """.format(amount, message, filename.name, write_to))
    if response.lower() == 'y':
        print("\n---------------------")
        print(" STARTING REQUESTS...")
        print("---------------------\n")
        users_list = read_from_file(filename)
        results = send_all_requests(users_list, amount, message)

        print("\n---------------------  ")
        print("       RESULTS:         ")
        print("---------------------\n")
        print("%sSuccessful Requests: %d%s" % (fg(2), len(results[0]), attr(0)))
        if len(results[0]) > 0:
            for user in results[0]:
                print("%s %s" % (user.first, user.last))
        print("%s\nFailed Requests: %d%s" % (fg(1), len(results[1]), attr(0)))
        if len(results[1]) > 0:
            for user in results[1]:
                print("%s %s" % (user.first, user.last))
        print("\n%sUsers without an account: %d%s" % (fg(3), len(results[2]), attr(0)))
        if len(results[2]) > 0:
            for user in results[2]:
                print("%s %s" % (user.first, user.last))
        print("\n%sRemaining Users: %d%s" % (fg(4), len(results[3]), attr(0)))
        if len(results[3]) > 0:
            for user in results[3]:
                print("%s %s" % (user.first, user.last))
        if write_to:
            if len(results[3]) > 0:
                write_to_file(results[3])
                print("\ncsv file created successfully")
            else:
                print("no file created")
        print()
    else:
        sys.exit()


# ----------- MAIN ------------
if __name__ == '__main__':
    # config argument parser
    parser = argparse.ArgumentParser(
        prog='VenmoGroupRequest',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
    Send Venmo requests to users from a csv file

    usage:
      VenmoGroupRequest 5 'party pitch'
      VenmoGroupRequest 7 't-shirts for event' -file 'smallGroup.csv'
      VenmoGroupRequest 5 'party' -write""")
    parser.add_argument('amount',
                        type=float,
                        help='$ amount requesting')
    parser.add_argument('message',
                        help='request message')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='%(prog)s 0.2.0')
    parser.add_argument('-file',
                        default='csv/master.csv',
                        type=argparse.FileType('r'),
                        help='.csv file of usernames (default is master.csv)')
    parser.add_argument('-write',
                        action='store_true',
                        help='create a csv file of remaining users')
    args = parser.parse_args()

    # config log parser for venmo.payment
    logging = logging.getLogger("venmo.payment")
    logging.error = LogTracker(logging.error)

    main(args.amount, args.message, args.file, args.write)
