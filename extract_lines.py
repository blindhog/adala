from ciscoconfparse import CiscoConfParse
import argparse
import adala


argparser = argparse.ArgumentParser()
argparser.add_argument('-f','--files',help='Configuration Filename or Regex of Files', nargs='*')
argparser.add_argument('-t', '--text', help='Regex Search Text', required=True)

args = argparser.parse_args()
if args.files:
    file_list = args.files
text=args.text

for file in file_list:
    confparse = CiscoConfParse(file)
    iosparse = adala.IOSParse()
    hostname = iosparse.get_hostname(file)
    iosparse.print_list(iosparse.generate_header_h2("{} configuration lines containing {}\n! {}".format(hostname,text,file)))
    iosparse.print_list(iosparse.get_lines(file,text))