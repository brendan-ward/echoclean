from collections import OrderedDict
from echoclean.ruleset import Ruleset


def test_blank():
    ruleset = Ruleset(
        [OrderedDict({'foo': '', 'ret': 'bar'})],
        result_cols=('ret', )
    )

    rows = [
        OrderedDict({'foo': ''}),
        OrderedDict({'foo': ' '}),
        OrderedDict({'foo': 'the_foo'}),
        OrderedDict({'foo': None})
    ]

    # Blank qualifies as any
    for row in rows:
        assert ruleset.test(row) == ['bar']


    ruleset = Ruleset(
        [OrderedDict({'foo': 'blank', 'ret': 'bar'})],
        result_cols=('ret', )
    )
    assert ruleset.test(OrderedDict({'foo': ''})) == ['bar']
    assert ruleset.test(OrderedDict({'foo': None})) == ['bar']
    assert ruleset.test(OrderedDict({'foo': 'the_foo'})) == None



def test_any():
    ruleset = Ruleset(
        [OrderedDict({'foo': 'any', 'ret': 'bar'})],
        result_cols=('ret', )
    )

    ruleset2 = Ruleset(
        [OrderedDict({'foo': 'any including blank', 'ret': 'incl_blank'})],
        result_cols=('ret', )
    )

    # None and '' don't count as values
    empty_rows = [
        OrderedDict({'foo': None}),
        OrderedDict({'foo': ''}),
    ]

    for row in empty_rows:
        assert ruleset.test(row) == ['bar']

    for row in empty_rows:
        assert ruleset2.test(row) == ['incl_blank']


def test_number():
    ruleset = Ruleset(
        [
            OrderedDict({'foo': '3-6', 'ret': '3-6'}),
            OrderedDict({'foo': '<1', 'ret': '<1'}),
            OrderedDict({'foo': '<=1', 'ret': '<=1'}),
            OrderedDict({'foo': 2, 'ret': '2'}),
            OrderedDict({'foo': '>10', 'ret': '>10'}),
            OrderedDict({'foo': '>=10', 'ret': '>=10'})
        ],
        result_cols=('ret', )
    )

    assert ruleset.test(OrderedDict({'foo': 5})) == ['3-6']
    assert ruleset.test(OrderedDict({'foo': 0})) == ['<1']
    assert ruleset.test(OrderedDict({'foo': 1})) == ['<=1']
    assert ruleset.test(OrderedDict({'foo': 2})) == ['2']
    assert ruleset.test(OrderedDict({'foo': 2.5})) is None
    assert ruleset.test(OrderedDict({'foo': 10})) == ['>=10']
    assert ruleset.test(OrderedDict({'foo': 11})) == ['>10']
    assert ruleset.test(OrderedDict({'foo': None})) is None


def test_tokens():
    ruleset = Ruleset(
        [
            OrderedDict({'foo': 'one', 'ret': 'one'}),
            OrderedDict({'foo': 'foo, bar', 'ret': 'foo,bar'}),
            OrderedDict({'foo': 'this, or that', 'ret': 'this,that'}),
            OrderedDict({'foo': 'this, that, or blank', 'ret': 'this or that or blank'}),
            OrderedDict({'foo': 'not something', 'ret': 'not something'}),
            OrderedDict({'foo': 'not blank', 'ret': 'not blank'})
        ],
        result_cols=('ret', )
    )

    assert ruleset.test(OrderedDict({'foo': 'one'})) == ['one']
    assert ruleset.test(OrderedDict({'foo': 'foo'})) == ['foo,bar']
    assert ruleset.test(OrderedDict({'foo': 'bar'})) == ['foo,bar']
    assert ruleset.test(OrderedDict({'foo': 'this'})) == ['this,that']
    assert ruleset.test(OrderedDict({'foo': 'that'})) == ['this,that']
    assert ruleset.test(OrderedDict({'foo': 'something else'})) == ['not something']
    assert ruleset.test(OrderedDict({'foo': 'something'})) == ['not blank']
    assert ruleset.test(OrderedDict({'foo': 'other'})) == ['not something']
    assert ruleset.test(OrderedDict({'foo': ''})) == ['this or that or blank']


def test_compound_rules():
    ruleset = Ruleset(
        [
            OrderedDict({'foo': 'one', 'bar': 'two', 'ret': 'one and two'}),
            OrderedDict({'foo': 'one', 'bar': '>2', 'ret': 'one and >2'}),
            OrderedDict({'foo': 'one', 'bar': '', 'ret': 'one and not bar'})
        ],
        result_cols=('ret', )
    )

    assert ruleset.test(OrderedDict({'foo': 'one', 'bar': ''})) == ['one and not bar']
    assert ruleset.test(OrderedDict({'foo': '', 'bar': ''})) is None
    assert ruleset.test(OrderedDict({'foo': '2', 'bar': 'two'})) is None
    assert ruleset.test(OrderedDict({'foo': 'one', 'bar': 'two'})) == ['one and two']
    assert ruleset.test(OrderedDict({'foo': 'one', 'bar': 3})) == ['one and >2']


#TODO: test multiple return values

# TODO: Validation tests
# Missing columns, bad values, etc