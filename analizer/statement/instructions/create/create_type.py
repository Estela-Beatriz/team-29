
from analizer.abstract import instruction as inst
from analizer.typechecker.Metadata import Struct
from analizer.reports import Nodo
from storage.storageManager import jsonMode

class CreateType(inst.Instruction):
    def __init__(self, exists, name, values=[]):
        self.exists = exists
        self.name = name
        self.values = values

    def execute(self, environment):
        lista = []
        for value in self.values:
            lista.append(value.execute(environment).value)
        result = Struct.createType(self.exists, self.name, lista)
        if result == None:
            report = "Type creado"
        else:
            report = result
        return report

    def dot(self):
        new = Nodo.Nodo("CREATE_TYPE")
        if self.exists:
            exNode = Nodo.Nodo("IF_NOT_EXISTS")
            new.addNode(exNode)
        idNode = Nodo.Nodo(self.name)
        new.addNode(idNode)
        paramsNode = Nodo.Nodo("PARAMS")
        new.addNode(paramsNode)
        for v in self.values:
            paramsNode.addNode(v.dot())

        return new
