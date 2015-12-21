#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Michael Davidsaver <mdavidsaver@gmail.com>
Copyright 2015
Licence: GPL 3+
"""

appname='kwlimport'

import codecs
import sys
from base64 import standard_b64decode

from kwlhelper.service import KWallet, PASSWORD, STREAM, MAP

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

def main(args):
    from xml.etree.ElementTree import fromstring

    data=fromstring(args.input.read())

    if args.wallet:
        wname=args.wallet
    else:
        wname=data.attrib('name')

    KWL = KWallet(appname='kwlimport')
    
    with KWL.open(wname, create=True) as WALL:
        for f in data.findall('folder'):
            fn=f.attrib['name']
            FOLD = WALL.folder(fn, create=True)

            ents = dict(FOLD.iterentries())

            for e in f.findall('password'):
                en=e.attrib['name']
                val=e.text
    
                if en in ents and not args.overwrite:
                    print 'Skipping password:',en
                    continue
    
                FOLD.writePassword(en, val)
                print 'Set password',en #,'with',val

            for e in f.findall('map'):
                en=e.attrib['name']

                if en in ents and not args.overwrite:
                    print 'Skipping map:',en
                    continue

                elist = []
                for me in e.findall('mapentry'):
                    elist.append((me.attrib['name'], me.text))

                FOLD.writeMap(en, elist)
                print 'Set map',en #,'with',repr(bytestr)

            for e in f.findall('stream'):
                en=e.attrib['name']
    
                if en in ents and not args.overwrite:
                    print 'Skipping binary:',en
                    continue

                val=standard_b64decode(e.text or '')

                FOLD.writeStream(en, val)
                print 'Set binary',en #,'with',val

if __name__=='__main__':
    args = getargs()
    try:
        main(args)
    finally:
        args.input.close()
