from analizer.abstract import expression as exp
from analizer.reports import Nodo


class TableAll(exp.Expression):
    """
    Esta clase representa una tabla.*
    """

    def __init__(self, table, row, column):
        super().__init__(row, column)
        self.table = table

    def execute(self, environment):
        env = environment
        lst = []
        while env != None:
            if self.table in env.variables:
                table = env.variables[self.table].value
                for p in env.dataFrame:
                    temp = p.split(".")
                    if temp[0] == table:
                        identifier = exp.Identifiers(
                            self.table, temp[1], self.row, self.column
                        )
                        lst.append(identifier)
                break
            env = env.previous
        return lst

    def dot(self):
        new = Nodo.Nodo(str(self.table))
        punto = Nodo.Nodo(".*")
        new.addNode(punto)
        return new