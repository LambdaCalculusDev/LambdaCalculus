import expression as _expression
import runtime as _runtime
import syntax as _syntax


__all__ = ('LambdaLanguage',)


class LambdaLanguage:

    def __init__(self, *, expr_builder=None, code_reader=None, term_builder=None, expr_representer=None):
        if expr_builder is None:
            expr_builder = self._get_default_expr_builder()
        self._expr_builder = expr_builder

        if code_reader is None:
            code_reader = self._get_default_code_reader()
        self._code_reader = code_reader

        if term_builder is None:
            term_builder = self._get_default_term_builder()
        self._term_builder = term_builder

        if expr_representer is None:
            expr_representer = self._get_default_expr_representer()
        self._expr_representer = expr_representer

    def term_from_code(self, lambda_code):
        main_expression = self._code_reader(lambda_code)
        return main_expression.reinterpret_using(self._term_builder)

    def represent_term(self, term):
        expression = term.as_abstract_expression(expr_builder=self._expr_builder)
        return self._expr_representer(expression)

    def _get_default_expr_builder(self):
        return _expression.basic.LambdaExpressionBuilder()

    def _get_default_code_reader(self):
        expr_tactics = _syntax.classic_expression.LambdaExpressionTactics(self._expr_builder)

        definitions_translator = _expression.definitions.DefinitionsExpressionTranslator(self._expr_builder)

        program_tactics = _syntax.classic_program.LambdaProgramTactics(
            expr_tactics,
            apply_definitions=definitions_translator.apply_definitions
        )

        return lambda code: _syntax.tactics_core.apply_tactic(program_tactics.program, code)

    def _get_default_term_builder(self):
        return _runtime.lambda_terms.LambdaTermBuilder()

    def _get_default_expr_representer(self):
        return _syntax.classic_expression.represent_lambda_expression
