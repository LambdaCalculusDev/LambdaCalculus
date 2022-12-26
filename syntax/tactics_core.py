import functools as _functools


__all__ = (
    'tactic', 'apply_tactic', 'TacticFailed',
    'fail', 'catch_fail', 'ResultOrFail',
    'nothing', 'either', 'maybe',
    'some', 'maybe_some',
    'chain', 'pick',
)


# The way tactics are interpreted
# entirely depends on apply_tactic function used
def apply_tactic(tactic, text, *, cursor_index=None):
    if cursor_index is None:
        result, cursor_index = apply_tactic(tactic, text, cursor_index=0)
        if cursor_index < len(text):
            raise TacticFailed(f'parsing failed on position {cursor_index}')
        return result

    if isinstance(tactic, _CompositeTactic):
        result, cursor_index = _apply_composite_tactic(tactic, text, cursor_index=cursor_index)

    elif isinstance(tactic, str):
        result, cursor_index = _apply_string_tactic(tactic, text, cursor_index=cursor_index)

    elif isinstance(tactic, _CatchFailTacticWrapper):
        result, cursor_index = _apply_tactic_catching_fail(tactic.tactic, text, cursor_index=cursor_index)

    elif isinstance(tactic, _TacticFail):
        raise TacticFailed(tactic.fail_info)

    else:
        raise TypeError('not a parsing tactic', tactic)

    return result, cursor_index


def _apply_composite_tactic(tactic, text, *, cursor_index):
    spawned_tactic = tactic()
    latest_tactic_result = None

    while True:
        try:
            next_tactic = spawned_tactic.send(latest_tactic_result)
        except StopIteration as stop_iteration:
            result = stop_iteration.value
            return result, cursor_index
        # May raise TacticFailed
        latest_tactic_result, cursor_index = apply_tactic(next_tactic, text, cursor_index=cursor_index)


def tactic(generator_spawner):
    @_functools.wraps(generator_spawner)
    def make_tactic_by_args(*args, **kwargs):
        ready_generator_spawner = _functools.partial(generator_spawner, *args, **kwargs)
        return _CompositeTactic(ready_generator_spawner)
    return make_tactic_by_args


class _CompositeTactic:

    def __init__(self, generator_spawner):
        self._generator_spawner = generator_spawner

    def __call__(self):
        return self._generator_spawner()


def _apply_string_tactic(tactic, text, *, cursor_index):
    string_required = tactic
    if not text.startswith(string_required, cursor_index):
        raise TacticFailed(f'{repr(string_required)} not found')
    cursor_index += len(string_required)
    return string_required, cursor_index


def _apply_tactic_catching_fail(tactic, text, *, cursor_index):
    try:
        result, cursor_index = apply_tactic(tactic, text, cursor_index=cursor_index)
    except TacticFailed as tactic_fail:
        result = ResultOrFail(tactic_fail.fail_info, failed=True)
    else:
        result = ResultOrFail(result, failed=False)
    return result, cursor_index


class TacticFailed(ValueError):

    def __init__(self, fail_info):
        self._fail_info = fail_info

    @property
    def fail_info(self):
        return self._fail_info


@tactic
def fail(fail_info):
    yield _TacticFail(fail_info)


class _TacticFail:

    def __init__(self, fail_info):
        self._fail_info = fail_info

    @property
    def fail_info(self):
        return self._fail_info


def catch_fail(tactic):
    return _CatchFailTacticWrapper(tactic)


class _CatchFailTacticWrapper:

    def __init__(self, tactic):
        self._tactic = tactic

    @property
    def tactic(self):
        return self._tactic


class ResultOrFail:

    def __init__(self, value, *, failed):
        self._failed = failed
        if self._failed:
            self._fail_info = value
        else:
            self._result = value

    @property
    def failed(self):
        return self._failed

    @property
    def result(self):
        return self._result

    @property
    def fail_info(self):
        return self._fail_info


@tactic
def nothing():
    return
    yield


nothing = nothing()


@tactic
def either(*tactics_to_try):
    for tactic in tactics_to_try:
        applied_tactic = yield catch_fail(tactic)
        if not applied_tactic.failed:
            return applied_tactic.result
    yield fail('All tactics failed')


@tactic
def maybe(tactic, *, otherwise=None):
    parsing = yield catch_fail(tactic)
    if not parsing.failed:
        result = parsing.result
    else:
        result = otherwise
    return result


@tactic
def some(element_tactic, sep=nothing):
    first_element = yield element_tactic

    @tactic
    def read_next():
        yield sep
        parsed_element = yield element_tactic
        return parsed_element

    other_elements = yield _cycle(read_next())

    return [first_element, *other_elements]


@tactic
def _cycle(element_tactic):
    parsed_elements = []
    element_parsing = yield catch_fail(element_tactic)
    while not element_parsing.failed:
        parsed_elements.append(element_parsing.result)
        element_parsing = yield catch_fail(element_tactic)
    return parsed_elements


@tactic
def maybe_some(element, sep=nothing):
    some_elements = some(element, sep=sep)
    result = yield maybe(some_elements, otherwise=[])
    return result


@tactic
def chain(*tactics):
    results = []
    for tactic in tactics:
        if isinstance(tactic, _PickThisTacticResultWrapper):
            results.append((yield tactic.tactic))
        else:
            yield tactic
    return results


def pick(tactic):
    return _PickThisTacticResultWrapper(tactic)


class _PickThisTacticResultWrapper:
    def __init__(self, tactic):
        self._tactic = tactic

    @property
    def tactic(self):
        return self._tactic
