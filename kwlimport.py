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
import dbus
import struct
from base64 import standard_b64decode

int32=struct.Struct('!I')

def getargs():
    from argparse import ArgumentParser
    P = ArgumentParser(usage='%(prog)s [-i file|-] [-w walletname] [-O]',
                  description='Import KDE KWallet in XML form from stdin or file')
    P.add_argument('-i', '--input', help='Read output to file (- for stdout)')
    P.add_argument('-w', '--wallet', help='Wallet name (override name in file)')
    P.add_argument('-O', '--overwrite', help='Overwrite existing entries',
                 action='store_true', default=False)
    A = P.parse_args()

    if A.input:
        A.input = codecs.open(A.input, mode='r', encoding='utf-8')
    else:
        A.input = sys.stdin
    return A

def dopen():
    sbus=dbus.SessionBus()
    proxy=sbus.get_object('org.kde.kwalletd', '/modules/kwalletd')
    return sbus, dbus.Interface(proxy, 'org.kde.KWallet')

def main(kwallet, args):
    from xml.etree.ElementTree import fromstring

    data=fromstring(args.input.read())

    if args.wallet:
        wname=args.wallet
    else:
        wname=data.attrib('name')

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

            if en in ents and not args.overwrite:
                print 'Skipping password:',en
                continue

            kwallet.writePassword(thewallet,fn,en,val,appname)
            print 'Set password',en #,'with',val

        for e in f.findall('map'):
            en=e.attrib['name']

            bytestr=''
            count=0

            if en in ents and not args.overwrite:
                print 'Skipping map:',en
                continue

            for me in e.findall('mapentry'):
                keystr=me.attrib['name'].encode('utf-16be')
                if me.text is None:
                    valstr = ''
                else:
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

            if en in ents and not args.overwrite:
                print 'Skipping binary:',en
                continue

            kwallet.writeEntry(thewallet,fn,en,val,appname)
            print 'Set binary',en #,'with',val


    kwallet.close(thewallet,False,appname)

if __name__=='__main__':
    session, kwallet = dopen()
    args = getargs()
    try:
        main(kwallet, args)
    finally:
        session.close()
        args.input.close()
