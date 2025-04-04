from collections import defaultdict
import re
import marko
from marko import Markdown, MarkoExtension, inline, block

# From the example: https://marko-py.readthedocs.io/en/latest/extend.html
class GitHubWiki(inline.InlineElement):

    pattern = r'\[\[ *(.+?) *\| *(.+?) *\]\]'
    parse_children = True

    def __init__(self, match):
        self.target = match.group(2)
        
        
class QueryBlock(inline.InlineElement):
    # Set the pattern to match [[? ... ]]
    pattern = r'\[\[\? *(.+?) *\.\.\.\]\]'
    parse_children = True
    
class AnnotatedBlock(inline.InlineElement):
    # Set the pattern to match group::group::group potentially multiline
    pattern = r'([^\n]+)::([^\n]+)::([^\n]+)'
    # pattern = r' *(.+?) *\:\: *(.+?) *\:\: *(.+?) *'

    priority = 6
    parse_children = True

    def __init__(self, match):
        self.matches = [match.group(1), match.group(2), match.group(3)]
        self.children = []
        
    def parse(self, parser):
        self.children.append(parser.parse_inline(self.matches[0]))

        for match in self.matches[1:]:
            self.children.append(Markdown().parse(match).children[0])



class AnnotatedBlock(block.BlockElement):
    # pattern = re.compile(r'([^\n]+)::([^\n]+)::([^\n]+)', flags=re.M)
    pattern = r'([^\n]+)::([^\n]+)::([^\n]+)'
    priority = 6

    def __init__(self, matches):
        self.children = [inline.RawText(matches.group(1))]
        self.children.append(inline.RawText(matches.group(2)))
        self.children.append(inline.RawText(matches.group(3)))

    @classmethod
    def match(cls, source: marko.source.Source):
        return source.expect_re(cls.pattern)
    
    @classmethod
    def parse(cls, source: marko.source.Source):
        m = source.match
        source.consume()
        return cls(m)




text = """
[[Linking somewhere else|With alias]]
[[?Query selector...]]
[[?Another option...]]::*has annotation*::I kinda like this, it's good enough for now!
"""

# text = "text1::text2::text3"


Extensions = MarkoExtension(
    elements=[AnnotatedBlock, GitHubWiki, QueryBlock],
    renderer_mixins=[]
)

markdown = Markdown()
markdown.use(Extensions)

# d = markdown(text)
d = markdown.parse(text)

print(d)


import marko.source
import networkx as nx
import matplotlib.pyplot as plt






G = nx.DiGraph()
label_count = defaultdict(int)

def add_nodes_edges(node, parent=None):
    node_id = id(node)
    node_label = type(node).__name__
    label_count[node_label] += 1
    unique_label = f"{node_label}({label_count[node_label]})"

    if isinstance(node, str):
        return

    G.add_node(node_id, label=unique_label)
    if parent:
        G.add_edge(id(parent), node_id)

    if hasattr(node, 'children'):
        for child in node.children:
            if isinstance(child, inline.RawText):
                child_node_id = f"{child}s{id(child)}"
                if not G.has_node(child_node_id):
                    G.add_node(child_node_id, label=str(child))
                    G.add_edge(node_id, child_node_id)
                continue
            add_nodes_edges(child, node)

add_nodes_edges(d)

for layer, nodes in enumerate(nx.topological_generations(G)):
    for node in nodes:
        G.nodes[node]["layer"] = layer

pos = nx.multipartite_layout(G, subset_key="layer")

labels = nx.get_node_attributes(G, 'label')
nx.draw(G, pos, labels=labels, with_labels=True, node_size=3000, node_color="white", font_size=10, font_color="black", font_weight="bold", arrows=True)
plt.show()
