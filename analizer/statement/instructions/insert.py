import sys
sys.path.append("../../..")
from storage.storageManager import jsonMode
from analizer.typechecker.Metadata import Struct
from analizer.symbol.environment import Environment
from analizer.reports import Nodo
from analizer.abstract import instruction as inst

envVariables = []


# carga de datos
Struct.load()

# variable encargada de almacenar la base de datos a utilizar
dbtemp = ""
# listas encargadas de almacenar los errores semanticos
syntaxPostgreSQL = list()
semanticErrors = list()
syntaxErrors = list()
class InsertInto(inst.Instruction):
    def __init__(self, tabla, columns, parametros):
        self.tabla = tabla
        self.parametros = parametros
        self.columns = columns

    def execute(self, environment):
        try:
            lista = []
            params = []
            tab = self.tabla

            for p in self.parametros:
                params.append(p.execute(environment))

            result = Checker.checkInsert(dbtemp, self.tabla, self.columns, params)
            if result[0] == None:
                for p in result[1]:
                    if p == None:
                        lista.append(p)
                    else:
                        lista.append(p.value)
                res = jsonMode.insert(dbtemp, tab, lista)
                if res == 2:
                    semanticErrors.append(
                        ["La base de datos " + dbtemp + " no existe", self.row]
                    )
                    syntaxPostgreSQL.append(
                        "Error: 42000: La base de datos  " + str(dbtemp) + " no existe"
                    )
                    return "La base de datos no existe"
                elif res == 3:
                    semanticErrors.append(
                        ["La tabla " + str(tab) + " no existe", self.row]
                    )
                    syntaxPostgreSQL.append(
                        "Error: 42P01: La tabla " + str(tab) + " no existe"
                    )
                    return "No existe la tabla"
                elif res == 5:
                    semanticErrors.append(
                        [
                            "La instruccion INSERT tiene mas o menos registros que columnas",
                            self.row,
                        ]
                    )
                    syntaxPostgreSQL.append(
                        "Error: 42611: INSERT tiene mas o menos registros que columnas "
                    )
                    return "Columnas fuera de los limites"
                elif res == 4:
                    semanticErrors.append(
                        [
                            "El valor de la clave esta duplicada, viola la restriccion unica",
                            self.row,
                        ]
                    )
                    syntaxPostgreSQL.append(
                        "Error: 23505: el valor de clave esta duplicada, viola la restricción única "
                    )
                    return "Llaves primarias duplicadas"
                elif res == 1:
                    syntaxPostgreSQL.append("Error: XX000: Error interno")
                    return "Error en la operacion"
                elif res == 0:
                    return "Fila Insertada correctamente"
            else:
                return result[0]
        except:
            syntaxPostgreSQL.append("Error: P0001: Error en la instruccion INSERT")
            pass

    def dot(self):
        new = Nodo.Nodo("INSERT_INTO")
        t = Nodo.Nodo(self.tabla)
        par = Nodo.Nodo("PARAMS")
        new.addNode(t)
        for p in self.parametros:
            par.addNode(p.dot())

        if self.columns != None:
            colNode = Nodo.Nodo("COLUMNS")
            for c in self.columns:
                colNode.addNode(Nodo.Nodo(str(c)))
            new.addNode(colNode)

        new.addNode(par)
        # ast.makeAst(root)
        return new
