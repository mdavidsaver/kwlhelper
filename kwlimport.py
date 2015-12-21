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

def resolve_ignore(folder, key, curtype, cur, newtype, new):
    print 'Resolve',folder,key,'keep existing'
    return curtype, cur

def resolve_replace(folder, key, curtype, cur, newtype, new):
    print 'Resolve',folder,key,'replace with new'
    return newtype, new

def getargs():
    from argparse import ArgumentParser
    P = ArgumentParser(usage='%(prog)s [-i file|-] [-w walletname] [-O]',
                  description='Import KDE KWallet in XML form from stdin or file')
    P.add_argument('-i', '--input', help='Read output to file (- for stdout)')
    P.add_argument('-w', '--wallet', help='Wallet name (override name in file)')
    P.add_argument('-C', '--conflict', default='ignore', metavar='METHOD',
                   help='Conflict resolution: ignore, replace, merge')
    A = P.parse_args()

    if A.input:
        A.input = codecs.open(A.input, mode='r', encoding='utf-8')
    else:
        A.input = sys.stdin

    if A.conflict=='ignore':
        A.conflict = resolve_ignore
    elif A.conflict=='replace':
        A.conflict = resolve_replace
    else:
        P.error("Unknown conflict resolution method '%s'"%A.conflict)

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

            newents = []

            for e in f.findall('password'):
                en=e.attrib['name']
                etype = PASSWORD
                val=e.text
                newents.append((en, etype, val))

            for e in f.findall('map'):
                en=e.attrib['name']
                etype = MAP

                val = []
                for me in e.findall('mapentry'):
                    val.append((me.attrib['name'], me.text))

                newents.append((en, etype, val))

            for e in f.findall('stream'):
                en=e.attrib['name']
                etype = STREAM
    
                val=standard_b64decode(e.text or '')

                newents.append((en, etype, val))

            for en, etype, val in newents:
                if en in ents:
                    etype, val = args.conflict(FOLD.name, en,
                                               ents[en],
                                               FOLD.readEntry(en, ents[en]),
                                               etype, val)
    
                FOLD.writeEntry(etype, en, val)
                ents[en] = etype
                print 'Store',etype,en #,'with',val

if __name__=='__main__':
    args = getargs()
    try:
        main(args)
    finally:
        args.input.close()
