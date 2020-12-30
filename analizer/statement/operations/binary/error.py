from analizer.abstract import expression as exp

class ErrorBinaryOperation(exp.Expression):
    """
    Reporta error de una expresion
    """

    def __init__(self, exp1, exp2, row, column):
        exp.Expression.__init__(self, row, column)
        self.exp1 = exp1
        self.exp2 = exp2
        self.value = "error"
        self.error = (
            "No se pudo concretar la operacion entre " + str(exp1) + " : " + str(exp2)
        )
        self.type = exp.ERROR.TYPEERROR

    def execute(self, environment):
        print(self.error)
