import unittest

import runtime


class TestRuntime(unittest.TestCase):

    def setUp(self):
        self._json_expression_builder = JsonExpressionBuilder()
        self._term_builder = runtime.lambda_terms.LambdaTermBuilder()

    def test_readme_example(self):
        lam = self._term_builder.lambda_function
        var = self._term_builder.variable
        app = self._term_builder.application

        def apply_n_times(function, argument, *, n):
            for i in range(n):
                argument = app(function, argument)
            return argument

        f = var('f')
        x = var('x')
        three_term = lam('f', lam('x', apply_n_times(f, x, n=3)))

        num = var('num')
        square_term = lam('num', lam('f', apply_n_times(num, f, n=2)))

        main_term = app(square_term, three_term)
        main_term.normalize()

        expected_result = lam('f', lam('x', apply_n_times(f, x, n=9)))

        self._assert_terms_equal(main_term, expected_result)

    def _assert_terms_equal(self, term_a, term_b):
        expr_a = term_a.as_abstract_expression(self._json_expression_builder)
        expr_b = term_b.as_abstract_expression(self._json_expression_builder)
        self.assertEqual(expr_a, expr_b)


class JsonExpressionBuilder:

    def lambda_function(self, argument_name, body):
        return {
            'type': 'function',
            'argument_name': argument_name,
            'body': body,
        }

    def variable(self, name):
        return {
            'type': 'variable',
            'name': name,
        }

    def application(self, applied, argument):
        return {
            'type': 'application',
            'applied': applied,
            'argument': argument,
        }


if __name__ == '__main__':
    unittest.main()
