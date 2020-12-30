from analizer.abstract import instruction as inst
from analizer.typechecker.Metadata import Struct
from analizer.reports import Nodo
from storage.storageManager import jsonMode


# carga de datos
Struct.load()

# listas encargadas de almacenar los errores semanticos
syntaxPostgreSQL = list()
semanticErrors = list()

class AlterDataBase(inst.Instruction):
    def __init__(self, option, name, newname):
        self.option = option  # define si se renombra o se cambia de dueño
        self.name = name  # define el nombre nuevo de la base de datos o el nuevo dueño
        self.newname = newname

    def execute(self, environment):
        try:
            if self.option == "RENAME":
                valor = jsonMode.alterDatabase(self.name, self.newname)
                if valor == 2:
                    semanticErrors.append(
                        ["La base de datos " + str(self.name) + " no existe", self.row]
                    )
                    syntaxPostgreSQL.append(
                        "Error: 42000: La base de datos  "
                        + str(self.name)
                        + " no existe"
                    )
                    return "La base de datos no existe: '" + self.name + "'."
                if valor == 3:
                    semanticErrors.append(
                        [
                            "La base de datos " + str(self.newname) + " ya existe",
                            self.row,
                        ]
                    )
                    syntaxPostgreSQL.append(
                        "Error: 42P04: La base de datos  "
                        + str(self.newname)
                        + " ya existe"
                    )
                    return "El nuevo nombre para la base de datos existe"
                if valor == 1:
                    syntaxPostgreSQL.append("Error: XX000: Error interno")
                    return "Hubo un problema en la ejecucion de la sentencia"
                if valor == 0:
                    Struct.alterDatabaseRename(self.name, self.newname)
                    return (
                        "Base de datos renombrada: " + self.name + " - " + self.newname
                    )
                return "Error ALTER DATABASE RENAME: " + self.newname
            elif self.option == "OWNER":
                valor = Struct.alterDatabaseOwner(self.name, self.newname)
                if valor == 0:
                    return "Instruccion ejecutada con exito ALTER DATABASE OWNER"
                syntaxPostgreSQL.append("Error: XX000: Error interno")
                return "Error ALTER DATABASE OWNER"
            syntaxPostgreSQL.append("Error: XX000: Error interno")
            return "Fatal Error ALTER DATABASE: " + self.newname
        except:
            syntaxPostgreSQL.append(
                "Error: P0001: Error en la instruccion ALTER DATABASE"
            )

    def dot(self):
        new = Nodo.Nodo("ALTER_DATABASE")
        iddb = Nodo.Nodo(self.name)
        new.addNode(iddb)

        optionNode = Nodo.Nodo(self.option)
        new.addNode(optionNode)
        valOption = Nodo.Nodo(self.newname)
        optionNode.addNode(valOption)

        return new
