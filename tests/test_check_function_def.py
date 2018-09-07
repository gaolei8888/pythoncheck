import pytest
import helper

from pythonwhat.local import setup_state
from pythonwhat.check_syntax import v2_check_functions
globals().update(v2_check_functions)

@pytest.mark.debug
@pytest.mark.parametrize('stu, passes', [
    ('', False),
    ('def test(): print(3)', False),
    ('def test(x): pass', False),
    ('def test(x): print(x + 2)', False),
    ('def test(x): print(x)', True)
])
def test_check_function_def_basic(stu, passes):
    s = setup_state(stu, 'def test(x): print(x)')
    with helper.verify_sct(passes):
        s.check_function_def('test').multi(
            check_args(0),
            check_body().set_context(1).check_function('print').check_args(0).has_equal_value()
        )

@pytest.mark.parametrize('stu, passes', [
    ('def test(a, b): return 1', False),
    ('def test(a, b): return a + b', False),
    ('''
def test(a, b):
    if a == 3:
        raise ValueError('wrong')
    print(a + b)
    return a + b
''', False),
    ('def test(a, b): print(int(a) + int(b)); return int(a) + int(b)', False),
    ('def test(a, b): print(a + b); return a + b', True)
])
def test_check_call(stu, passes):
    s = setup_state(stu, 'def test(a, b): print(a + b); return a + b')
    with helper.verify_sct(passes):
        s.check_function_def('test').multi(
            check_call("f(1,2)").has_equal_value(),
            check_call("f(1,2)").has_equal_output(),
            check_call("f(3,1)").has_equal_value(),
            check_call("f(1, '2')").has_equal_error()
        )

@pytest.mark.parametrize('stu, passes', [
    ('lambda a,b: 1', False),
    ('lambda a,b: a + b', True)
])
def test_check_call_lambda(stu, passes):
    s = setup_state(stu, 'lambda a, b: a + b')
    with helper.verify_sct(passes):
        s.check_lambda_function().multi(
            check_call("f(1,2)").has_equal_value(),
            check_call("f(1,2)").has_equal_output()
        )

def test_check_call_error_types():
    s = setup_state('def test(): raise NameError("boooo")',
                    'def test(): raise ValueError("boooo")')
    s.check_function_def("test").check_call("f()").has_equal_error()
