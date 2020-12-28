from analizer.abstract import expression as exp
from analizer.reports import Nodo
from analizer.expressions import primitive


class Arithmetic(exp.Expression):
    """
    Esta clase recibe un parametro de expresion
    para realizar operaciones unarias
    """

    def __init__(self, exp, operator, row, column):
        super().__init__(row, column)
        self.exp = exp
        self.operator = operator
        self.temp = str(operator) + exp.temp

    def execute(self, environment):
        exp = self.exp.execute(environment)
        operator = self.operator
        if exp.type != exp.TYPE.NUMBER:
            exp.list_errors.append(
                "Error: 42883: la operacion no existe entre: "
                + str(operator)
                + " "
                + str(exp.type)
                + "\n En la linea: "
                + str(self.row)
            )
            return ArithmeticError
        if operator == "+":
            value = exp.value
        elif operator == "-":
            value = exp.value * -1
        else:
            exp.list_errors.append(
                "Error: 42883: la operacion no existe entre: "
                + str(operator)
                + " "
                + str(exp.type)
                + "\n En la linea: "
                + str(self.row)
            )
            raise Exception
        return primitive.Primitive(
            exp.TYPE.NUMBER, value, self.temp, self.row, self.column
        )

    def dot(self):
        n1 = self.exp.dot()
        new = Nodo.Nodo(self.operator)
        new.addNode(n1)
        return new