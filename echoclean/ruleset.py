import re
import copy
import logging


logger = logging.getLogger('echoclean')


NUMBER_RE = re.compile('\d+\.*\d*')
COMPARATOR_RE = re.compile('[<>]=*')
EMPTY_VALUES = (None, '', 'blank')


class Ruleset(object):
    def __init__(self, rules, result_cols):
        self.rules = [Rule(rule, result_cols) for rule in rules]

    def __repr__(self):
        return '---------------------------\n'.join([str(rule) for rule in self.rules])

    def test(self, row):
        # Standardize row values to match criteria
        test_row = copy.deepcopy(row)  # need to copy so we don't alter original row
        for key, value in test_row.iteritems():
            if isinstance(value, basestring):
                test_row[key] = value.lower().strip()
            if test_row[key] in EMPTY_VALUES:
                test_row[key] = None

        for i, rule in enumerate(self.rules):
            logger.debug('testing against rule #{0}'.format(i))
            result = rule.test(test_row)
            if result:
                logger.info('PASSED rule #{0}\n-----------------------------------'.format(i))
                return result

            logger.info('FAILED rule #{0}\n-----------------------------------'.format(i))

        # No matches
        logger.debug('FAILED ALL RULES')
        return None


class Rule(object):
    def __init__(self, rule, result_cols):
        self._result = []
        for col in result_cols:
            self._result.append(rule.pop(col))

        # TODO: try / except block
        self.criteria = {k: Criterion(v) for k, v in rule.iteritems()}

    def __repr__(self):
        return '\n'.join(['{0}: {1}'.format(k, v) for k,v in self.criteria.iteritems()])

    def test(self, row):
        for key, criterion in self.criteria.iteritems():
            value = row[key]
            passed = criterion.test(row[key])
            is_blank = value in EMPTY_VALUES

            if passed:
                logger.debug('({0}: {1}) with {2} ==> PASSED'.format(
                    key, criterion, 'blank' if is_blank else value))
            else:
                logger.info('({0}: {1}) with {2} ==> FAILED'.format(
                    key, criterion, 'blank' if is_blank else value))
                return None

        # If it didn't fail, it must have passed
        return list(self._result)  # return a copy


class Criterion(object):
    def __init__(self, criterion):
        # Mutually exclusive options
        self.is_blank = False
        self.allows_blank = False  # blank is one of several options allowed
        self.is_any = False
        self.is_number = False
        # Otherwise use set logic for self.values

        self.values = None
        self.comparator = None  # either inequality expression if self.is_number or 'not' if self.values is a set

        if criterion is not None:
            criterion = str(criterion).strip().lower()

        if criterion == 'blank':
            self.is_blank = True
            return

        if criterion in ('any', None, '', 'any including blank'):
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
        criterion = criterion.replace(' or ', ',').replace(',or', ',')  # TODO: refactor as a regex
        tokens = [c.strip().replace('or ', ',') for c in criterion.split(',')]
        # need to filter a little further
        tokens = [t for t in tokens if t]
        self.values = set()
        for token in tokens:
            if not token:
                continue
            elif token in EMPTY_VALUES:
                self.allows_blank = True
            elif token.startswith('not '):
                self.comparator = 'not'
                token = token.replace('not ', '').strip()
                # if token in EMPTY_VALUES:  # Not sure what I was doing here!  FIXME!
                #     token = None
                # tokens[index] = token
                self.values.add(token)
                break  # Only expect one not condition
            else:
                self.values.add(token)

    def __repr__(self):
        if self.is_blank:
            return 'blank'
        elif self.is_any:
            return 'any'
        elif self.is_number:
            if len(self.values) == 1:
                return '{0} {1}'.format(self.comparator or '==', self.values[0])
            else:
                return '{0} - {1}'.format(self.values[0], self.values[1])
        else:
            return '{0}IN: [{1}]{2}'.format(
                self.comparator.upper() + ' ' if self.comparator is not None else '',
                ','.join([str(v) for v in self.values]),
                ' (allows blank)' if self.allows_blank else ''
            )

    def test(self, value):
        value_is_blank = value in EMPTY_VALUES
        if self.is_blank:
            return value_is_blank

        elif self.is_any:
            return True

        elif self.allows_blank and value_is_blank:
            return True

        elif self.is_number:
            if value_is_blank:
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
            # if value_is_blank:
            #     return False
            return value not in self.values
        else:

            if value_is_blank:
                value = 'blank'
            logger.debug('value is {0} testing {1}'.format(value, self.values))
            return value in self.values
