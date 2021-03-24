from ciscoconfparse import CiscoConfParse
import argparse
import adala


argparser = argparse.ArgumentParser()
argparser.add_argument('-f','--files',help='Configuration Filename or Regex of Files', nargs='*')

args = argparser.parse_args()
if args.files:
    file_list = args.files

for filename in file_list:
    confparse = CiscoConfParse(filename)
    iosparse = adala.IOSParse()
    hostname = iosparse.get_hostname(filename)
    iosparse.print_list(iosparse.generate_header_h2('{} MLS QOS Configurations\n! {}'.format(hostname,filename)))
    iosparse.print_list(iosparse.get_mls_qos_configs(filename))
    