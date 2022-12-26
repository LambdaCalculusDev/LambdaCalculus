import string

import syntax.tactics_core as tc


__all__ = ('LambdaExpressionTactics',)


class LambdaExpressionTactics:

    def __init__(self, expr_builder):
        self._expr_builder = expr_builder

    _gap_char = tc.either(*string.whitespace)
    maybe_gap = tc.maybe_some(_gap_char)

    _name_char = tc.either(*string.ascii_letters, *string.digits, '_')

    @property
    @tc.tactic
    def name(self):
        chars_sequence = yield tc.some(self._name_char)
        return ''.join(chars_sequence)

    @property
    @tc.tactic
    def _variable(self):
        return self._expr_builder.variable((yield self.name))

    @property
    @tc.tactic
    def _lambda_function(self):
        argument_name, body = yield tc.chain(
            '\\', tc.pick(self.name), '.', self.maybe_gap, tc.pick(self.expression)
        )
        return self._expr_builder.lambda_function(argument_name, body)

    @property
    @tc.tactic
    def _brackets(self):
        content, = yield tc.chain('(', tc.pick(self.expression), ')')
        return content

    @property
    def _application_chain_element(self):
        return tc.either(self._variable, self._lambda_function, self._brackets)

    @property
    @tc.tactic
    def _application_chain(self):
        applied, *arguments = yield tc.some(self._application_chain_element, sep=self.maybe_gap)
        for argument in arguments:
            applied = self._expr_builder.application(applied, argument)
        return applied

    @property
    @tc.tactic
    def expression(self):
        yield self.maybe_gap
        result = yield self._application_chain
        yield self.maybe_gap
        return result


def represent_lambda_expression(expression, *, is_argument=False, is_chain_end=True):
    expr = expression
    repr_expr = represent_lambda_expression

    if expr.is_application():
        applied_repr = repr_expr(expr.applied, is_argument=False, is_chain_end=False)
        argument_repr = repr_expr(expr.argument, is_argument=True, is_chain_end=is_chain_end)
        result = f'{applied_repr} {argument_repr}'
        if is_argument:
            result = f'({result})'

    elif expr.is_lambda_function():
        body_repr = repr_expr(expr.body)
        result = f'\\{expr.argument_name}. {body_repr}'
        if not is_chain_end:
            result = f'({result})'

    elif expr.is_variable():
        result = f'{expr.name}'

    else:
        raise TypeError('unknown lambda expression type')

    return result
