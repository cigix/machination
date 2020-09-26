'''Package mtoutput: Various output drivers for Turing machines.

Every driver exhibits the following methods:
  - formatrule(state:str, rule:mtparser.Rule) -> str
      Format one rule
  - formatstate(state:str, rules:list of mtparser.Rule) -> str
      Format a state
  - formatstates(states:dict of str to list of mtparser.Rule) -> str
      Format a set of states
  - formatmt(states:dict of str to list of mtparser.Rule) -> str
      Format a set of states; assuming that set is complete and final
'''

class OutputDriver:
    '''Default implementation of an output driver. You should not use this class
    directly, rather heritate from it.'''
    def formatrule(self, state, rule):
        '''formatrule(self, state, rule): Format a rule

        Parameters:
          - state: str, the name of the state
          - rule: mtparser.Rule, the rule to format

        Return: str, the formatted rule
        '''
        raise NotImplementedError

    def formatstate(self, state, rules):
        '''formatstate(self, state, rules): Format a state

        Parameters:
          - state: str, the name of the state
          - rules: list of mtparser.Rule, the rules of the state

        Return: str, the formatted state
        '''
        return '\n'.join(self.formatrule(state, rule) for rule in rules)

    def formatstates(self, states):
        '''formatstate(self, state, rules): Format a state

        Parameters:
          - states: dict of str to list of mtparser.Rule, the states to format

        Return: str, the formatted states
        '''
        return '\n'.join(self.formatstate(state, rules)
                         for state, rules in states.items())

    formatmt = formatstates

class Human(OutputDriver):
    '''Format a Turing machine as humanly as possible'''
    def formatrule(self, _, rule):
        match = f"{rule.match}:"
        write = f'"{rule.write}",'
        direction = ["0,", "right,", "left,"][rule.direction]
        return f"  {match:4} {write:6} {direction:6} {rule.state}"

    def formatstate(self, state, rules):
        return '\n'.join([f"{state}:"]
                         + [OutputDriver.formatstate(self, state, rules)])

class Formal(OutputDriver):
    '''Format a Turing machine as formally as possible'''
    def formatrule(self, state, rule):
        direction = ["final", "right", "left"][rule.direction]
        return (f"({state}, {rule.match}) -> "
                f"({rule.write}, {direction}, {rule.state})")
