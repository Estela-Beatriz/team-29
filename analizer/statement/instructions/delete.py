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
class Delete(inst.Instruction):
    def __init__(self, fromcl, wherecl, row, column):
        inst.Instruction.__init__(self, row, column)
        self.wherecl = wherecl
        self.fromcl = fromcl

    def execute(self, environment):
        try:
            # Verificamos que no pueden venir mas de 1 tabla en el clausula FROM
            if len(self.fromcl.tables) > 1:
                syntaxErrors.append(["Error sintactico cerca de ,", self.row])
                syntaxPostgreSQL.append(
                    "Error: 42601: Error sintactico cerca de , en la linea "
                    + str(self.row)
                )
                return "Error: syntax error at or near ','"
            newEnv = Environment(environment, dbtemp)
            global envVariables
            envVariables.append(newEnv)
            self.fromcl.execute(newEnv)
            value = [newEnv.dataFrame[p] for p in newEnv.dataFrame]
            labels = [p for p in newEnv.dataFrame]
            for i in range(len(labels)):
                newEnv.dataFrame[labels[i]] = value[i]
            if self.wherecl == None:
                return newEnv.dataFrame.filter(labels)
            wh = self.wherecl.execute(newEnv)
            w2 = wh.filter(labels)
            # Si la clausula WHERE devuelve un dataframe vacio
            if w2.empty:
                return "Operacion DELETE completada"
            # Logica para eliminar
            table = self.fromcl.tables[0].name
            pk = Struct.extractPKIndexColumns(dbtemp, table)
            # Se obtienen las parametros de las llaves primarias para proceder a eliminar
            rows = []
            if pk:
                for row in w2.values:
                    rows.append([row[p] for p in pk])
            else:
                rows.append([i for i in w2.index])
            print(rows)
            # TODO: La funcion del STORAGE esta bugueada
            bug = False
            for row in rows:
                result = jsonMode.delete(dbtemp, table, row)
                if result != 0:
                    bug = True
                    break
            if bug:
                return ["Error: Funcion DELETE del Storage", rows]
            return "Operacion DELETE completada"
        except:
            syntaxPostgreSQL.append("Error: P0001: Error en la instruccion DELETE")

    def dot(self):
        new = Nodo.Nodo("DELETE")
        new.addNode(self.fromcl.dot())
        new.addNode(self.wherecl.dot())
        return new