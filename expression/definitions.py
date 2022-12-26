class DefinitionsExpressionTranslator:

    def __init__(self, expr_builder):
        self._expr_builder = expr_builder
        self._lam = self._expr_builder.lambda_function
        self._var = self._expr_builder.variable
        self._app = self._expr_builder.application

    def apply_definitions(self, definitions, main_expression):
        if not definitions:
            return main_expression

        definitions_names = [name for name, expr in definitions]
        implementations = [expr for name, expr in definitions]

        objects_tuple = self._create_objects_tuple_by_definitions(definitions_names, implementations)

        main_expression = self._app(
            objects_tuple,
            self._abstract_by_names(main_expression, definitions_names)
        )

        return main_expression

    def _create_objects_tuple_by_definitions(self, definitions_names, implementations):
        lam, var, app = self._lam, self._var, self._app

        def abstract_by_definitions_names(expr):
            return self._abstract_by_names(expr, definitions_names)

        i = 0
        while f'x{i}' in definitions_names:
            i += 1
        objects_tuple_name = f'x{i}'
        i += 1
        while f'x{i}' in definitions_names:
            i += 1
        objects_tuple_callback_name = f'x{i}'

        # Because of possible variables names collision,
        # we cannot directly put any user-defined object inside of a lambda scope.
        # So instead we will create combinator that takes user-defined objects as arguments,
        # and then we will apply it to user-defined objects.
        # Therefore, no variable can be accidentally bound

        objects_tuple_elements = [app(var(objects_tuple_name), var(def_name)) for def_name in definitions_names]
        objects_tuple_by_itself = lam(
            objects_tuple_name,
            self._create_tuple(
                objects_tuple_callback_name,
                objects_tuple_elements
            )
        )

        defined_objects_raw = [abstract_by_definitions_names(impl) for impl in implementations]
        objects_tuple_by_itself = self._pass_arguments(
            abstract_by_definitions_names(objects_tuple_by_itself),
            defined_objects_raw
        )

        objects_tuple = app(self._y_combinator, objects_tuple_by_itself)

        return objects_tuple

    def _pass_arguments(self, applied, arguments):
        result = applied
        for argument in arguments:
            result = self._app(result, argument)
        return result

    def _abstract_by_names(self, expr, names):
        for name in reversed(names):
            expr = self._lam(name, expr)
        return expr

    def _create_tuple(self, callback_name, tuple_values):
        tuple_body = self._pass_arguments(self._var(callback_name), tuple_values)
        return self._lam(callback_name, tuple_body)

    @property
    def _y_combinator(self):
        lam, var, app = self._lam, self._var, self._app
        f = var('f')
        x = var('x')
        y_combinator = lam('f', app(
            lam('x', app(x, x)),
            lam('x', app(f, app(x, x)))
        ))
        return y_combinator
