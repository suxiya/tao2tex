"""
tao2tex.py
by Calvin Khor

Goes through a saved HTML version of one of Tao's blogposts, and spits out a LaTeX version

A partial inverse for LaTeX2WP which can be found here: https://lucatrevisan.wordpress.com/latex-to-wordpress/using-latex2wp/
At the moment, this is hard-coded to work only for Tao's blogposts.
"""


from bs4 import (
    BeautifulSoup,
    FeatureNotFound,
    NavigableString,
    PageElement,
    SoupStrainer,
)

# url = "https://terrytao.wordpress.com/"
# url = "https://www.baidu.cn/"
# r = requests.get(url)
# print(r.text)
# soup = BeautifulSoup(response)

# demo_html = """<div class="post-content">


# <p>
#  <a href="https://www.ias.edu/scholars/rachel-greenfeld">Rachel Greenfeld</a> and I have just uploaded to the arXiv our paper “<a href="https://arxiv.org/abs/2211.15847">A counterexample to the periodic tiling conjecture</a>“. This is the full version of the result I announced on this blog <a href="https://terrytao.wordpress.com/2022/09/19/a-counterexample-to-the-periodic-tiling-conjecture/">a few months ago</a>, in which we disprove the <em>periodic tiling conjecture</em> of <a href="https://mathscinet.ams.org/mathscinet-getitem?mr=857454">Grünbaum-Shephard</a> and <a href="https://mathscinet.ams.org/mathscinet-getitem?mr=1369421">Lagarias-Wang</a>. The paper took a little longer than expected to finish, due to a technical issue that we did not realize at the time of the announcement that required a workaround.
# </p><p>
# In more detail: the original strategy, as described in the announcement, was to build a “tiling language” that was capable of encoding a certain “<img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex.php" srcset="https://s0.wp.com/latex.php?latex=%7Bp%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7Bp%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{p}" class="latex">-adic Sudoku puzzle”, and then show that the latter type of puzzle had only non-periodic solutions if <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex.php" srcset="https://s0.wp.com/latex.php?latex=%7Bp%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7Bp%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{p}" class="latex"> was a sufficiently large prime. As it turns out, the second half of this strategy worked out, but there was an issue in the first part: our tiling language was able (using <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex(1).php" srcset="https://s0.wp.com/latex.php?latex=%7B2%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7B2%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{2}" class="latex">-group-valued functions) to encode arbitrary boolean relationships between boolean functions, and was also able (using <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex(2).php" srcset="https://s0.wp.com/latex.php?latex=%7B%7B%5Cbf+Z%7D%2Fp%7B%5Cbf+Z%7D%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7B%7B%5Cbf+Z%7D%2Fp%7B%5Cbf+Z%7D%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{{\bf Z}/p{\bf Z}}" class="latex">-valued functions) to encode “clock” functions such as <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex(3).php" srcset="https://s0.wp.com/latex.php?latex=%7Bn+%5Cmapsto+n+%5Chbox%7B+mod+%7D+p%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7Bn+%5Cmapsto+n+%5Chbox%7B+mod+%7D+p%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{n \mapsto n \hbox{ mod } p}" class="latex"> that were part of our <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex.php" srcset="https://s0.wp.com/latex.php?latex=%7Bp%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7Bp%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{p}" class="latex">-adic Sudoku puzzle, but we were not able to make these two types of functions “talk” to each other in the way that was needed to encode the <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex.php" srcset="https://s0.wp.com/latex.php?latex=%7Bp%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7Bp%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{p}" class="latex">-adic Sudoku puzzle (the basic problem being that if <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex(4).php" srcset="https://s0.wp.com/latex.php?latex=%7BH%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7BH%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{H}" class="latex"> is a finite abelian <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex(1).php" srcset="https://s0.wp.com/latex.php?latex=%7B2%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7B2%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{2}" class="latex">-group then there are no non-trivial subgroups of <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex(5).php" srcset="https://s0.wp.com/latex.php?latex=%7BH+%5Ctimes+%7B%5Cbf+Z%7D%2Fp%7B%5Cbf+Z%7D%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7BH+%5Ctimes+%7B%5Cbf+Z%7D%2Fp%7B%5Cbf+Z%7D%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{H \times {\bf Z}/p{\bf Z}}" class="latex"> that are not contained in <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex(4).php" srcset="https://s0.wp.com/latex.php?latex=%7BH%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7BH%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{H}" class="latex"> or trivial in the <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex(2).php" srcset="https://s0.wp.com/latex.php?latex=%7B%7B%5Cbf+Z%7D%2Fp%7B%5Cbf+Z%7D%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7B%7B%5Cbf+Z%7D%2Fp%7B%5Cbf+Z%7D%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{{\bf Z}/p{\bf Z}}" class="latex"> direction). As a consequence, we had to replace our “<img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex.php" srcset="https://s0.wp.com/latex.php?latex=%7Bp%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7Bp%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{p}" class="latex">-adic Sudoku puzzle” by a “<img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex(1).php" srcset="https://s0.wp.com/latex.php?latex=%7B2%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7B2%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{2}" class="latex">-adic Sudoku puzzle” which basically amounts to replacing the prime <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex.php" srcset="https://s0.wp.com/latex.php?latex=%7Bp%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7Bp%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{p}" class="latex"> by a sufficiently large power of <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex(1).php" srcset="https://s0.wp.com/latex.php?latex=%7B2%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7B2%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{2}" class="latex"> (we believe <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex(6).php" srcset="https://s0.wp.com/latex.php?latex=%7B2%5E%7B10%7D%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7B2%5E%7B10%7D%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{2^{10}}" class="latex"> will suffice). This solved the encoding issue, but the analysis of the <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex(1).php" srcset="https://s0.wp.com/latex.php?latex=%7B2%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7B2%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{2}" class="latex">-adic Sudoku puzzles was a little bit more complicated than the <img src="./A counterexample to the periodic tiling conjecture _ What&#39;s new_files/latex.php" srcset="https://s0.wp.com/latex.php?latex=%7Bp%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002 1x, https://s0.wp.com/latex.php?latex=%7Bp%7D&amp;bg=ffffff&amp;fg=000000&amp;s=0&amp;c=20201002&amp;zoom=4.5 4x" alt="{p}" class="latex">-adic case, for the following reason. The following is a nice exercise in analysis:
# </p>"""

default_html = "test1.html"


def soup_maker(user_html: str, strainer: SoupStrainer) -> BeautifulSoup:
    """Creates a new soup from the raw html with an optional SoupStrainer."""
    with open(user_html, "r", encoding="UTF-8") as html_doc:
        try:
            soup = BeautifulSoup(html_doc.read(), "lxml", parse_only=strainer)
        except FeatureNotFound:
            print(
                "You should install the lxml parser: pip install lxml. Trying with default parser"
            )
            soup = BeautifulSoup(html_doc.read(), parse_only=strainer)
        return soup


# def preamble(author: str, title: str, date: str) -> str:
#     """converts the local template file into a preamble expressed as a string"""
#     return ""


def url_formatter(url: str, text: str = "") -> str:
    """turns a url with a text into the corresponding LaTeX code.
    If no text is given, then the url is used instead."""
    if text == "":
        text = url
    return r"\href{" + url + r"}{" + text + "}"


def em_formatter(text: str) -> str:
    """formats a string inside an <em> tag with the emph LaTeX macro.
    This code ASSUMES that an <em> tag contains only a simple string, with no other tags."""
    return r"\emph{" + text + "}"


def math_formatter(text: str) -> str:
    """turns the given img tag that was already checked to encode math, into LaTeX code"""
    return text


def display_math_formatter(text: str, dollar: str = "") -> str:
    """adds display math delimitters around math_formatter"""
    if dollar:
        left_delim = "$$"
        right_delim = "$$"
    else:
        left_delim = r"\["
        right_delim = r"\]"
    return left_delim + math_formatter(text) + right_delim + r"\n"


def inline_math_formatter(text: str, dollar: str = "") -> str:
    """adds inline math delimitters around math_formatter"""
    if dollar:
        left_delim = "$"
        right_delim = "$"
    else:
        left_delim = r"\("
        right_delim = r"\)"
    return left_delim + math_formatter(text) + right_delim


def section_formatter(text: str) -> str:
    """formats a section header using the section LaTeX macro"""
    # TODO: use regex to remove the fancy formatting and number
    # TODO: check if there are tags in test2.html
    return r"\section{" + text + "}"


def theorem_formatter(soup: BeautifulSoup) -> str:
    """formats a blockquote into a theorem/conjecture/etc."""
    # TODO: use regex to figure out the theorem type.
    return r"XXXXXXXX THEOREM XXXXXXXX\n" + "".join(soup_processor(soup))


def child_processor(child: PageElement) -> list[str]:
    """Turns a child element into a list of legal LaTeX strings."""
    if isinstance(child, NavigableString):
        return [child.get_text()]
    elif child.name == "em":
        return [em_formatter(child.get_text())]
    elif (
        child.name == "p" and "align" in child.attrs.keys() and len(child.contents) == 1
    ):
        if child.contents[0].name == "img" and "alt" in child.attrs.keys():
            return [display_math_formatter(child.contents[0]["alt"])]
        elif child.contents[0].name == "b":
            return [section_formatter(child.contents[0].get_text())]
        else:
            return ["TODO", child.get_text()]
    elif child.name == "img" and "alt" in child.attrs.keys():
        return [inline_math_formatter(child["alt"])]
    elif child.name == "img":
        # TODO: save images and appropriately format
        return ["\n unknown image found \n"]
    elif child.name == "a" and "href" in child.attrs.keys():
        # TODO: turn things like <a href="#approx">(19)</a> into labels
        return [url_formatter(child["href"], child.get_text())]
    elif child.name == "a" and "name" in child.attrs.keys():
        # TODO: save the name as a tag
        return ["TODO", child.get_text()]
    elif child.name == "blockquote":
        # TODO: Theorem detect with regex and implement
        return ["TODO", child.get_text()]
    elif child.name == "p":
        return [*soup_processor(child), "\n"]
    else:
        return [child.get_text()]


def soup_processor(soup: BeautifulSoup) -> list[str]:
    """converts a BeautifulSoup into a list of legal LaTeX strings"""
    out = []
    for child in soup.children:
        out.extend(child_processor(child))

    return out


def main():
    """Goes through a saved HTML version of a blogpost and spits out a LaTeX version"""
    strainer = SoupStrainer("div", id="primary")
    soup = soup_maker(default_html, strainer)

    title = soup.h1.get_text()
    metadata = soup_processor(soup.find("p", "post-metadata"))

    print(title)
    print("".join(metadata))
    # print(soup.p["post-metadata"])
    content = soup.find(attrs={"class": "post-content"})
    print("".join(soup_processor(content)))
    print(r"\end{document}")

    # TODO: parse the centered theorems
    # TODO: also parse the comments: potentially has bad tex
    # TODO: longer blog posts have section headers too...
    # TODO: process the title and metadata into a preamble
    # TODO: Post-processing: Equation numbering? adding tao's banner?
    # TODO: what about "" into ``''? then '' into `'? and {\bf} into \mathbf{}?
    # TODO: convert &nbsp; to standard whitespace


if __name__ == "__main__":
    main()
