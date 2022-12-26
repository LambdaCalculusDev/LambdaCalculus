import abc as _abc
from abc import abstractmethod as _abstractmethod
import enum as _enum


__all__ = ['ILambdaExpression', 'ILambdaExpressionBuilder']


class ILambdaExpression(_abc.ABC):

    ExprTypes = _enum.Enum('ExprTypes', ['LAMBDA_FUNCTION', 'VARIABLE', 'APPLICATION'])

    @property
    @_abstractmethod
    def expr_type(self) -> ExprTypes:
        pass

    def is_lambda_function(self):
        return self.expr_type is self.ExprTypes.LAMBDA_FUNCTION

    def is_variable(self):
        return self.expr_type is self.ExprTypes.VARIABLE

    def is_application(self):
        return self.expr_type is self.ExprTypes.APPLICATION

    @property
    @_abstractmethod
    def argument_name(self):
        pass

    @property
    @_abstractmethod
    def body(self):
        pass

    @property
    @_abstractmethod
    def name(self):
        pass

    @property
    @_abstractmethod
    def applied(self):
        pass

    @property
    @_abstractmethod
    def argument(self):
        pass

    @_abstractmethod
    def reinterpret_using(self, instructions):
        pass


class ILambdaExpressionBuilder(_abc.ABC):

    @_abstractmethod
    def lambda_function(self, argument_name, body) -> ILambdaExpression:
        pass

    @_abstractmethod
    def variable(self, name) -> ILambdaExpression:
        pass

    @_abstractmethod
    def application(self, applied, argument) -> ILambdaExpression:
        pass
