# -*- coding: utf-8 -*-
"""
Author: Michael Davidsaver <mdavidsaver@gmail.com>
Copyright 2015
Licence: GPL 3+
"""

import struct

import dbus

__all__ = [
    'KWallet',
    'PASSWORD',
    'STREAM',
    'MAP',
]

PASSWORD = 1
STREAM = 2
MAP = 3

_int32=struct.Struct('!I')

class KWallet(object):
    '''Thin wrapper around DBus service with proper conversion
    to/from python types
    '''

    def __init__(self, appname, session=None):
        self.appname = appname
        self._session = session or dbus.SessionBus()
        
        self._proxy=self._session.get_object('org.kde.kwalletd', '/modules/kwalletd')
        self._I = dbus.Interface(self._proxy, 'org.kde.KWallet')

    def wallets(self, session=None):
        '@returns a list of strings'
        return [str(W) for W in self._I.wallets()]

    def open(self, name, create=False):
        '''Open, and optionally create, a wallet
        @returns a WalletProxy
        '''
        if not create and name not in self.wallets():
            raise ValueError("Wallet '%s' does not exist"%name)

        W = self._I.open(name, 0, self.appname)
        return WalletProxy(self, W, name)

    def delete(self, name):
        """Permenently delete a wallet (use with care)
        """
        self._I.deleteWallet(name)

    def close(self, name, force=False):
        self._I.close(name, force)

    def __repr__(self):
        return "KWallet(appname='%s')"%self.appname

class WalletProxy(object):
    def __init__(self, KW, W, name):
        self._KW, self._W, self.name = KW, W, name

    def __enter__(self):
        return self
    def __exit__(self,A,B,C):
        self.close()

    def close(self, force=False):
        self._KW._I.close(self._W, force, self._KW.appname)

    def folders(self):
        'Return a list of folder names'
        return [str(F) for F in self._KW._I.folderList(self._W, self._KW.appname)]

    def iterfolders(self):
        'Returns an iterator yielding FolderProxy'
        for F in self._KW._I.folderList(self._W, self._KW.appname):
            yield FolderProxy(self._KW, self._W, F)

    __iter__ = iterfolders

    def folder(self,name,create=False):
        if name not in self.folders():
            if not create:
                raise ValueError('Folder does not exist')
            self._KW._I.createFolder(self._W, name, self._KW.appname)
        return FolderProxy(self._KW, self._W, name)

    def __repr__(self):
        return "WalletProxy(name='%s')"%self.name

class FolderProxy(object):
    def __init__(self, KW, W, F):
        self._KW, self._W, self.name = KW, W, F

    def iterentries(self):
        '''Returns an iterator yielding a tuple of entry name and type.
        Type is one of PASSWORD, STREAM, or MAP
        '''
        for E in self._KW._I.entryList(self._W, self.name, self._KW.appname):
            T = self._KW._I.entryType(self._W, self.name, E, self._KW.appname)
            yield (E, T)

    __iter__ = iterentries

    def readPassword(self, key):
        'Returns a string'
        return str(self._KW._I.readPassword(self._W, self.name, key, self._KW.appname))

    def writePassword(self, key, value):
        self._KW._I.writePassword(self._W, self.name, key, value, self._KW.appname)

    def readStream(self, key):
        'Returns a string'
        bytes = self._KW._I.readEntry(self._W, self.name, key, self._KW.appname)
        return ''.join(map(chr, bytes))

    def writeStream(self, key, value):
        self._KW._I.writeEntry(self._W, self.name, key, value, self._KW.appname)

    def readMapList(self, key):
        'Returns a list of tuples (str, str|None)'
        bytes = self._KW._I.readMap(self._W, self.name, key, self._KW.appname)
        raw = ''.join(map(chr, bytes))

        # map is encoded as a 32-bit count followed by a number of variable
        # length entities, each with it's own count

        count, = _int32.unpack(raw[:4])
        raw = raw[4:]
        ret = [None]*count
        for i in range(count):
            NL, = _int32.unpack(raw[:4])
            raw = raw[4:]
            name = raw[:NL].decode('utf-16be')
            raw = raw[NL:]

            VL, = _int32.unpack(raw[:4])
            raw = raw[4:]
            if VL==0xffffffff:
                ret[i] = (name, None)
            else:
                ret[i] = (name,raw[:VL].decode('utf-16be'))
                raw = raw[VL:]

        return ret

    def readMap(self, key):
        'Returns a dictionary {str:str|None}'
        return dict(self.readMapList(key))

    def writeMap(self, key, value):
        'Write a dict or list of tuples'
        if hasattr(value, 'values'):
            value = value.items()

        out = []
        for K, val in value:
            K = K.encode('utf-16be')
            out.append(_int32.pack(len(K)) + K)
            if val is None:
                out.append(_int32.pack(0xffffffff))
            else:
                val = val.encode('utf-16be')
                out.append(_int32.pack(len(val)) + val)

        raw = _int32.pack(len(out)/2) + ''.join(out)
        self._KW._I.writeMap(self._W, self.name, key, raw, self._KW.appname)

    def __repr__(self):
        return "FolderProxy(name='%s')"%self.name
