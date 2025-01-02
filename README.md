# ReDFA

Experimenting with parsing regex and deterministic finite automata.

Currently, only a small subset of PCRE (Perl Compatible Regular Expressions) is supported:

| Syntax | Example | Remarks |
| ------ | ------- | ------- |
| Simple characters | "abc", "1a2b3c" | Characters that are explicitly typed out are supported. Ranges like "[A-z]" are not. |
| Brackets | "(123)" | Wrap a bracket around an expression. This allows you to create unnamed groups too. |
| Pipes | "(ab\|cd)" | The final DFA can choose to parse "ab" or "cd". |
| Kleene Symbols | "a*", "(ab)+", "(ab\|cd)?" | Stars, plusses and question marks. |
| Escaped Characters | "\\(" | Use a backslash to escape special characters. |