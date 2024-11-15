import collections as _collections


class LambdaTermBuilder:

    def __init__(self, variable_names_manager=None):
        if variable_names_manager is None:
            variable_names_manager = _VariableNamesManager()
        self._variable_names_manager = variable_names_manager

    def _term_from_node(self, node):
        return _LambdaTerm(node, term_builder=self, variable_names_manager=self._variable_names_manager)

    def lambda_function(self, argument_name, lambda_body):
        argument_name = self._variable_names_manager.identifier_by_name(argument_name)
        return self._term_from_node(_LambdaFunctionNode(argument_name, lambda_body))

    def variable(self, name):
        name = self._variable_names_manager.identifier_by_name(name)
        return self._term_from_node(_VariableNode(name))

    def application(self, applied, argument):
        return self._term_from_node(_ApplicationNode(applied, argument))


class _VariableNamesManager:

    def __init__(self, varnames_pool=None, next_unused_id=None):
        if varnames_pool is None:
            varnames_pool = set()
        self._varnames_pool = varnames_pool

        if next_unused_id is None:
            next_unused_id = 0
        self._next_unused_id = next_unused_id

    def identifier_by_name(self, name):
        self._varnames_pool.add(name)
        return name

    def name_by_identifier(self, identifier):
        return identifier

    def create_new_identifier(self, *, old_identifier=None):
        while str(self._next_unused_id) in self._varnames_pool:
            self._next_unused_id += 1
        result = str(self._next_unused_id)
        self._varnames_pool.add(result)
        return result


_LambdaFunctionNode = _collections.namedtuple('LambdaFunctionNode', 'argument_name body')
_VariableNode = _collections.namedtuple('VariableNode', 'name')
_ApplicationNode = _collections.namedtuple('ApplicationNode', 'applied argument')

_RedirectNode = _collections.namedtuple('RedirectNode', 'target')

_TermNode = (_LambdaFunctionNode, _VariableNode, _ApplicationNode, _RedirectNode)


class _LambdaTerm:

    def __init__(self, node, *, term_builder, variable_names_manager):
        if not isinstance(node, _TermNode):
            raise TypeError('invalid node type', type(node))
        self._term_builder = term_builder
        self._variable_names_manager = variable_names_manager
        self._node = node
        self._is_semi_reduced = False
        self._names_depend_on = self._find_names_depend_on()

    def as_abstract_expression(self, expr_builder):
        repr_name = self._variable_names_manager.name_by_identifier

        if self._is_variable_now():
            result = expr_builder.variable(repr_name(self._name))

        elif self._is_lambda_function_now():
            result = expr_builder.lambda_function(
                repr_name(self._argument_name),
                self._body.as_abstract_expression(expr_builder)
            )

        elif self._is_application_now():
            result = expr_builder.application(
                self._applied.as_abstract_expression(expr_builder),
                self._argument.as_abstract_expression(expr_builder)
            )

        else:
            raise RuntimeError

        return result

    def normalize(self):
        terms_to_normalize = targets_stack = [self]
        while targets_stack:
            term = targets_stack.pop()
            term.semi_reduce()
            term, _ = term._drop_outer_lambdas()
            applied, arguments = term._drop_arguments()
            assert applied._is_variable_now()
            targets_stack.extend(arguments)

    def semi_reduce(self):
        terms_to_semi_reduce = targets_stack = [self]
        while targets_stack:
            term = targets_stack[-1]
            if term._is_redirection_now() and not term._without_redirects()._is_semi_reduced:
                targets_stack.append(term._without_redirects())
            elif term._is_lambda_function_now() and not term._body._is_semi_reduced:
                targets_stack.append(term._body)
            elif term._is_application_now() and not term._applied._is_semi_reduced:
                targets_stack.append(term._applied)
            elif term._can_do_outer_reduction():
                term._reduce_by_one_step()
            else:
                term._is_semi_reduced = True
                targets_stack.pop()

    def _collapse_redirects_chain(self):
        if not self._is_redirection_now():
            raise RuntimeError

        latest_redirect = self
        redirects_to_fix = []
        while latest_redirect._node.target._is_redirection_now():
            redirects_to_fix.append(latest_redirect)
            latest_redirect = latest_redirect._node.target

        target = latest_redirect._node.target
        for redirect in redirects_to_fix:
            redirect._node = _RedirectNode(target)

    def _without_redirects(self):
        if not self._is_redirection_now():
            return self
        self._collapse_redirects_chain()
        return self._node.target

    def _node_without_redirects(self):
        return self._without_redirects()._node

    def _is_lambda_function_now(self):
        return isinstance(self._node_without_redirects(), _LambdaFunctionNode)

    def _is_variable_now(self):
        return isinstance(self._node_without_redirects(), _VariableNode)

    def _is_application_now(self):
        return isinstance(self._node_without_redirects(), _ApplicationNode)

    def _is_redirection_now(self):
        return isinstance(self._node, _RedirectNode)

    @property
    def _argument_name(self):
        return self._node_without_redirects().argument_name

    @property
    def _body(self):
        return self._node_without_redirects().body._without_redirects()

    @property
    def _name(self):
        return self._node_without_redirects().name

    @property
    def _applied(self):
        return self._node_without_redirects().applied._without_redirects()

    @property
    def _argument(self):
        return self._node_without_redirects().argument._without_redirects()

    def _find_names_depend_on(self):
        if self._is_variable_now():
            names = frozenset({self._name})
        elif self._is_application_now():
            names = self._applied._names_depend_on | self._argument._names_depend_on
        elif self._is_lambda_function_now():
            names = self._body._names_depend_on
            names -= frozenset({self._argument_name})
        else:
            raise RuntimeError
        return names

    def _may_depend_on_name(self, variable_name):
        return variable_name in self._names_depend_on

    def _can_do_outer_reduction(self):
        return self._is_application_now() and self._applied._is_lambda_function_now()

    def _reduce_by_one_step(self):
        reduced_by_one_step = self._get_reduced_by_one_step()
        if reduced_by_one_step._is_application_now() and not reduced_by_one_step._is_redirection_now():
            self._node = _RedirectNode(reduced_by_one_step)
        else:
            self._node = reduced_by_one_step._node

    def _get_reduced_by_one_step(self):
        assert self._can_do_outer_reduction()

        applied_lambda = self._applied
        target_name = applied_lambda._argument_name
        applied_lambda_body = applied_lambda._body

        if not applied_lambda_body._may_depend_on_name(target_name):
            return applied_lambda_body

        inner_term, bypassed_lambdas_names = applied_lambda_body._drop_outer_lambdas()

        target_name_unused = (
            target_name in bypassed_lambdas_names
            or (inner_term._is_variable_now() and inner_term._name != target_name)
            or not inner_term._may_depend_on_name(target_name)
        )

        if target_name_unused:
            return applied_lambda_body

        target_substitution = self._argument

        new_lambdas_names, lambdas_renamings = self._rename_bypassed_lambdas(
            bypassed_lambdas_names, target_substitution
        )

        inner_term = self._compose_new_inner_term(
            inner_term, target_name, target_substitution, lambdas_renamings
        )

        return inner_term._wrap_in_lambdas(new_lambdas_names)

    def _rename_bypassed_lambdas(self, bypassed_lambdas_names, new_term_inside):
        new_lambdas_names = list(bypassed_lambdas_names)
        lambdas_renamings = []
        for i, lambda_name in enumerate(bypassed_lambdas_names):
            if new_term_inside._may_depend_on_name(lambda_name):
                new_lambda_name = self._variable_names_manager.create_new_identifier(lambda_name)
                lambdas_renamings.append((lambda_name, new_lambda_name))
                new_lambdas_names[i] = new_lambda_name
        return new_lambdas_names, lambdas_renamings

    def _compose_new_inner_term(self, inner_term, target_name, target_substitution, lambdas_renamings):
        if inner_term._is_application_now():
            applied = inner_term._applied
            argument = inner_term._argument
            for old_name, new_name in lambdas_renamings:
                if applied._may_depend_on_name(old_name):
                    applied = applied._rename_free_variable(old_name, new_name)
                if argument._may_depend_on_name(old_name):
                    argument = argument._rename_free_variable(old_name, new_name)
            # Checking applied and argument for _may_depend_on_name(target_name)
            # looks reasonable here, but for unknown reason
            # in practice it slows things down a lot
            applied = applied._substitute(target_name, target_substitution)
            argument = argument._substitute(target_name, target_substitution)
            inner_term = applied._apply(argument)

        elif inner_term._is_variable_now() and inner_term._name == target_name:
            # Nothing to rename, because nobody depends on renamed bypassed lambdas
            inner_term = target_substitution

        return inner_term

    def _drop_outer_lambdas(self):
        term = self
        bypassed_names = []
        while term._is_lambda_function_now():
            bypassed_names.append(term._argument_name)
            term = term._body
        return term, bypassed_names

    def _drop_arguments(self):
        term = self

        arguments = []
        while term._is_application_now():
            arguments.append(term._argument)
            term = term._applied
        arguments.reverse()
        applied = term

        return applied, arguments

    def _wrap_in_lambdas(self, lambdas_names):
        term = self
        for argument_name in reversed(lambdas_names):
            term = term._abstract_by(argument_name)
        return term

    def _substitute(self, name, value):
        return self._abstract_by(name)._apply(value)

    def _rename_free_variable(self, old_name, new_name):
        return self._substitute(old_name, self._term_builder.variable(new_name))

    def _apply(self, argument):
        return self._term_builder.application(self, argument)

    def _abstract_by(self, name):
        return self._term_builder.lambda_function(name, self)
