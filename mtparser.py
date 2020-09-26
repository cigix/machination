'''Package mtparser: Defines utilities to turn a Turing machine description into
a set of rules.
'''

class Rule:
    '''Attributes:
      - match: str, the symbol to match against
      - write: str, the symbol to write
      - direction: int, the direction to shift to (one of -1, 0, 1)
      - state: str, the state to go to
    '''
    def __init__(self, match, write, direction, state):
        '''Rule(match, write, direction, state): Instanciate a Rule

        Parameters:
          - match: str, the symbol to match against
          - write: str, the symbol to write
          - direction: int or str, the direction to shift to
          - state: str, the state to go to

        If `write` is "SAME", it is replaced with `match`.

        If `direction` is a str, "left" is replaced with -1, "right" is replaced
        with 1.

        Raise ValueError if `direction` is anything other than "left", "right",
        -1, 0, or 1.
        '''
        self.match = match
        self.write = match if write == "SAME" else write
        if isinstance(direction, int):
            if -1 <= direction <= 1:
                self.direction = direction
            else:
                raise ValueError(f'direction "{direction}" outside of [-1 .. 1]')
        elif isinstance(direction, str):
            if direction == "left":
                self.direction = -1
            elif direction == "right":
                self.direction = 1
            else:
                raise ValueError(f'unknown direction "{direction}"')
        else:
            raise ValueError("unknown type for direction")
        self.state = state

def parse(mtdesc, alphabet):
    '''parse(mtdesc, alphabet): Parse a Turing machine description

    Parameters:
      - mtdesc: dict, the Turing machine description
      - alphabet: str, the set of symbols

    Return: dict of str to list of Rules

    Flatten a Turing machine description (see the
    [https://github.com/cigix/machination/blob/main/README.md](Syntax Document))
    into a dictionary where the keys are names of states and the values are
    lists of Rules. All context-specific symbols are expanded, all
    state-templates replaced with their instanciations.

    On top of the given alphabet, parse() injects two symbols, "NUL" and "EOT".
    '''
    symbols = set(alphabet)
    symbols.add("NUL")
    symbols.add("EOT")

    states = dict()

    def parsestate(name):
        '''parsestate(name): Flatten a single state

        Parameters:
          - name: str, the name of the state

        Side-effects: read from `mtdesc` and `states`, write to `states`
        '''
        rulesdesc = mtdesc[name]

        # Split out the explicit symbols and rules, and the "ELSE" rule
        # Replace the destination state
        explicitsymbols = set()
        elserule = None
        rules = list() # list of Rules
        for symbol, (write, direction, state) in rulesdesc.items():
            if state == "SAME":
                state = name

            if symbol == "ELSE":
                elserule = (write, direction, state)
            else:
                explicitsymbols.add(symbol)
                rules.append(Rule(symbol, write, direction, state))

        if elserule is not None:
            # For every non explicit symbol
            for symbol in symbols - explicitsymbols:
                rules.append(Rule(symbol, *elserule))

        for rule in rules:
            if rule.state[-1] == '.':
                rule.state = instanciatetemplate(rule.state, rule.match)

        states[name] = rules

    def instanciatetemplate(name, instsymbol):
        '''instanciatetemplate(name, instsymbol): Instanciate a state-template

        Parameters:
          - name: str, the name of the state-template
          - instsymbol: str, the instanciation symbol

        Side-effects: read from `mtdesc` and `states`, write to `states`

        Return: str, the name of the instanciated state

        Raise ValueError if `name` does not end with a dot.
        '''
        if name[-1] != '.':
            raise ValueError(f'"{name}" does not end with a dot')
        instanciationname = name[:-1] + instsymbol
        if instanciationname in states:
            # already instanciated, nothing to do
            return instanciationname
        # Avoid infinite recursion
        states[instanciationname] = None

        rulesdesc = mtdesc[name]

        explicitsymbols = set()
        elserule = None
        rules = list() # list of Rules
        for symbol, (write, direction, state) in rulesdesc.items():
            if symbol == "DOT":
                symbol = instsymbol
            if write == "DOT":
                write = instsymbol

            if state == "SAME":
                state = instanciationname

            if symbol == "ELSE":
                elserule = (write, direction, state)
            else:
                explicitsymbols.add(symbol)
                rules.append(Rule(symbol, write, direction, state))

        if elserule is not None:
            for symbol in symbols - explicitsymbols:
                rules.append(Rule(symbol, *elserule))

        for rule in rules:
            if rule.state[-1] == '.':
                rule.state = instanciatetemplate(rule.state, instsymbol)

        states[instanciationname] = rules
        return instanciationname

    for name in mtdesc.keys():
        if name[-1] != '.':
            parsestate(name)

    return states
