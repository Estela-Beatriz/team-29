from analizer.abstract import expression as exp

class ErrorTernaryOperation(exp.Expression):
    """
    Reporta error de una expresion
    """

    def __init__(self, exp1, exp2, exp3, row, column):
        exp.Expression.__init__(self, row, column)
        self.exp1 = exp1
        self.exp2 = exp2
        self.exp3 = exp3
        self.error = (
            "No se pudo concretar la operacion entre "
            + str(exp1)
            + " : "
            + str(exp2)
            + " : "
            + str(exp3)
        )
        self.type = exp.ERROR.TYPEERROR

    def execute(self, environment):
        print(self.error)
