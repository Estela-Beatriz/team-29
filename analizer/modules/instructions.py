from analizer.instructions import delete
from analizer.instructions import insert
from analizer.instructions import update


def Delete (fromcl, wherecl, row, column):
    return delete.Delete(fromcl, wherecl, row, column)

def InsertInto (tabla, columns, parametros):
    return insert.InsertInto(tabla, columns, parametros)

def Update (fromcl, values, wherecl, row, column):
    return update.Update(fromcl, values, wherecl, row, column)