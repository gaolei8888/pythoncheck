import pytest
import helper
from pythoncheck.Reporter import Reporter
from difflib import Differ

def message(output, patt):
    return Reporter.to_html(patt) == output['message']

def lines(output, s, e):
    if s and e:
        return output['column_start'] == s and output['column_end'] == e
    else:
        return True

# Check Function Call ---------------------------------------------------------

@pytest.mark.parametrize('stu, patt, cols, cole', [
    ('', 'Did you call `round()`?', None, None),
    ('round(1)', 'Check your call of `round()`. Did you specify the second argument?', 1, 8),
    ('round(1, a)', 'Check your call of `round()`. Did you correctly specify the second argument? Running it generated an error: `name \'a\' is not defined`.', 10, 10),
    ('round(1, 2)', 'Check your call of `round()`. Did you correctly specify the second argument? Expected `3`, but got `2`.', 10, 10),
    ('round(1, ndigits = 2)', 'Check your call of `round()`. Did you correctly specify the second argument? Expected `3`, but got `2`.', 10, 20)
])
def test_check_function_pos(stu, patt, cols, cole):
    output = helper.run({
        'DC_CODE': stu,
        'DC_SOLUTION': 'round(1, 3)',
        'DC_SCT': 'Ex().check_function("round").check_args(1).has_equal_value()'
    })
    assert not output['correct']
    assert message(output, patt)
    assert lines(output, cols, cole)

@pytest.mark.parametrize('stu, patt, cols, cole', [
    ('round(1)', 'Check your call of `round()`. Did you specify the argument `ndigits`?', 1, 8),
    ('round(1, a)', 'Check your call of `round()`. Did you correctly specify the argument `ndigits`? Running it generated an error: `name \'a\' is not defined`.', 10, 10),
    ('round(1, 2)', 'Check your call of `round()`. Did you correctly specify the argument `ndigits`? Expected `3`, but got `2`.', 10, 10)
])
def test_check_function_named(stu, patt, cols, cole):
    output = helper.run({
        'DC_CODE': stu,
        'DC_SOLUTION': 'round(1, 3)',
        'DC_SCT': 'Ex().check_function("round").check_args("ndigits").has_equal_value()'
    })
    assert not output['correct']
    assert message(output, patt)
    assert lines(output, cols, cole)

@pytest.mark.parametrize('stu, patt, cols, cole', [
    ('round(3)', 'Check your call of `round()`. Did you correctly specify the first argument? Expected `2`, but got `3`.', 7, 7),
    ('round(1 + 1)', 'Check your call of `round()`. Did you correctly specify the first argument? Expected `2`, but got `1 + 1`.', 7, 11)
])
def test_check_function_ast(stu, patt, cols, cole):
    output = helper.run({
        'DC_CODE': stu,
        'DC_SOLUTION': 'round(2)',
        'DC_SCT': 'Ex().check_function("round").check_args(0).has_equal_ast()'
    })
    assert not output['correct']
    assert message(output, patt)
    assert lines(output, cols, cole)

@pytest.mark.parametrize('stu, patt, cols, cole', [
    ('list("wrong")', 'Check your call of `list()`. Did you correctly specify the first argument? Expected `"test"`, but got `"wrong"`.', 6, 12),
    ('list("te" + "st")', 'Check your call of `list()`. Did you correctly specify the first argument? Expected `"test"`, but got `"te" + "st"`.', 6, 16)
])
def test_check_function_ast2(stu, patt, cols, cole):
    output = helper.run({
        'DC_CODE': stu,
        'DC_SOLUTION': 'list("test")',
        'DC_SCT': 'Ex().check_function("list", signature = False).check_args(0).has_equal_ast()'
    })
    assert not output['correct']
    assert message(output, patt)
    assert lines(output, cols, cole)

@pytest.mark.parametrize('stu, patt, cols, cole', [
    ('round(a)', 'Check your call of `round()`. Did you correctly specify the first argument? Expected `b`, but got `a`.', 7, 7),
    ('round(b + 1 - 1)', 'Check your call of `round()`. Did you correctly specify the first argument? Expected `b`, but got `b + 1 - 1`.', 7, 15)
])
def test_check_function_ast3(stu, patt, cols, cole):
    output = helper.run({
        'DC_PEC': 'a = 3\nb=3',
        'DC_CODE': stu,
        'DC_SOLUTION': 'round(b)',
        'DC_SCT': 'Ex().check_function("round", signature = False).check_args(0).has_equal_ast()'
    })
    assert not output['correct']
    assert message(output, patt)
    assert lines(output, cols, cole)

@pytest.mark.parametrize('stu, patt', [
    ('import pandas as pd', 'Did you call `pd.DataFrame()`?'),
    ('import pandas as pad', 'Did you call `pad.DataFrame()`?'),
])
def test_check_function_pkg1(stu, patt):
    output = helper.run({
        "DC_SOLUTION": "import pandas as pd; pd.DataFrame({'a': [1, 2, 3]})",
        "DC_CODE": stu,
        "DC_SCT": "test_function_v2('pandas.DataFrame')"
    })
    assert not output['correct']
    assert message(output, patt)

@pytest.mark.parametrize('stu, patt', [
    ('import numpy as nump', 'Did you call `nump.random.rand()`?'),
    ('from numpy.random import rand as r', 'Did you call `r()`?'),
])
def test_check_function_pkg2(stu, patt):
    output = helper.run({
        "DC_SOLUTION": "import numpy as np; x = np.random.rand(1)",
        "DC_CODE": stu,
        "DC_SCT": "test_function_v2('numpy.random.rand')"
    })
    assert not output['correct']
    assert message(output, patt)

@pytest.mark.parametrize('stu, patt', [
    ('', 'Did you call `round()`?'),
    ('round(1)', 'Did you call `round()` twice?'),
    ('round(1)\nround(5)', 'Check your second call of `round()`. Did you correctly specify the first argument? Expected `2`, but got `5`.'),
    ('round(1)\nround(2)', 'Did you call `round()` three times?'),
    ('round(1)\nround(2)\nround(5)', 'Check your third call of `round()`. Did you correctly specify the first argument? Expected `3`, but got `5`.'),
])
def test_multiple_check_functions(stu, patt):
    output = helper.run({
        'DC_CODE': stu,
        'DC_SOLUTION': 'round(1)\nround(2)\nround(3)',
        'DC_SCT': 'Ex().multi([ check_function("round", index=i).check_args(0).has_equal_value() for i in range(3) ])'
    })
    assert not output['correct']
    assert message(output, patt)

@pytest.mark.parametrize('stu, patt, cols, cole', [
    ("df.groupby('a')", "Check your call of `df.groupby()`. Did you correctly specify the first argument? Expected `'b'`, but got `'a'`.", 12, 14),
    ("df.groupby('b').a.value_counts()", 'Check your call of `df.groupby.a.value_counts()`. Did you specify the argument `normalize`?', 1, 32),
    ("df[df.b == 'x'].groupby('b').a.value_counts()", 'Check your call of `df.groupby.a.value_counts()`. Did you specify the argument `normalize`?', 1, 45),
])
def test_check_method(stu, patt, cols, cole):
    output = helper.run({
        'DC_PEC': "import pandas as pd; df = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'x', 'y']})",
        'DC_CODE': stu,
        'DC_SOLUTION': "df.groupby('b').a.value_counts(normalize = True)",
        'DC_SCT': """
from pythoncheck.signatures import sig_from_obj
import pandas as pd
Ex().check_function('df.groupby').check_args(0).has_equal_ast()
Ex().check_function('df.groupby.a.value_counts', signature = sig_from_obj(pd.Series.value_counts)).check_args('normalize').has_equal_ast()
        """
    })
    assert not output['correct']
    assert message(output, patt)
    assert lines(output, cols, cole)


# Check Object ----------------------------------------------------------------

@pytest.mark.parametrize('stu, patt, cols, cole', [
    ('', 'Did you define the variable `x` without errors?', None, None),
    ('x = 2', 'Did you correctly define the variable `x`? Expected `5`, but got `2`.', 1, 5)
])
def test_check_object(stu, patt, cols, cole):
    output = helper.run({
        'DC_CODE': stu,
        'DC_SOLUTION': 'x = 5',
        'DC_SCT': 'Ex().check_object("x").has_equal_value()'
    })
    assert not output['correct']
    assert message(output, patt)
    assert lines(output, cols, cole)

@pytest.mark.parametrize('sct', [
    "test_data_frame('df', columns=['a'])",
    "import pandas as pd; Ex().check_object('df', typestr = 'pandas DataFrame').is_instance(pd.DataFrame).check_keys('a').has_equal_value()"
])
@pytest.mark.parametrize('stu, patt, cols, cole', [
    ('df = 3', 'Did you correctly define the pandas DataFrame `df`? Is it a DataFrame?', 1, 6),
    ('df = pd.DataFrame({"b": [1]})', 'Did you correctly define the pandas DataFrame `df`? There is no column `\'a\'`.', 1, 29),
    ('df = pd.DataFrame({"a": [1]})', 'Did you correctly define the pandas DataFrame `df`? Did you correctly set the column `\'a\'`? Expected something different.', 1, 29),
    ('y = 3; df = pd.DataFrame({"a": [1]})', 'Did you correctly define the pandas DataFrame `df`? Did you correctly set the column `\'a\'`? Expected something different.', 8, 36)
])
def test_test_data_frame_no_msg(sct, stu, patt, cols, cole):
    output = helper.run({
        'DC_PEC': 'import pandas as pd',
        'DC_SOLUTION': 'df = pd.DataFrame({"a": [1, 2, 3]})',
        'DC_CODE': stu,
        'DC_SCT': sct
    })
    assert not output['correct']
    assert message(output, patt)
    assert lines(output, cols, cole)

@pytest.mark.parametrize('stu_code, patt, cols, cole', [
    ('x = {}', 'Did you correctly define the variable `x`? There is no key `\'a\'`.', 1, 6),
    ('x = {"b": 3}', 'Did you correctly define the variable `x`? There is no key `\'a\'`.', 1, 12),
    ('x = {"a": 3}', 'Did you correctly define the variable `x`? Did you correctly set the key `\'a\'`? Expected `2`, but got `3`.', 1, 12),
    ('y = 3; x = {"a": 3}', 'Did you correctly define the variable `x`? Did you correctly set the key `\'a\'`? Expected `2`, but got `3`.', 8, 19),
])
def test_check_keys(stu_code, patt, cols, cole):
    output = helper.run({
        'DC_SOLUTION': 'x = {"a": 2}',
        'DC_CODE': stu_code,
        'DC_SCT': 'Ex().check_object("x").check_keys("a").has_equal_value()'
    })
    assert not output['correct']
    assert message(output, patt)
    assert lines(output, cols, cole)

@pytest.mark.parametrize('stu, patt', [
    ('round(2.34)', 'argrwong'),
    ('round(1.23)', 'objectnotdefined'),
    ('x = round(1.23) + 1', 'objectincorrect')
])
def test_check_object_manual(stu, patt):
    output = helper.run({
        'DC_CODE': stu,
        'DC_SOLUTION': 'x = round(1.23)',
        'DC_SCT': """
Ex().check_function('round').check_args(0).has_equal_value(incorrect_msg = 'argrwong')
Ex().check_object('x', missing_msg='objectnotdefined').has_equal_value('objectincorrect')
"""
    })
    assert not output['correct']
    assert message(output, patt)

# Check call ------------------------------------------------------------------

@pytest.mark.parametrize('stu, patt', [
    ('', 'The system wants to check the definition of `test()` but hasn\'t found it.'),
    ('def test(a, b): return 1', 'Check the definition of `test()`. To verify it, we reran `test(1, 2)`. Expected `3`, but got `1`.'),
    ('def test(a, b): return a + b', 'Check the definition of `test()`. To verify it, we reran `test(1, 2)`. Expected the output `3`, but got `no printouts`.'),
    ('''
def test(a, b):
    if a == 3:
        raise ValueError('wrong')
    print(a + b)
    return a + b
''', 'Check the definition of `test()`. To verify it, we reran `test(3, 1)`. Running the higlighted expression generated an error: `wrong`.'),
    ('def test(a, b): print(int(a) + int(b)); return int(a) + int(b)', 'Check the definition of `test()`. To verify it, we reran `test(1, "2")`. Running the higlighted expression didn\'t generate an error, but it should!'),
])
def test_check_call(stu, patt):
    output = helper.run({
        'DC_CODE': stu,
        'DC_SOLUTION': 'def test(a, b): print(a + b); return a + b',
        'DC_SCT': """
Ex().check_function_def('test').multi(
    check_call('f(1, 2)').has_equal_value(),
    check_call('f(1, 2)').has_equal_output(),
    check_call('f(3, 1)').has_equal_value(),
    check_call('f(1, "2")').has_equal_error()
)"""
    })
    assert not output['correct']
    assert message(output, patt)

@pytest.mark.parametrize('stu, patt', [
    ('echo_word = (lambda word1, echo: word1 * echo * 2)', "Check the first lambda function. To verify it, we reran it with the arguments `('test', 2)`. Expected `testtest`, but got `testtesttesttest`.")
])
def test_check_call_lambda(stu, patt):
    output = helper.run({
        'DC_SOLUTION': 'echo_word = (lambda word1, echo: word1 * echo)',
        'DC_CODE': stu,
        'DC_SCT': "Ex().check_lambda_function().check_call(\"f('test', 2)\").has_equal_value()"
    })
    assert not output['correct']
    assert message(output, patt)

## has_import -----------------------------------------------------------------

@pytest.mark.parametrize('stu, patt', [
    ('', 'Did you import `pandas`?'),
    ('import pandas', 'Did you import `pandas` as `pd`?'),
    ('import pandas as pan', 'Did you import `pandas` as `pd`?')
])
def test_has_import(stu, patt):
    output = helper.run({
        'DC_CODE': stu,
        'DC_SOLUTION': 'import pandas as pd',
        'DC_SCT': "Ex().has_import('pandas', same_as=True)"
    })
    assert not output['correct']
    assert message(output, patt)

@pytest.mark.parametrize('stu, patt', [
    ('', 'wrong'),
    ('import pandas', 'wrongas'),
    ('import pandas as pan', 'wrongas')
])
def test_has_import_custom(stu, patt):
    output = helper.run({
        'DC_CODE': stu,
        'DC_SOLUTION': 'import pandas as pd',
        'DC_SCT': "Ex().has_import('pandas', same_as=True, not_imported_msg='wrong', incorrect_as_msg='wrongas')"
    })
    assert not output['correct']
    assert message(output, patt)

## Check has_equal_x ----------------------------------------------------------

@pytest.mark.parametrize('stu, patt, cols, cole', [
    ("my_dict = {'a': 1, 'b': 2}\nfor key, value in my_dict.items(): x = key + ' -- ' + str(value)",
     "Check the first for statement. Did you correctly specify the body? Are you sure you assigned the correct value to `x`?",
     36, 64),
    ("my_dict = {'a': 1, 'b': 2}\nfor key, value in my_dict.items(): x = key + ' - ' + str(value)",
     "Check the first for statement. Did you correctly specify the body? Expected the output `a - 1`, but got `no printouts`.",
     36, 63)
])
def test_has_equal_x(stu, patt, cols, cole):
    output = helper.run({
        'DC_SOLUTION': "my_dict = {'a': 1, 'b': 2}\nfor key, value in my_dict.items():\n    x = key + ' - ' + str(value)\n    print(x)",
        'DC_CODE': stu,
        'DC_SCT': "Ex().check_for_loop().check_body().set_context('a', 1).multi(has_equal_value(name = 'x'), has_equal_output())"
    })
    assert not output['correct']
    assert message(output, patt)
    assert lines(output, cols, cole)

@pytest.mark.parametrize('stu, patt, cols, cole', [
    ('result = (num for num in range(3))', 'Check the first generator expression. Did you correctly specify the iterable part? Expected `range(0, 31)`, but got `range(0, 3)`.', 26, 33),
    ('result = (num*2 for num in range(31))', 'Check the first generator expression. Did you correctly specify the body? Expected `4`, but got `8`.', 11, 15)
])
def test_has_equal_x_2(stu, patt, cols, cole):
    output = helper.run({
        'DC_SOLUTION': 'result = (num for num in range(31))',
        'DC_CODE': stu,
        'DC_SCT': "Ex().check_generator_exp().multi(check_iter().has_equal_value(), check_body().set_context(4).has_equal_value())"
    })
    assert not output['correct']
    assert message(output, patt)
    assert lines(output, cols, cole)

## test_correct ---------------------------------------------------------------

@pytest.mark.parametrize('stu, patt', [
    ('', 'Did you define the variable `a` without errors?'),
    ('a = 1', 'Did you define the variable `b` without errors?'),
    ('a = 1; b = a + 1', 'Did you define the variable `c` without errors?'),
    ('a = 1; b = a + 1; c = b + 1', 'Have you used `print(c)` to do the appropriate printouts?'),
    ('print(4)', 'Did you define the variable `a` without errors?'),
    ('c = 3; print(c + 1)', 'Have you used `print(c)` to do the appropriate printouts?'),
    ('b = 3; c = b + 1; print(c)', 'Did you define the variable `a` without errors?'),
    ('a = 2; b = a + 1; c = b + 1', 'Did you correctly define the variable `a`? Expected `1`, but got `2`.'),
])
def test_nesting(stu, patt):
    output = helper.run({
        'DC_SOLUTION': 'a = 1; b = a + 1; c = b + 1; print(c)',
        'DC_CODE': stu,
        'DC_SCT': '''
Ex().test_correct(
    has_printout(0),
    F().test_correct(
        check_object('c').has_equal_value(),
        F().test_correct(
            check_object('b').has_equal_value(),
            check_object('a').has_equal_value()
        )
    )
)
        '''
    })
    assert not output['correct']
    assert message(output, patt)

## test limited stacking ------------------------------------------------------

@pytest.mark.parametrize('sct, patt', [
    ('Ex().check_for_loop().check_body().check_for_loop().check_body().has_equal_output()',
        'Check the first for statement. Did you correctly specify the body? Expected the output `1+1`, but got `1-1`.'),
    ('Ex().check_for_loop().check_body().check_for_loop().disable_highlighting().check_body().has_equal_output()',
        'Check the first for statement. Did you correctly specify the body? Check the first for statement. Did you correctly specify the body? Expected the output `1+1`, but got `1-1`.')
])
def test_limited_stacking(sct, patt):
    code = '''
for i in range(2):
    for j in range(2):
        print(str(i) + "%s" + str(j))
'''
    output = helper.run({
        'DC_CODE': code % '-',
        'DC_SOLUTION': code % '+',
        'DC_SCT': sct
    })
    assert not output['correct']
    assert message(output, patt)

## test has_expr --------------------------------------------------------------

@pytest.mark.parametrize('sct, patt', [
    ("Ex().check_object('x').has_equal_value()", 'Did you correctly define the variable `x`? Expected `[1]`, but got `[0]`.'),
    ("Ex().has_equal_value(name = 'x')", 'Are you sure you assigned the correct value to `x`?'),
    ("Ex().has_equal_value(expr_code = 'x[0]')", "Running the expression `x[0]` didn't generate the expected result.")
])
def test_has_expr(sct, patt):
    output = helper.run({
        'DC_SOLUTION': 'x = [1]',
        'DC_CODE': 'x = [0]',
        'DC_SCT': sct
    })
    assert not output['correct']
    assert message(output, patt)