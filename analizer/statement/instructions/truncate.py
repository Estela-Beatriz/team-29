from analizer.abstract import instruction as inst
from analizer.typechecker.Metadata import Struct
from analizer.reports import Nodo
from storage.storageManager import jsonMode



class Truncate(inst.Instruction):
    def __init__(self, name):
        self.name = name

    def execute(self, environment):
        try:
            valor = jsonMode.truncate(inst.dbtemp, self.name)
            if valor == 2:
                inst.semanticErrors.append(
                    ["La base de datos " + str(inst.dbtemp) + " no existe ", self.row]
                )
                inst.syntaxPostgreSQL.append(
                    "Error: 42000: La base de datos  " + str(inst.dbtemp) + " no existe"
                )
                return "La base de datos no existe"
            if valor == 3:
                inst.semanticErrors.append(
                    ["La tabla " + str(self.name) + " no existe ", self.row]
                )
                inst.syntaxPostgreSQL.append(
                    "Error: 42P01: La tabla " + str(self.name) + " no existe"
                )
                return "El nombre de la tabla no existe"
            if valor == 1:
                inst.syntaxPostgreSQL.append("Error: XX000: Error interno")
                return "Hubo un problema en la ejecucion de la sentencia"
            if valor == 0:
                return "Truncate de la tabla: " + self.name
        except:
            inst.syntaxPostgreSQL.append("Error: P0001: Error en la instruccion TRUNCATE")

    def dot(self):
        new = Nodo.Nodo("TRUNCATE")
        n = Nodo.Nodo(self.name)
        new.addNode(n)
        return new
