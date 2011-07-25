#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Michael Davidsaver <mdavidsaver@gmail.com>
Copyright 2011
Licence: GPL 3+
"""

appname='kwlexport'

import codecs
import sys
from optparse import OptionParser
import dbus
import struct
from base64 import standard_b64encode

int32=struct.Struct('!I')

opts=OptionParser(usage='%prog [-o file|-] [-w walletname]',
                  description='Export KDE KWallet in XML form to stdout or file')
opts.add_option('-o', '--output', help='Write output to file (- for stdout)')
opts.add_option('-w', '--wallet', help='Wallet name (default is lexographic first)')

opts, args = opts.parse_args()

if opts.output or opts.output=='-':
    out=codecs.open(opts.output, mode='w', encoding='utf-8')
else:
    out=sys.stdout

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

print >>out,'''<?xml version="1.0" encoding="UTF-8"?>
<wallet name="%(name)s">'''%{'name':wname}

for f in folders:
    
    ents=kwallet.entryList(thewallet,f,appname)

    if len(ents)==0:
        print >>out,u'    <folder name="%(name)s"/>'%{'name':f}
        continue
    
    else:
        print >>out,u'    <folder name="%(name)s">'%{'name':f}

    for e in ents:
        etype=kwallet.entryType(thewallet,f,e,appname)
        
        if etype==1:
            p=kwallet.readPassword(thewallet,f,e,appname)
            print >>out,' '*8,u'<password name="%s">%s</password>'%(e,p)
            
        elif etype==2:
            p=kwallet.readEntry(thewallet,f,e,appname)
            # returns a list of bytes
            # convert to byte string
            p=map(str,p)
            if len(p)==0:
                p=u''
            else:
                p=reduce(str.__add__, p)
            p=standard_b64encode(p)

            print >>out,' '*8,u'<stream name="%s">%s</stream>'%(e,p)
            
        elif etype==3:
            p=kwallet.readMap(thewallet,f,e,appname)
            # returns a list of bytes
            # convert to byte string
            p=reduce(str.__add__, map(str,p))

            # first 4 bytes is the number of pairs
            count,=int32.unpack(p[:4])
            p=p[4:]

            if count==0:
                print >>out,' '*8,u'<map name="%s"/>'%e
                continue
            
            else:
                print >>out,' '*8,u'<map name="%s">'%e
                for n in range(count):

                    # length of payload in bytes
                    keylen,=int32.unpack(p[:4])
                    p=p[4:]
                    key=p[:keylen].decode('utf-16be') # payload
                    p=p[keylen:]

                    vallen,=int32.unpack(p[:4])
                    p=p[4:]
                    val=p[:vallen].decode('utf-16be')
                    p=p[vallen:]

                    print >>out,' '*12,u'<mapentry name="%s">%s</mapentry>'%(key,val)
                print >>out,' '*8,'</map>'

        else:
            print >>sys.stderr,'Ignoring unknown entry type',etype

    print >>out,'    </folder>'

print >>out,'</wallet>'

kwallet.close(thewallet,False,appname)

if out is not sys.stdout:
    out.close()
