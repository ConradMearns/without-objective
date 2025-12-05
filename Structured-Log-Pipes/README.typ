#set document(title: "Structured Log Pipes", author: "Conrad")
#set page(numbering: "1")
#set text(font: "Linux Libertine", size: 11pt)

#align(center)[
  #block(text(weight: 700, 1.5em)[Structured Log Pipes])
]

#v(1em)

= AI Use Preface

I care more about sharing the idea than being a perfect writer - so parts of this article are AI generated.

Claude helped me write the introductory text here.
I wrapped what Claude wrote in `<claude>` and `</claude>` tags for honest provenance.
I may edit the text Claude produces - but will keep the tags.
Everything outside of the tags is my own.

#v(1em)

= The UNIX Philosophy

#quote(block: true)[
  This is the Unix philosophy: \
  Write programs that do one thing and do it well. \
  Write programs to work together. \
  Write programs to handle text streams, because that is a universal interface.

  #align(right)[— Doug McIlroy (2003). _The Art of Unix Programming: Basics of the Unix Philosophy_]
]

`<claude Read @README.md - help me expand on these ideas. What is the main benefit and reasoning behind the UNIX philosophy of writing small single purpose scripts? Where does this fall apart? and why isn't it a good solution / used more broadly? Does this new approach help to solve any of these problems?>`

The UNIX philosophy's main benefits:
- *Composability*: Small tools can be combined in unexpected ways
- *Simplicity*: Each program has a single, clear purpose
- *Reusability*: Tools can be reused across different contexts
- *Debuggability*: Easy to test individual components
- *Flexibility*: Combine tools without rewriting them

= Where UNIX Pipes Fall Apart

Despite their elegance, UNIX pipes have fundamental limitations that prevent broader adoption:

== 1. Unstructured Text is Brittle
- Parsing text output (awk, sed, cut) is fragile and error-prone
- No schemas or types—breaking changes are silent
- Whitespace, quotes, and special characters cause endless edge cases

== 2. Limited Flow Control
- Linear pipelines only—no branching, fan-out, or fan-in
- Can't easily send output to multiple consumers
- No built-in support for conditional routing

== 3. Poor Error Handling
- Exit codes are the only signal (0 or non-zero)
- Error messages go to stderr (unstructured text again)
- Hard to propagate context about what failed and why

== 4. No State Management
- Each process is isolated—can't share state without external tools
- No reactivity—can't respond to events or build feedback loops
- Difficult to build stateful, long-running processes

== 5. Limited Observability
- Hard to debug multi-stage pipelines
- No structured logging by default
- Can't easily trace data flow through the system

This is why UNIX pipes work great for simple scripts but struggle in 'enterprise' software where you need:
- Reactive, event-driven systems
- Complex branching logic
- Structured logging and observability
- Type safety and validation
- Scalable, long-running processes

= The Solution: Structured Log Pipes

What if we kept the UNIX philosophy of composability but fixed the interface?

*Key insight*: Replace unstructured text with JSONL (JSON Lines)

== Benefits Over Traditional UNIX Pipes

+ *Structured Data*: Type-safe events with schemas (via dataclasses)
+ *Maintains Composability*: Still uses stdin/stdout—works with existing UNIX tools
+ *Better Debugging*: JSON is human-readable and machine-parseable
+ *Foundation for Reactivity*: Structured events enable event-driven patterns
+ *Language Agnostic*: Any language can emit/consume JSONL
+ *Incremental Adoption*: Works alongside existing text-based tools

`</claude>`

== Current Features

- JSONL stdout for structured event emission
- Type-safe event parsing (Python dataclasses)
- Composable via UNIX pipes

= Piping structured data in and out of `fibwait.py`

I made `fibwait.py` to illustrate the concept - roughed out but works.

```bash
without-objective/Structured-Log-Pipes$ ./fibwait.py
# {"a": 1, "b": 2}
without-objective/Structured-Log-Pipes$ ./fibwait.py | ./fibwait.py
# {"a": 2, "b": 3}
without-objective/Structured-Log-Pipes$ ./fibwait.py | ./fibwait.py | ./fibwait.py
# {"a": 3, "b": 5}
without-objective/Structured-Log-Pipes$
```

The main idea here would be to do all sorts of complex Side-Effect driving work, and then wrap that work in Structured Logging _as we should anyway_.
Then, this can be used to control scripts down the line - or simply produce a log of work completed.

== Problems with

#block(fill: rgb("#f0f0f0"), inset: 10pt, radius: 4pt)[
  *P*: JSONL does look ugly though, it would be nice to have a Logging Format that is slightly more human readable that works for this.
]

`logfmt` is _an_ alternative - I wont say better but it does at least have good support and colored formatting.

#block(fill: rgb("#f0f0f0"), inset: 10pt, radius: 4pt)[
  *P*: The stdin parsing system inside fibwait sucks though, we can't really expect people to write this themselves.
]

#block(fill: rgb("#f0f0f0"), inset: 10pt, radius: 4pt)[
  *P*: fibwait is a bad example.
]

#block(fill: rgb("#f0f0f0"), inset: 10pt, radius: 4pt)[
  *P*: Since I'm introducing libraries in scripts - are we just going to expect users to make a venv compatible with new libraries I need??
]

== New Requirements

#block(fill: rgb("#e0f0ff"), inset: 10pt, radius: 4pt)[
  *N*: Need at a utility file to capture the complexities we are introducing to make this easy to use - otherwise it's too much effort
]

#block(fill: rgb("#e0f0ff"), inset: 10pt, radius: 4pt)[
  *N*: Let's make a simple Content Addressable Storage example instead of fibwait
]

= A Better Example - Simple Content Addressable Storage ETL

== Effectual Scripting: Partition Scanning

#link("https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies")

```bash
chmod +x scan_partition.py
uv add --script scan_partition.py pandas
```

```python
#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "pandas",
# ]
# ///
```

*Progress*:
- [x] ls
- [ ] stat
- [ ] hash
- [ ] 'upload'

#v(2em)
#line(length: 100%)

== References

- #link("https://pages.cs.wisc.edu/~remzi/Naur.pdf")[Naur.pdf]
- #link("https://www.arthropod.software/p/vibe-coding-our-way-to-disaster")[Vibe Coding Our Way to Disaster]
