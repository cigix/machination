#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "rules.h"

#define TAPE_LENGTH 1024

int main(int argc, char * argv[])
{
  char * input = NULL;
  int verbose = 0;
  for (int i = 1; i < argc; ++i)
  {
    if (strcmp(argv[i], "-h") == 0
        || strcmp(argv[i], "-help") == 0
        || strcmp(argv[i], "--help") == 0)
    {
      printf("Usage: %s [OPTIONS...] <INPUT>\n"
             "\n"
             "Options:\n"
             "  -v    Print every step\n"
             "  -h, -help, --help  Print this help\n"
             "\n"
             "Execute the Turing machine with the specified input\n",
             argv[0]);
      return 0;
    }
    else if (strcmp(argv[i], "-v") == 0)
      verbose = 1;
    else
      input = argv[i];
  }

  if (input == NULL)
  {
    fprintf(stderr, "No input given. See %s -h.\n", argv[0]);
    return 1;
  }

  char * tape = calloc(TAPE_LENGTH, sizeof (char));
  tape[0] = EOT;
  tape[TAPE_LENGTH - 1] = EOT;

  ssize_t head = 1;
  strcpy(tape + head, input);
  ssize_t max_head = strlen(input);

  int direction = 0;
  int state = 0;

  do
  {
    if (verbose)
    {
      printf("Tape: ");
      for (ssize_t i = 0; i <= max_head; ++i)
      {
        if (tape[i] == NUL)
          printf(" ");
        else if (tape[i] == EOT)
          printf("#");
        else
          printf("%c", tape[i]);
      }
      printf("\n"
             "Head: ");
      for (ssize_t i = 0; i < head; ++i)
        printf(" ");
      printf("^\n"
             "State: %d\n", state);
    }
    size_t i = 0;
    for (; i < RULES_SIZE; ++i)
    {
      if (rules[i].state == state && rules[i].read == tape[head])
        break;
    }
    if (i == RULES_SIZE)
    {
      fprintf(stderr, "No matching rule for state %d and symbol %c (%#hhx)\n",
              state, tape[head], tape[head]);
      free(tape);
      return 1;
    }

    struct rule rule = rules[i];

    if (verbose)
    {
      printf("Applying rule %zu: (%d, ", i, rule.state);
      if (rule.read == NUL)
        printf("NUL");
      else if (rule.read == EOT)
        printf("EOT");
      else
        printf("%c", rule.read);
      printf(") -> (");
      if (rule.write == NUL)
        printf("NUL");
      else if (rule.write == EOT)
        printf("EOT");
      else
        printf("%c", rule.write);
      printf(", %d, %d)\n", rule.dir, rule.destination);
    }

    tape[head] = rule.write;
    direction = rule.dir;
    state = rule.destination;

    head += direction;
    if (head < 0 && direction != FINAL)
    {
      fprintf(stderr,
              "Head got past the left end of the tape\n"
              "State: %d\n",
              rule.state);
      free(tape);
      return 1;
    }
    if (TAPE_LENGTH <= head && direction != FINAL)
    {
      fprintf(stderr,
          "Head got past the right end of the tape (increase TAPE_LENGTH?)\n"
          "State: %d\n",
          rule.state);
      free(tape);
      return 1;
    }
    if (max_head < head)
      max_head = head;
  }
  while (direction != FINAL);

  if (verbose)
    printf("Output: ");
  printf("%s\n", tape + 1);
  free(tape);
  return 0;
}
