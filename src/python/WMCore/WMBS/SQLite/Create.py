"""
_Create_

Implementation of Create for SQLite.

Inherit from CreateWMBSBase, and add SQLite specific creates to the dictionary 
at some high value.
"""

__revision__ = "$Id: Create.py,v 1.5 2009/10/05 18:08:03 sfoulkes Exp $"
__version__ = "$Revision: 1.5 $"

from WMCore.WMBS.CreateWMBSBase import CreateWMBSBase

class Create(CreateWMBSBase):
    def __init__(self, logger = None, dbi = None, params = None):
        """
        _init_

        Call the base class's constructor and create all necessary tables,
        constraints and inserts.
        """
        CreateWMBSBase.__init__(self, logger, dbi, params)
        self.requiredTables.append('30wmbs_subs_type')
        
        self.create["30wmbs_subs_type"] = \
          """CREATE TABLE wmbs_subs_type (
             id   INTEGER      PRIMARY KEY AUTOINCREMENT,
             name VARCHAR(255) NOT NULL)"""

        for subType in ("Processing", "Merge", "Harvesting"):
            subTypeQuery = "INSERT INTO wmbs_subs_type (name) values ('%s')" % \
                           subType
            self.inserts["wmbs_subs_type_%s" % subType] = subTypeQuery
            
    def execute(self, conn = None, transaction = None):
        for i in self.create.keys():
            self.create[i] = self.create[i].replace('AUTO_INCREMENT', 'AUTOINCREMENT')
            
        return CreateWMBSBase.execute(self, conn, transaction)
