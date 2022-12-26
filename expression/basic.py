import expression.interface as _interface


__all__ = ['LambdaExpressionBuilder']


class LambdaExpressionBuilder(_interface.ILambdaExpressionBuilder):

    def lambda_function(self, argument_name, body):
        return _LambdaExpression(
            type=_LambdaExpression.ExprTypes.LAMBDA_FUNCTION,
            argument_name=argument_name,
            body=body
        )

    def variable(self, name):
        return _LambdaExpression(
            type=_LambdaExpression.ExprTypes.VARIABLE,
            name=name
        )

    def application(self, applied, argument):
        return _LambdaExpression(
            type=_LambdaExpression.ExprTypes.APPLICATION,
            applied=applied,
            argument=argument
        )


class _LambdaExpression(_interface.ILambdaExpression):

    def __init__(self, type, **kwargs):
        expr_type = type
        del type

        if expr_type is self.ExprTypes.LAMBDA_FUNCTION:
            self._argument_name = kwargs.pop('argument_name')
            self._body = kwargs.pop('body')

        elif expr_type is self.ExprTypes.VARIABLE:
            self._name = kwargs.pop('name')

        elif expr_type is self.ExprTypes.APPLICATION:
            self._applied = kwargs.pop('applied')
            self._argument = kwargs.pop('argument')

        else:
            raise TypeError(f'invalid expression type: {expr_type}')

        self._expr_type = expr_type

        if kwargs:
            raise TypeError(f'unexpected arguments: {kwargs}')

    @property
    def expr_type(self):
        return self._expr_type

    @property
    def argument_name(self):
        return self._argument_name

    @property
    def body(self):
        return self._body

    @property
    def name(self):
        return self._name

    @property
    def applied(self):
        return self._applied

    @property
    def argument(self):
        return self._argument

    def reinterpret_using(self, instructions):
        if self.is_lambda_function():
            argument_name = self.argument_name
            body = self.body.reinterpret_using(instructions)
            result = instructions.lambda_function(argument_name, body)

        elif self.is_variable():
            result = instructions.variable(self.name)

        elif self.is_application():
            applied = self.applied.reinterpret_using(instructions)
            argument = self.argument.reinterpret_using(instructions)
            result = instructions.application(applied, argument)

        else:
            raise TypeError

        return result
