#
# (c) 2017 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
# Contains CLIConf Plugin methods for ENOS Modules
# Lenovo Networking
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
import json

from itertools import chain

from ansible.module_utils._text import to_bytes, to_text
from ansible.module_utils.network.common.utils import to_list
from ansible.plugins.cliconf import CliconfBase, enable_mode


class Cliconf(CliconfBase):

    def get_device_info(self):
        device_info = {}

        device_info['network_os'] = 'enos'
        reply = self.get(b'show version')
        data = to_text(reply, errors='surrogate_or_strict').strip()

        match = re.search(r'^Software Version (.*?) ', data, re.M | re.I)
        if match:
            device_info['network_os_version'] = match.group(1)

        match = re.search(r'^Lenovo RackSwitch (\S+)', data, re.M | re.I)
        if match:
            device_info['network_os_model'] = match.group(1)

        match = re.search(r'^(.+) uptime', data, re.M)
        if match:
            device_info['network_os_hostname'] = match.group(1)
        else:
            device_info['network_os_hostname'] = "NA"

        return device_info

    @enable_mode
    def get_config(self, source='running'):
        if source not in ('running', 'startup'):
            msg = "fetching configuration from %s is not supported"
            return self.invalid_params(msg % source)
        if source == 'running':
            cmd = b'show running-config'
        else:
            cmd = b'show startup-config'
        return self.send_command(cmd)

    @enable_mode
    def edit_config(self, command):
        for cmd in chain([b'configure terminal'], to_list(command), [b'end']):
            self.send_command(cmd)

    def get(self, command, prompt=None, answer=None, sendonly=False):
        return self.send_command(command, prompt=prompt, answer=answer, sendonly=sendonly)

    def get_capabilities(self):
        result = {}
        result['rpc'] = self.get_base_rpc()
        result['network_api'] = 'cliconf'
        result['device_info'] = self.get_device_info()
        return json.dumps(result)
