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
    iosparse.print_list(iosparse.generate_header_h2("{} Routing Configurations".format(hostname)))
    iosparse.print_list(iosparse.get_general_routing_configs(file))
    iosparse.print_list(iosparse.get_dynamic_routing_configs(file))
    # iosparse.print_list(iosparse.generate_header_h2("{} Static Routing Configurations".format(hostname)))
    iosparse.print_list(iosparse.get_static_routing_configs(file))
    