#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xml.etree.ElementTree import ElementTree, Element, SubElement, tostring
import sys

from PyQt4 import QtGui
from kwlmerge.mergemain import mergeMain

from collections import defaultdict

import logging
log = logging.getLogger('kwlmerge')

class AbortMerge(Exception):
    pass

def parseFiles():

    data=defaultdict(list)

    for f in sys.argv[1:]:
        tree=ElementTree()
        tree.parse(f)
        log.info('Read %s',f)

        H=tree.getroot()

        for d in H.findall('folder'):
            dn=d.attrib['name']
            log.debug('Visit %s',dn)

            for p in d.findall('password'):
                pn=p.attrib['name']
                log.debug('Visit %s/%s',dn,pn)

                data[(dn,pn)].append((f,p.text))

    return data

def merge(data):

    base=Element('wallet')

    for (dn,pn),v in data.iteritems():
        d=base.find(dn)
        if d is None:
            d=SubElement(base, 'folder', name=dn)

        unique=[]

        for other in v:
            if not any(map(lambda x: other[1]==x[1] ,unique)):
                unique.append(other)

        if len(unique)>1:
            m=mergeMain(None, unique, title='%s/%s'%(dn,pn))
            if not m.exec_():
                raise AbortMerge('Operation aborted')
            unique=m.merged
        else:
            unique=unique[0][1]

        SubElement(d, pn, name=pn).text=unique

    return base

if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG,
        format='%(message)s', stream=sys.stderr)

    from sys import exit, argv
    app = QtGui.QApplication(argv)

    data=parseFiles()
    try:
        base=merge(data)
    except AbortMerge:
        print >>sys.stderr,'Aborted by user'
        exit(1)

    print tostring(base)
