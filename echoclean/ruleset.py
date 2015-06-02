import re
import copy

NUMBER_RE = re.compile('\d+\.*\d*')
COMPARATOR_RE = re.compile('[<>]=*')
EMPTY_VALUES = (None, '', 'blank')


class Ruleset(object):
    def __init__(self, rules, result_cols):
        self.rules = [Rule(rule, result_cols) for rule in rules]

    def test(self, row):
        # Standardize row values to match criteria
        test_row = copy.deepcopy(row)  # need to copy so we don't alter original row
        for key, value in test_row.iteritems():
            if isinstance(value, basestring):
                test_row[key] = value.lower().strip()
            if test_row[key] in EMPTY_VALUES:
                test_row[key] = None

        for i, rule in enumerate(self.rules):
            result = rule.test(test_row)
            if result:
                return result

        # No matches
        return None


class Rule(object):
    def __init__(self, rule, result_cols):
        self._result = []
        for col in result_cols:
            self._result.append(rule.pop(col))

        # TODO: try / except block
        self.criteria = {k: Criterion(v) for k, v in rule.iteritems()}

    def test(self, row):
        for key, criterion in self.criteria.iteritems():
            if not criterion.test(row[key]):
                return None

        # If it didn't fail, it must have passed
        return list(self._result)  # return a copy


class Criterion(object):
    def __init__(self, criterion):
        # Mutually exclusive options
        self.is_blank = False
        self.is_any = False
        self.is_number = False
        # Otherwise use set logic for self.values

        self.values = None
        self.comparator = None  # either inequality expression if self.is_number or 'not' if self.values is a set

        if criterion is not None:
            criterion = str(criterion).strip().lower()

        if criterion == 'blank':  # TODO: document this change
            self.is_blank = True
            return

        if criterion in ('any', None, ''):  # TODO: document this change
            self.is_any = True
            return

        numbers = NUMBER_RE.findall(criterion)
        if numbers:
            self.is_number = True
            self.values = [float(n) for n in numbers]
            if len(self.values) > 2:
                raise ValueError('Too many values for comparison')
            elif len(self.values) == 1:
                comparator = COMPARATOR_RE.search(criterion)
                if comparator:
                    self.comparator = comparator.group()
            return

        # 'or' is unnecessary in list of tokens, it is implicit
        tokens = [c.strip().replace('or ', '') for c in criterion.split(',')]
        for index, token in enumerate(tokens):
            if token in EMPTY_VALUES:
                tokens[index] = None
            elif token.startswith('not '):
                self.comparator = 'not'
                token = token.replace('not ', '')
                if token in EMPTY_VALUES:
                    token = None
                tokens[index] = token
                break  # Only expect one not condition

        self.values = set(tokens)

    def test(self, value):
        if self.is_blank:
            return value in EMPTY_VALUES

        elif self.is_any:
            return True

        elif self.is_number:
            if value in EMPTY_VALUES:
                return False

            num_values = len(self.values)
            value = float(value)
            if num_values == 1:
                if self.comparator is None:
                    return value == self.values[0]
                else:
                    return eval('{0} {1} {2}'.format(value, self.comparator, self.values[0]))
            else:
                return value >= self.values[0] and value <= self.values[1]

        elif self.comparator == 'not':
            # Value must be non-blank
            if value in EMPTY_VALUES:
                return False
            return value not in self.values
        else:
            return value in self.values
