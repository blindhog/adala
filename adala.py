from ciscoconfparse import CiscoConfParse
import re

class IOSParse:
    def generate_header_h1(self,text):
        header_list = []
        header_list.append('\n\n')
        header_list.append('############################################################')
        header_list.append('# {}'.format(text))
        header_list.append('############################################################')
        return header_list
    
    def generate_header_h2(self,text):
        header_list = []
        header_list.append('\n\n')
        header_list.append('!------------------------------------------------------------!')
        header_list.append('! {}'.format(text))
        header_list.append('!------------------------------------------------------------!')
        return header_list
    
    def print_list (self,input_list):
        for line in input_list:
            print(line)
        return
    
    def build_show_cmds_dict(self,config):
        show_cmds_dict = {}
        show_cmd = None
        confparse = CiscoConfParse(config)
        for line in confparse.find_lines('.'):
          if re.search(r'#\s+show|#\s+more',line):
            show_cmd = line.split("#")[1]
            show_cmd = show_cmd.strip()
            show_cmds_dict[show_cmd] = []
          if show_cmd is not None:
            show_cmds_dict[show_cmd].append(line)
        return show_cmds_dict
    
    
    def get_output(self, cmd_regex,show_cmds_dict):
        cmd_output = None
        for show_cmd in show_cmds_dict.keys():
            if re.search(cmd_regex,show_cmd):
               cmd_output = show_cmds_dict[show_cmd]
               print(show_cmd)
        if cmd_output is not None:
            return cmd_output
        else:
            return ['No output found for \"{}\" command'.format(re.sub('\
                ?','',cmd_regex))]

    # def get_show_version(self,config):
    #     cmd_regex = r'sho?w? vers?i?o?n?'
    #     show_cmds_dict = build_show_cmds_dict(config)
    #     return get_output(cmd_regex,show_cmds_dict)
    # 
    # def get_show_run(self,config):
    #     cmd_regex = r'sho?w? runn?i?n?g?-?c?o?n?f?i?g?|more system:running-config'
    #     show_cmds_dict = build_show_cmds_dict(config)
    #     return get_output(cmd_regex,show_cmds_dict)
    
    def get_hostname(self,config):
        confparse = CiscoConfParse(config)
        hostname_line = confparse.find_lines('^hostname')
        if len(hostname_line) > 0:
            hostname = hostname_line[0].split(' ')[-1]
        else:
            hostname = "{{ hostname }}"
        return hostname

    def get_snmp_configs(self,config):
        confparse = CiscoConfParse(config)
        configs = confparse.find_all_children('^!?snmp')
        return configs

    def get_acl_configs(self,config,acl_name=''):
        confparse = CiscoConfParse(config)
        configs = []
        if acl_name != '':
            configs = confparse.find_all_children('access-list.*{}'.format(acl_name))
        else:
            configs = confparse.find_all_children('^ip access-list')
            configs += confparse.find_all_children('^access-list')
        return configs

    def get_mqc_qos_configs(self,config,name=''):
        confparse = CiscoConfParse(config)
        configs = []
        if name != '':
            policy_maps = confparse.find_lines('^policy-map {}'.format(name))
        else:
            policy_maps = confparse.find_lines('^policy-map')
        for policy_map in policy_maps:
            if configs != []:
                configs.append('\n\n!---\n\n')
            policy_map_name = policy_map.split(' ')[-1]
            policy_map_config = confparse.find_all_children('^policy-map {}'.format(policy_map_name))
            for pm_line in policy_map_config:
                if re.search(' class ',pm_line):
                    class_map_config = []
                    acl_name = ''
                    class_map_name = pm_line.split(' ')[-1]
                    class_map_config = confparse.find_all_children('class-map.*{}'.format(class_map_name))
                    for cm_line in class_map_config:
                        if re.search('match access-group',cm_line):
                            configs.append('!')
                            acl_name = cm_line.split(' ')[-1]
                            configs += self.get_acl_configs(config,acl_name) 
                    configs.append('!')
                    configs += class_map_config
            configs += policy_map_config
        return configs

    def get_mls_qos_configs(self,config):
        confparse = CiscoConfParse(config)
        configs = []
        mls_qos_config = confparse.find_blocks('mls qos')
        for line in mls_qos_config:
            if re.search('^interface',line):
                configs.append('!')
            configs.append(line)
        return configs

    def get_auto_qos_configs(self,config,full=False):
        confparse = CiscoConfParse(config)
        configs = []
        interface_configs = []
        auto_qos_config = []
        auto_qos_mls_configs = []
        auto_qos_mqc_configs = []
        auto_qos_blocks = confparse.find_blocks('auto qos')
        if full == True:
            auto_qos_config = auto_qos_blocks
        else:
            for line in auto_qos_blocks:
                if re.search('^interface',line):
                    auto_qos_config.append(line)
                if re.search('srr-queue',line):
                    auto_qos_config.append(line)
                if re.search('priority-queue',line):
                    auto_qos_config.append(line)
                if re.search('mls qos',line):
                    auto_qos_config.append(line)
                if re.search('auto qos',line):
                    auto_qos_config.append(line)
                if re.search('service-policy',line):
                    auto_qos_config.append(line)
        for line in auto_qos_config:
            if re.search('^interface',line):
                interface_configs.append('!')
            if re.search('mls qos',line):
                auto_qos_mls_configs = confparse.find_lines('^mls qos')
            if re.search('service-policy',line):
                service_policy_name = line.split(' ')[-1]
                auto_qos_mqc_configs = self.get_mqc_qos_configs(config,service_policy_name)
            interface_configs.append(line)
        
        if auto_qos_mls_configs != []:
            configs += auto_qos_mls_configs
            configs.append('\n!---\n')

        if auto_qos_mqc_configs != []:
            configs += auto_qos_mqc_configs
            configs.append('\n!---\n')

        configs += interface_configs
        return configs

    def get_general_routing_configs(self,config,protocol=''):
        confparse = CiscoConfParse(config)
        configs = []
        configs = confparse.find_lines('^ip routing')
        return configs

    def get_static_routing_configs(self,config,protocol=''):
        confparse = CiscoConfParse(config)
        configs = []
        configs = confparse.find_lines('^ip route')
        configs += confparse.find_lines('^ip default-gateway')
        return configs

    def get_dynamic_routing_configs(self,config,protocol=''):
        confparse = CiscoConfParse(config)
        configs = []
        if protocol not in ['rip','eigrp','ospf','bgp','isis','']:
            print('Invalid Routing Protocol. Please choose rip, eigrp, ospf, bgp or isis.')
        dynamic_routing_configs = confparse.find_blocks('^router {}'.format(protocol))
        for line in dynamic_routing_configs:
            if re.search('^router',line) and configs != []:
                configs.append('\n\n!---\n\n')
            configs.append(line)
        return configs

    def get_spanning_tree_configs(self,config):
        confparse = CiscoConfParse(config)
        configs = []
        spanning_tree_configs = confparse.find_blocks('spanning-tree')
        for line in spanning_tree_configs:
            if re.search('^interface',line):
                configs.append('!')
                configs.append(line)
            if re.search('spanning-tree',line):
                configs.append(line)
        return configs
                
    def get_errdisable_configs(self,config):
        confparse = CiscoConfParse(config)
        configs = []
        configs = confparse.find_lines('errdisable')
        return configs
        
    def get_aaa_configs(self,config):
        confparse = CiscoConfParse(config)
        configs = []
        aaa_configs = []
        radius_server_configs = []
        aaa_configs = confparse.find_lines('aaa')
        for line in aaa_configs:
            if 'group' in line:
                for position, item in enumerate(line.split()):
                    if item == 'group':
                        group_position = position + 1
                        group_name = line.split()[group_position]
                        if group_name == 'radius':
                            radius_server_configs = confparse.find_all_children('radius.server')
                            radius_server_configs.append('!')
                            radius_server_configs += confparse.find_all_children('ip radius')
        configs += radius_server_configs
        configs.append('!')
        configs += aaa_configs                
        return configs

    def get_logging_configs(self,config):
        confparse = CiscoConfParse(config)
        configs = []
        configs = confparse.find_blocks('^logging')
        return configs

    def get_password7_configs(self,config):
        confparse = CiscoConfParse(config)
        configs = []
        configs = confparse.find_blocks('password 7')
        return configs

    def get_line_vty_configs(self,config):
        confparse = CiscoConfParse(config)
        configs = []
        configs = confparse.find_blocks('^line vty')
        return configs

    def get_ip_interface_configs(self,config):
        confparse = CiscoConfParse(config)
        configs = []
        ip_interfaces = confparse.find_parents_w_child('^interface','ip address')
        if ip_interfaces != []:
            for line in ip_interfaces:
                configs = confparse.find_all_children(line)
        return configs