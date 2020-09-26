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

class C(OutputDriver):
    '''Format a Turing machine for use in a C program'''
    def formatrule(*_):
        raise NotImplementedError("C output driver only implements formatmt()")

    def formatmt(self, states):
        statenum = { "start": 0 }
        statenames = list(states.keys())
        statenames.remove("start")
        for i, state in enumerate(statenames):
            statenum[state] = i + 1
        def symbolchar(symbol):
            if symbol in ("NUL", "EOT"):
                return symbol
            if symbol == "'":
                return r"'\''"
            if symbol == '\\':
                return r"'\\'"
            return f"'{symbol}'"
        directions = ["FINAL", "RIGHT", "LEFT"]

        header = '''#define NUL (0)
#define EOT (0x03) // End of tape <=> End of text

#define LEFT (-1)
#define RIGHT (1)
#define FINAL (0)

// Describe one rule of the transition function
struct rule
{
  // Inputs:
  // The origin state
  int state;
  // The current symbol under the head
  char read;

  // Outputs:
  // The symbol to write
  char write;
  // The movement to apply. Should be in [-1 .. 1].
  int dir;
  // The next state
  int destination;
};

static struct rule rules[] = {
'''
        rule_count = 0;
        for state, rules in states.items():
            header += f"  /* {state} */\n"
            for rule in rules:
                header += "  { "
                header += f"{statenum[state]}, "
                header += f"{symbolchar(rule.match)}, "
                header += f"{symbolchar(rule.write)}, "
                header += f"{directions[rule.direction]}, "
                header += f"{statenum[rule.state]} "
                header += "},\n"
                rule_count += 1

        header += "};\n"
        header += "\n"
        header += f"#define RULES_SIZE ({rule_count})\n"

        with open("rules.h", 'w') as file:
            file.write(header)
        return "Successfully written transition function as rules.h"
