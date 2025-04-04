# This Markdown File is a Graph

I'm writing this blog post while thinking about the problem. Effectively trying to produce a chicken and egg simultaneously.

The forcing factor behind this is the itch of procrastination that takes away the will to do _real_ work - but this seemed like a good way to spend a small amount of time while getting into flow I can use for work as well.

Firstly - context. I've been an Obsidian user since it's first release. I was an early adopter of Roam back then too - but all of these solutions have other smaller issues that keep nagging at me.
The result is that I'm _still_ thinking of building my own tool. One major issue is that accessing pieces of text within existing documents is cumbersome / weird / or unaccessible. Obsidian can use a `^` to insert direct links anywhere, but I'm not a fan of the markup.

I like heading links more - for example `[[2025-04-04-This-Markdown-is-a-Graph#This Markdown File is a Graph]]`.

Another issue is that I really just want to play with potential nonlinear writing systems - the Obsidian Canvas is a good tool for this, but still not quite what I want / need. It's a little too cumbersome to drag and drop / resize / move / and color blocks of text around. The storage format is JSON, which is good and bad. I won't elaborate here though.



# Building Blocks

A graph can be represented in many ways - we will consider $G = (V, E)$ where $V$ is a set of all Vertices and $E$ is a set of all edges connecting each vertex. 
$E$ is a set of tuples that point to vertices.
I may also refer to vertices as nodes.

Within the Obsidian graph, nodes are documents and edges are constructed via parsing documents to uncover the wikilinks inside them.
What I crave is something more descriptive, so that semantic relationships can be built between concepts. So for this graph, $E$ with actually refer to 2 nodes with an order (so that edges are directional) and a label.

The objective is to make a different kind of link for standalone markdown files to be represented as graphs - so here's some options:

```
# Building Blocks >> is after >> # This Markdown File is a Graph

Building Blocks >> is after >> This Markdown File is a Graph

A longer sentence, not a link to a heading or anything. This could be imagined as a footnote or a comment or an annotation perhaps.
>> annotates >> # Building Blocks
```

`>>` Wont work because it'll be confused for a blockquote. Maybe `::` is better. Directionality can be represented by ordering.

```
A longer sentence, not a link to a heading or anything. This could be imagined as a footnote or a comment or an annotation perhaps.
:: annotates :: # Building Blocks
```

I'm also partial to using wikilink notation as a way to 'highlight' sentences and turn them into links for Obsidian. It's a decent option for specifying links as well.

[[They would look like this.|Alias to the wikilink example]]

```
Specifying links could be done with the alias like this:
[[|Alias to the wikilink example]]
:: example for :: In-document linking
```

Another option would be to utilize the structure of the document to refer to specific sections.
This can be tricky though, because it's hard for an author without a parser to know what paragraph ordinal a certain text item falls in.

What about using ellipses for long sentences?

What if the bracket notation reflected the the block itself?

Honestly - the best solution for text matching is probably to use `?` as a query tool.
The only thing I think may pose as a challenge is that queries that match multiple items may be common. 

```
[[Another option...]]
[[# Building Blocks]][[Another option...]]
[[this_file.md]][[# Building Blocks]][[Another option...]]
[[this_file.md# Building Blocks?Another option...]]
[[?Another option...]]

[[?Another option...]]::has annotation::I kinda like this, it's good enough for now!
```

# Playing with the Markdown

```bash
python -m venv .venv
pip install marko matplotlib networkx
python net.py
```

