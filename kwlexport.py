#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Export an entire kwallet in XML from file or stdout to facilitate backup
and synchronization.

Author: Michael Davidsaver <mdavidsaver@gmail.com>
Copyright 2015
Licence: GPL 3+
"""

appname='kwlexport'

import sys
from base64 import standard_b64encode

from kwlhelper.service import KWallet, PASSWORD, STREAM, MAP

def getargs():
    from argparse import ArgumentParser
    P = ArgumentParser(usage='%(prog)s [-o file|-] [-w walletname]',
                       description='Export KDE KWallet in XML form to stdout or file')
    P.add_argument('-o','--output', help='Write output to file (- for stdout)')
    P.add_argument('-w', '--wallet', help='Wallet name (default is lexographic first)')
    A = P.parse_args()

    if A.output:
        import codecs
        A.output = codecs.open(A.output, mode='w', encoding='utf-8')
    else:
        A.output = sys.stdout

    return A

def main(args):
    out = args.output

    KWL = KWallet(appname='kwlexport')

    if args.wallet:
        wname=args.wallet
    else:
        x=KWL.wallets()
        if len(x)==0:
            raise RuntimeError('No wallets found')
        wname=str(x[0])

    with KWL.open(wname, create=False) as WALL:
    
        out.write(u'''<?xml version="1.0" encoding="UTF-8"?>
<wallet name="%(name)s">
'''%{'name':WALL.name})

        for FOLD in WALL:
            out.write(u'    <folder name="%(name)s">\n'%{'name':FOLD.name})
            for e, etype in FOLD:
                out.write(u' '*8)
                if etype==PASSWORD:
                    p=FOLD.readPassword(e)
                    out.write(u'<password name="%s">%s</password>\n'%(e,p))

                elif etype==STREAM:
                    p=FOLD.readStream(e)
                    p=standard_b64encode(p)

                    out.write(u'<stream name="%s">%s</stream>\n'%(e,p))

                elif etype==MAP:
                    out.write(u'<map name="%s">\n'%e)
                    for key, val in FOLD.readMapList(e):
                        out.write(u' '*12)
                        out.write(u'<mapentry name="%s">%s</mapentry>\n'%(key,val))
                    out.write(u' '*8)
                    out.write(u'</map>\n')
                        
                else:
                    print >>sys.stderr,'Ignoring unknown entry type',etype

            out.write(u'    </folder>\n')

        out.write(u'</wallet>\n')

if __name__=='__main__':
    args = getargs()
    try:
        main(args)
    finally:
        args.output.close()
