import syntax.tactics_core as tc


__all__ = ('LambdaProgramTactics',)


class LambdaProgramTactics:

    def __init__(self, expression_tactics, *, apply_definitions):
        self._expression = expression_tactics.expression
        self._name = expression_tactics.name
        self._maybe_gap = expression_tactics.maybe_gap
        self._apply_definitions = apply_definitions

    @property
    @tc.tactic
    def definition(self):
        maybe_gap = self._maybe_gap
        assignment_operator = tc.chain(maybe_gap, tc.maybe(':'), '=', maybe_gap)
        end_definition = tc.chain(maybe_gap, ';')

        variable_name, expression = yield tc.chain(
            tc.pick(self._name), assignment_operator, tc.pick(self._expression), end_definition
        )
        return (variable_name, expression)

    @property
    @tc.tactic
    def program(self):
        maybe_gap = self._maybe_gap
        maybe_some_definitions = tc.maybe_some(self.definition, sep=maybe_gap)

        definitions, main_expression = yield tc.chain(
            maybe_gap, tc.pick(maybe_some_definitions), maybe_gap,
            tc.pick(self._expression), maybe_gap
        )
        return self._apply_definitions(definitions, main_expression)
