from ciscoconfparse import CiscoConfParse
import argparse
import re
import adala

argparser = argparse.ArgumentParser()
argparser.add_argument('-f', '--files', help='Configuration Filename or Regex of Files', required=True, nargs='*')
argparser.add_argument('-t', '--text', help='Regex Search Text', required=True)

args = argparser.parse_args()

file_list = args.files
text = args.text


for filename in file_list:
    confparse = CiscoConfParse(filename)
    iosparse = adala.IOSParse()
    hostname = iosparse.get_hostname(filename)
    iosparse.print_list(iosparse.generate_header_h2('{} configuration blocks containing {}\n! {}'.format(hostname,text,filename)))
    for line in confparse.find_blocks(text):
        if re.match("^[0-9a-zA-Z]",line):
            print("\n")
        print(line)




