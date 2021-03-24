from ciscoconfparse import CiscoConfParse
import argparse
import adala


argparser = argparse.ArgumentParser()
argparser.add_argument('-f','--files',help='Configuration Filename or Regex of Files', nargs='*')

args = argparser.parse_args()
if args.files:
    file_list = args.files

for file in file_list:
    confparse = CiscoConfParse(file)
    iosparse = adala.IOSParse()
    hostname = iosparse.get_hostname(file)
    iosparse.print_list(iosparse.generate_header_h2("{} IP Interface Configurations".format(hostname)))
    iosparse.print_list(iosparse.get_ip_interface_configs(file))
    