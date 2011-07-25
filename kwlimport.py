#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Michael Davidsaver <mdavidsaver@gmail.com>
Copyright 2011
Licence: GPL 3+
"""

appname='kwlimport'

import codecs
import sys
from optparse import OptionParser
import dbus
import struct
from base64 import standard_b64decode

from xml.etree.ElementTree import fromstring

int32=struct.Struct('!I')

opts=OptionParser(usage='%prog [-i file|-] [-w walletname] [-O]',
                  description='Import KDE KWallet in XML form from stdin or file')
opts.add_option('-i', '--input', help='Read output to file (- for stdout)')
opts.add_option('-w', '--wallet', help='Wallet name (default is lexographic first)')
opts.add_option('-O', '--overwrite', help='Overwrite existing entries', action='store_true',
                default=False)

opts, args = opts.parse_args()

if opts.input or opts.input=='-':
    inp=codecs.open(opts.input, mode='r', encoding='utf-8')
else:
    inp=sys.stdin
    
data=fromstring(inp.read())

sbus=dbus.SessionBus()
proxy=sbus.get_object('org.kde.kwalletd', '/modules/kwalletd')
kwallet=dbus.Interface(proxy, 'org.kde.KWallet')

if opts.wallet:
    wname=opts.wallet
else:
    x=kwallet.wallets()
    if len(x)==0:
        raise RuntimeError('No wallets found')
    wname=str(x[0])

thewallet=kwallet.open(wname, 0, appname)
if thewallet<0:
    raise RuntimeError('Failed to open wallet: '+wname)

folders=kwallet.folderList(thewallet, appname)

for f in data.findall('folder'):
    fn=f.attrib['name']
    if fn not in folders:
        print 'create folder',fn
        kwallet.createFolder(thewallet, fn, appname)

    ents=kwallet.entryList(thewallet,fn,appname)
    
    for e in f.findall('password'):
        en=e.attrib['name']
        val=e.text
        
        if en in ents and not opts.overwrite:
            print 'Skipping password:',en
            continue

        kwallet.writePassword(thewallet,fn,en,val,appname)
        print 'Set password',en #,'with',val

    for e in f.findall('map'):
        en=e.attrib['name']
        
        bytestr=''
        count=0

        if en in ents and not opts.overwrite:
            print 'Skipping map:',en
            continue

        for me in e.findall('mapentry'):
            keystr=me.attrib['name'].encode('utf-16be')
            valstr=me.text.encode('utf-16be')

            bytestr+='%s%s%s%s'%(int32.pack(len(keystr)),
                                 keystr,
                                 int32.pack(len(valstr)),
                                 valstr)
                                 
            count+=1

        bytestr=int32.pack(count)+bytestr

        kwallet.writeMap(thewallet,fn,en,bytestr,appname)
        print 'Set map',en #,'with',repr(bytestr)


    for e in f.findall('stream'):
        en=e.attrib['name']

        val=standard_b64decode(e.text)

        if en in ents and not opts.overwrite:
            print 'Skipping binary:',en
            continue

        kwallet.writeEntry(thewallet,fn,en,val,appname)
        print 'Set binary',en #,'with',val


kwallet.close(thewallet,False,appname)
