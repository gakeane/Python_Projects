
"""
Module which implements a NX-OS API session with a cisco switch
module assumes that the Cisco switch as the NX API feature enabled

We can create a CiscoNxApiSession by creating a CiscoNxApiSession object
And giving it the IP address of the switch as an argument
"""

import json
import logging
import requests
import urllib3

log = logging.getLogger(__name__)
urllib3.disable_warnings()

DEFAULT_USER = 'admin'
DEFAUL_PASSWORD = 'admin'

class CiscoNxApiSession(object):
    """
    Class for interacting with the Cisco NX-OS API
    """

    def __init__(self, switch_ip, user=DEFAULT_USER, password=DEFAUL_PASSWORD):
        """ Initiator

        switch_ip: (string) IP address of the switch to connect with
        """

        self.ip = switch_ip
        self._user = user
        self._password = password

        self.base_url = 'https://%s:443/' % switch_ip
        self.cookies = {}
        self.open_session()

    def set_user(self, user):
        """ Sets the value to be used as the switch username by the CisciNxApiSession instance """
        self._user = user

    def set_password(self, password):
        """ Sets the value to be used as the switch username by the CisciNxApiSession instance """
        self._password = password

    def open_session(self):
        """ Creates a session with the Cisco switch NX-OS API and saves a cookie for this session """

        node = "api/aaaLogin.json"
        payload = {"aaaUser": {"attributes": {"name": self.user,
                                              "pwd": self.password}}}

        try:
            log.info("Opening API session with switch [%s]", self.ip)
            response = self._post(node=node, payload=payload)
            auth_token = response['imdata'][0]['aaaLogin']['attributes']['token']
            self.cookies['APIC-Cookie'] = auth_token

        except Exception as err:
            log.error("Exception while opening session with Cisco switch [%s] [%s]", self.ip, err)
            raise

    def close_session(self):
        """ Closes a session with the Cisco switch NX-OS API """

        node = "api/aaaLogout.json"
        payload = {"aaaUser": {"attributes": {"name": self.user}}}

        try:
            self._post(node=node, payload=payload)

        except Exception as err:
            log.error("Exception while closing session with Cisco switch [%s] [%s]", self.ip, err)
            raise

    # FIXME: Change admin and Welcome1 to use get methods
    def _post(self, node, payload, timeout=60):
        """ Sends a HTTP POST request to the NX-OS API on the switch and returns the response

        node:    ()
        payload: (Dictionary) Contains the information to be sent in the post request
        """

        url = self.base_url + node
        headers = {'Content-Type': 'application/json'}
        auth = (self.user, self.password)

        try:
            # send the command to the switch API
            response = requests.post(url, headers=headers, auth=auth, data=json.dumps(payload),
                                     verify=False, cookies=self.cookies, timeout=timeout)

            # check if the switch API received the command
            if response.status_code != 200:
                raise CiscoApiException("Error code [%s] [%s]" %
                                        (response.status_code, response.content.decode("utf-8")))

            # check if the command was successful
            if "ins_api" in payload:

                sub_responses = response.json()['ins_api']['outputs']['output']
                if not isinstance(sub_responses, list):
                    sub_responses = [sub_responses]

                for result in sub_responses:
                    if result['code'] != "200":
                        raise CiscoApiException("CLI command failed with error [%s] [%s] (See Logs for details)" %
                                                (result['code'], result['msg']))

            # return the result of the command
            return json.loads(response.text)

        except Exception:
            log.error("POST Request to switch [%s] failed", self.ip)
            raise

    def run_show_command(self, cmd, timeout=60):
        """ Used to execute a show command on the NX-OX API """

        node = "ins"
        payload = {"ins_api": {"version": "1.0",
                               "type": "cli_show",
                               "chunk": "0",
                               "sid": "1",
                               "input": cmd,
                               "output_format": "json"}}

        try:
            return self._post(node, payload, timeout)
        except Exception:
            log.error("FAILED COMMAND [%s]", cmd)
            raise

    def run_config_commands(self, cmds, timeout=600):
        """ Used to execute a list of commands which will perform some sort of configuration on the switch

        cmds: (list) List of commands which will perform the configuration
        """

        node = "ins"
        cmd = " ; ".join(cmds)
        payload = {"ins_api": {"version": "1.0",
                               "type": "cli_conf",
                               "chunk": "0",
                               "sid": "1",
                               "input": cmd,
                               "output_format": "json"}}

        try:
            return self._post(node, payload, timeout)
        except Exception:
            log.error("FAILED COMMAND(S) %s", cmds)
            raise

    ##################
    # SHOW COMMANDS
    ##################

    def show_system_config(self):
        """ Returns a dictionary containing information about the systems configuration

        (cli cmd: show version)
        """
        result = self.run_show_command("show version")
        return result['ins_api']['outputs']['output']['body']

    def show_running_config(self):
        """ Returns a dictionary containing information about the current running configuration

        (cli cmd: show running-config)
        """
        result = self.run_show_command("show running-config")
        return result['ins_api']['outputs']['output']['body']['nf:filter']['m:configure']['m:terminal']

    def show_startup_config(self):
        """ Returns a dictionary containing information about the current startup configuration

        (cli cmd: show startup-config)
        """
        result = self.run_show_command("show startup-config")
        return result['ins_api']['outputs']['output']['body']['nf:filter']['m:configure']['m:terminal']

    def show_ip4_routing_info(self):
        """ Returns a dictionary containing information about IPv4 routing on the switch

        (cli cmd: show ip route)
        """
        result = self.run_show_command("show ip route")
        result = result['ins_api']['outputs']['output']['body']['TABLE_vrf']
        routes = result['ROW_vrf']['TABLE_addrf']['ROW_addrf']['TABLE_prefix']['ROW_prefix']
        return {route['ipprefix']: route for route in routes}

    def show_interface(self, interface):
        """ Returns a dictionary with detailed information about the specified interface

        (cli cmd: show interface)
        interface: (string) The name of the interface to query (i.e. Ethernet 1/4, Po111)
        """
        result = self.run_show_command("show interface %s" % interface)
        return result['ins_api']['outputs']['output']['body']['TABLE_interface']['ROW_interface']

    def show_all_interfaces(self):
        """ Returns a dictionary with information about all the interfaces on the switch

        (cli cmd: show interface brief)
        """
        result = self.run_show_command("show interface brief")
        interfaces = result['ins_api']['outputs']['output']['body']['TABLE_interface']['ROW_interface']
        return {interface['interface']: interface for interface in interfaces}

    def show_all_vlans(self):
        """ Returns a dictionary of all the VLANs on the switch and the interfaces on those VLANs

        (cli cmd: show vlan brief)
        """
        result = self.run_show_command("show vlan brief")
        vlans = result['ins_api']['outputs']['output']['body']['TABLE_vlanbriefxbrief']['ROW_vlanbriefxbrief']
        return {vlan['vlanshowbr-vlanid']: vlan for vlan in vlans}

    def show_all_vpcs(self):
        """ Returns a dictionary of all the VPCs configured on the switch

        (cli cmd: show vpc brief)
        """
        result = self.run_show_command("show vpc brief")
        vpcs = result['ins_api']['outputs']['output']['body']['TABLE_vpc']['ROW_vpc']
        return {vpc['vpc-ifindex']: vpc for vpc in vpcs}

    ##################
    # CONFIGURATION COMMANDS
    ##################

    def save_configuration(self):
        """ Runs a copy running-config startup-config command so that configuration changes persist """

        cmds = ["copy running-config startup-config"]
        self.run_config_commands(cmds)

    def set_interface_up(self, interface):
        """ Sets an interface up

        interface: (string) The name of the interface to query (i.e. Ethernet 1/4 or Ethernet 1/2-8 for a range)
        """
        cmds = ["interface %s" % interface, "no shutdown"]
        log.info("Setting up interface(s) [%s]", interface)
        self.run_config_commands(cmds)
        self.save_configuration()

    def set_interface_down(self, interface):
        """ Sets an interface down

        interface: (string) The name of the interface to query (i.e. Ethernet 1/4 or Ethernet 1/2-8 for a range)
        """
        cmds = ["interface %s" % interface, "shutdown"]
        log.info("Setting down interface(s) [%s]", interface)
        self.run_config_commands(cmds)
        self.save_configuration()


class CiscoApiException(Exception):
    """ Exception to represent a failed command on the Cisco API """
    pass
