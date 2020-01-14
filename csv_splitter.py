#!/usr/bin/env python3
#
# CSV Splitter
#
# CLT for splitting apart large csv files into smaller files
# saves new files to current directory
# saves incrementally (file_1, file_2, etc.)
#
# Version 0.1.0
# August 12th 2019
# Python 3.7.0
#


import csv
import argparse


def read_from_file(filename):
    """
    reads a csv file and returns a 2d list of the contents
    :param filename: name of csv file
    :return: 2d list[x][y] where x is a row and y is a column
    """

    csv_list = []
    try:
        csv_reader = csv.reader(filename, delimiter=',')
        for row in csv_reader:
            csv_list.append([col for col in row])
        return csv_list
    except IOError:
        print("Error: could not open {}".format(filename))


def write_csv(csv_list, filename):
    """
    writes a single csv file to the current directory
    :param csv_list: 2d list containing the csv contents
    :param filename: name of the newly created csv file
    :return: True if write successful, False if not
    """

    try:
        with open(filename, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in csv_list:
                csv_writer.writerow([col for col in row])
        return True
    except IOError:
        print("Error: could not create {}".format(filename))
        return False


def main(infile, outfile, file_length):
    """
    main method - splits csv files into smaller files and writes then to current directory
    :param infile: name of csv file that will be split apart
    :param outfile: name of partitioned csv file(s) that will be made
    :param file_length: length of each new smaller csv file (** NOT INCLUDING HEADER **)
    :return: True if write successful, False if not
    """

    csv_list = read_from_file(infile)
    header = csv_list[0]
    csv_list = csv_list[1:]
    num_files = (len(csv_list) // file_length) + 1

    for i in range(num_files):
        partial_list = csv_list[:file_length]
        partial_list.insert(0,header)
        csv_list = csv_list[file_length:]
        filename = "{}_{}.csv".format(outfile, i + 1)
        response = write_csv(partial_list, filename)
        if response:
            print('{} written successfully'.format(filename))
        else:
            print('unable to successfully write {}'.format(filename))


if __name__ == '__main__':
    # config argument parser
    parser = argparse.ArgumentParser(
        prog='CSV Splitter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
Split .csv files into multiple smaller length file(s)

usage:
  csv_splitter 'master.csv' 'new_file.csv' 50""")
    parser.add_argument('infile',
                        type=argparse.FileType('r'),
                        help='csv file that will be split apart')
    parser.add_argument('outfile',
                        help='name of partitioned csv file(s) that will be made')
    parser.add_argument('length',
                        default='master.csv',
                        type=int,
                        help='length of new csv files (including header)')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='%(prog)s 0.1.0')
    args = parser.parse_args()

    main(args.infile, args.outfile, args.length)