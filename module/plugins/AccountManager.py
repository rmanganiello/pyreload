#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License,
    or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <http://www.gnu.org/licenses/>.

    @author: RaNaN
"""

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from os.path import exists
from shutil import copy
from threading import Lock

import six

from module.PullEvents import AccountUpdateEvent
from module.singletons import (
    get_account_manager,
    get_plugin_manager,
    get_pull_manager,
)
from module.util.encoding import smart_bytes
from module.utils import (
    chmod,
    lock,
)

ACC_VERSION = 1


class AccountManager():
    """manages all accounts"""

    def __init__(self, core):
        """Constructor"""

        self.core = core
        self.lock = Lock()

        self.initPlugins()
        self.saveAccounts() # save to add categories to conf

    def initPlugins(self):
        self.accounts = {} # key = ( plugin )
        self.plugins = {}

        self.initAccountPlugins()
        self.loadAccounts()


    def getAccountPlugin(self, plugin):
        """get account instance for plugin or None if anonymous"""
        if plugin in self.accounts:
            if plugin not in self.plugins:
                self.plugins[plugin] = get_plugin_manager().loadClass("accounts", plugin)(self, self.accounts[plugin])

            return self.plugins[plugin]
        else:
            return None

    def getAccountPlugins(self):
        """ get all account instances"""

        plugins = []
        for plugin in self.accounts.keys():
            plugins.append(self.getAccountPlugin(plugin))

        return plugins
    #----------------------------------------------------------------------
    def loadAccounts(self):
        """loads all accounts available"""

        if not exists("accounts.conf"):
            with open("accounts.conf", "wb") as f:
                f.write(smart_bytes('version: {0}'.format(ACC_VERSION)))

        with open("accounts.conf", "rb") as f:
            content = f.readlines()
            version = content[0].split(b":")[1].strip() if content else ""

        if not version or int(version) < ACC_VERSION:
            copy("accounts.conf", "accounts.backup")
            with open("accounts.conf", "wb") as f:
                f.write(smart_bytes('version: {0}'.format(ACC_VERSION)))
            self.core.log.warning(_("Account settings deleted, due to new config format."))
            return

        plugin = ""
        name = ""

        for line in content[1:]:
            line = line.strip()

            if (
                not line or
                line.startswith(b"#") or
                line.startswith(b"version")
            ):
                continue

            if line.endswith(b":") and line.count(b":") == 1:
                plugin = line[:-1]
                self.accounts[plugin] = {}

            elif line.startswith(b"@"):
                try:
                    option = line[1:].split()
                    self.accounts[plugin][name]["options"][option[0]] = [] if len(option) < 2 else ([option[1]] if len(option) < 3 else option[1:])
                except:
                    pass

            elif b":" in line:
                name, sep, pw = line.partition(b":")
                self.accounts[plugin][name] = {"password": pw, "options": {}, "valid": True}

    def saveAccounts(self):
        """save all account information"""

        with open("accounts.conf", "wb") as f:
            f.write(smart_bytes('version: {0}\n'.format(ACC_VERSION)))

            for plugin, accounts in six.iteritems(self.accounts):
                f.write(smart_bytes('\n{0}:\n'.format(plugin)))

                for name, data in six.iteritems(accounts):
                    f.write(smart_bytes('\n\t{0}:{1}\n'.format(name, data['password'])))
                    if data['options']:
                        for option, values in six.iteritems(data['options']):
                            f.write(smart_bytes('\t@{0} {1}\n'.format(option, b' '.join(values))))

            chmod(f.name, 0o600)

    def initAccountPlugins(self):
        """init names"""
        for name in get_plugin_manager().getAccountPlugins():
            self.accounts[name] = {}

    @lock
    def updateAccount(self, plugin , user, password=None, options={}):
        """add or update account"""
        if plugin in self.accounts:
            p = self.getAccountPlugin(plugin)
            updated = p.updateAccounts(user, password, options)
            #since accounts is a ref in plugin self.accounts doesnt need to be updated here

            self.saveAccounts()
            if updated: p.scheduleRefresh(user, force=False)

    @lock
    def removeAccount(self, plugin, user):
        """remove account"""

        if plugin in self.accounts:
            p = self.getAccountPlugin(plugin)
            p.removeAccount(user)

            self.saveAccounts()

    @lock
    def getAccountInfos(self, force=True, refresh=False):
        data = {}

        if refresh:
            self.core.scheduler.addJob(0, get_account_manager().getAccountInfos)
            force = False

        for p in self.accounts.keys():
            if self.accounts[p]:
                p = self.getAccountPlugin(p)
                data[p.__name__] = p.getAllAccounts(force)
            else:
                data[p] = []
        e = AccountUpdateEvent()
        get_pull_manager().addEvent(e)
        return data

    def sendChange(self):
        e = AccountUpdateEvent()
        get_pull_manager().addEvent(e)
