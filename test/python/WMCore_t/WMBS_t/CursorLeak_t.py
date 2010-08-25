#!/usr/bin/env python
"""
_File_t_

Unit tests for the WMBS File class.
"""

__revision__ = "$Id: CursorLeak_t.py,v 1.1 2009/03/24 22:10:17 sryu Exp $"
__version__ = "$Revision: 1.1 $"

import unittest
import logging
import os
import commands
import threading
import random
from sets import Set

from WMCore.Database.DBCore import DBInterface
from WMCore.Database.DBFactory import DBFactory
from WMCore.DAOFactory import DAOFactory
from WMCore.WMBS.File import File
from WMCore.WMFactory import WMFactory
from WMQuality.TestInit import TestInit
from WMCore.DataStructs.Run import Run
from WMCore.Services.UUID import makeUUID

class CursorLeakTest(unittest.TestCase):
    _setup = False
    _teardown = False

    def runTest(self):
        """
        _runTest_

        Run all the unit tests.
        """
        unittest.main()
    
    def setUp(self):
        """
        _setUp_

        Setup the database and logging connection.  Try to create all of the
        WMBS tables.  Also add some dummy locations.
        """
        if self._setup:
            return

        self.testInit = TestInit(__file__, os.getenv("DIALECT"))
        self.testInit.setLogging()
        self.testInit.setDatabaseConnection()
        self.testInit.setSchema(customModules = ["WMCore.WMBS"],
                                useDefault = False)

        myThread = threading.currentThread()
        daofactory = DAOFactory(package = "WMCore.WMBS",
                                logger = myThread.logger,
                                dbinterface = myThread.dbi)

        locationAction = daofactory(classname = "Locations.New")
        locationAction.execute(sename = "se1.cern.ch")
        locationAction.execute(sename = "se1.fnal.gov")        
        
        self._setup = True
        return
          
    def tearDown(self):        
        """
        _tearDown_
        
        Drop all the WMBS tables.
        """
        myThread = threading.currentThread()
        
        if self._teardown:
            return

        if myThread.transaction == None:
            myThread.transaction = Transaction(self.dbi)
        
        myThread.transaction.begin()

        factory = WMFactory("WMBS", "WMCore.WMBS")        
        destroy = factory.loadObject(myThread.dialect + ".Destroy")
        destroyworked = destroy.execute(conn = myThread.transaction.conn)

        if not destroyworked:
            raise Exception("Could not complete WMBS tear down.")
        
        myThread.transaction.commit()    
        self._teardown = True
            
    def testCursor(self):
        """
        _testCursor_
        
        test the cursor closing is really affected
        
        create 100 files with 5 parents and  loop 100 times.
        If the cursors are exhausted will crash.?
        
        TODO: improve for more effective testing. 

        """
        fileList = []
        parentFile = None
        for i in range(100):
            testFile = File(lfn = "/this/is/a/lfn%s" % i, size = 1024, events = 10, cksum=1111)            
            testFile.addRun(Run(1, *[i]))
            testFile.create()
            
            for j in range(5):
                parentFile = File(lfn = "/this/is/a/lfnP%s" % j, size = 1024, events = 10, cksum=1111)            
                parentFile.addRun(Run(1, *[j]))
                parentFile.create()
                testFile.addParent(parentFile['lfn'])
    
            fileList.append(testFile)
            
        for i in range(100):
            for file in fileList:
                file.loadData()
                file.getAncestors(level = 2)
                file.getAncestors(level = 2, type = "lfn")
        
        return
    
    def testLotsOfAncestors(self):
        """
        _testLotsOfAncestors_

        Create a file with 15 parents with each parent having 100 parents to
        verify that the query to return grandparents works correctly.
        """
        testFileA = File(lfn = "/this/is/a/lfnA", size = 1024, events = 10,
                        cksum = 1, locations = "se1.fnal.gov")
        testFileA.create()

        for i in xrange(15):
            testParent = File(lfn = makeUUID(), size = 1024, events = 10,
                              cksum = 1, locations = "se1.fnal.gov")
            testParent.create()
            testFileA.addParent(testParent["lfn"])

            for i in xrange(100):
                testGParent = File(lfn = makeUUID(), size = 1024, events = 10,
                                   cksum = 1, locations = "se1.fnal.gov")
                testGParent.create()
                testParent.addParent(testGParent["lfn"])                

        assert len(testFileA.getAncestors(level = 2, type = "lfn")) == 1500, \
               "ERROR: Incorrect grand parents returned"
        
        return
if __name__ == "__main__":
    unittest.main() 
