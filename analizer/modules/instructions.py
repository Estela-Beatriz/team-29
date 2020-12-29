from analizer.instructions import delete
from analizer.instructions import insert
from analizer.instructions import update
from analizer.instructions import drop 
from analizer.instructions import truncate
from analizer.instructions.create import create_data_base
from analizer.instructions.create import create_table


def Delete (fromcl, wherecl, row, column):
    return delete.Delete(fromcl, wherecl, row, column)

def InsertInto (tabla, columns, parametros):
    return insert.InsertInto(tabla, columns, parametros)

def Update (fromcl, values, wherecl, row, column):
    return update.Update(fromcl, values, wherecl, row, column)

def CreateDataBase(replace, exists, name, owner, mode):
    return create_data_base.CreateDatabase(replace, exists,name,owner,mode)

def CreateTable(exists, name, inherits, columns=[]):
    return create_table.CreateTable(exists,name,inherits,columns)

def Drop(structure, name, exists):
    return drop.Drop(structure, name, exists)
 
def Truncate(name):
    return truncate.Truncate(name)