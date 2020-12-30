
from analizer.abstract import expression as exp
from analizer.reports import Nodo
from datetime import datetime
from analizer.expressions import primitive

list_errors = list()

class Current(exp.Expression):
    def __init__(self, val, optStr, row, column) -> None:
        super().__init__(row, column)
        self.val = val
        self.optStr = optStr
        self.temp = val
        if optStr != None:
            self.temp += " " + optStr

    def execute(self, environment):

        try:
            if self.val == "CURRENT_DATE":
                value = datetime.now().strftime("%Y/%m/%d")
            elif self.val == "CURRENT_TIME":
                value = datetime.now().strftime("%H:%M:%S")
            elif self.val == "TIMESTAMP":
                if self.optStr == "now":
                    value = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                else:
                    value = self.optStr
            else:
                # ERROR
                list_errors.append(
                    "Error: 22007: Formato de fecha invalido " + str(self.str)
                )
                value = self.val
            return primitive.Primitive(exp.TYPE.STRING, value, self.temp, self.row, self.column)
        except:
            list_errors.append("Error: P0001: Error en expresiones de fechas")
            pass

    def dot(self):
        new = Nodo.Nodo(self.val)
        return new

