"""
tao2tex.py
by Calvin Khor

Goes through a saved HTML version of one of Tao's blogposts, and spits out a LaTeX version

A partial inverse for LaTeX2WP which can be found here:
https://lucatrevisan.wordpress.com/latex-to-wordpress/using-latex2wp/
At the moment, this is hard-coded to work only for Tao's blogposts.

naming conventions:
    a formatter function returns a string, while
    a wrapper function calls soup_processor or child_processor and returns a list of strings.
"""


import re  # https://regexkit.com/python-regex

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

DEFAULT_HTML = "test2.html"


def soup_maker(user_html: str, strainer: SoupStrainer) -> BeautifulSoup:
    """Creates a new soup from the raw html with an optional SoupStrainer."""
    with open(user_html, "r", encoding="UTF-8") as html_doc:
        try:
            soup = BeautifulSoup(html_doc.read(), "lxml", parse_only=strainer)
        except FeatureNotFound:
            print(
                "You should install the lxml parser: pip install lxml\n Trying with default parser"
            )
            soup = BeautifulSoup(html_doc.read(), parse_only=strainer)
        return soup


def ahref_formatter(href: str, text: str = "") -> str:
    """turns a href with a text into the corresponding LaTeX code.
    If no text is given, then the href is used instead."""
    url_matcher = re.compile(r"http.*")
    ref_matcher = re.compile(r"[0-9]+")
    eqref_matcher = re.compile(r"\([0-9]+\)")
    if url_matcher.match(href):
        if text == "":
            text = href
        return r"\href{" + href + r"}{" + text + "}"
    elif href[0] == "#" and ref_matcher.match(text):
        return r"\ref{" + href[1:] + "}"
    elif href[0] == "#" and eqref_matcher.match(text):
        return r"\eqref{" + href[1:] + "}"
    else:
        return href


def em_wrapper(soup: BeautifulSoup) -> list[str]:
    """formats a string inside an <em> tag with the emph LaTeX macro."""
    return [r"\emph{"] + soup_processor(soup) + ["}"]


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
    return left_delim + math_formatter(text) + right_delim


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
    section_matcher = re.compile(r"[a-zA-Z,]+")
    if section_match := section_matcher.findall(text):
        text = " ".join(section_match)
    return r"\section{" + text + "}"


def author_formatter(text: str) -> str:
    """formats an author"""
    return r"\author{" + text + "}"


def title_formatter(text: str) -> str:
    """formats a title"""
    return r"\title{" + text + "}"


def environment_wrapper(
    env_type: str, soup: BeautifulSoup, options: str = ""
) -> list[str]:
    """processes and wraps a soup in an environment"""
    return (
        [r"\begin{" + env_type + "}" + options + "\n"]
        + soup_processor(soup)
        + ["\n", r"\end{" + env_type + "}"]
    )


def theorem_wrapper(unprocessed_thm_title: str, soup: BeautifulSoup) -> list[str]:
    """formats a blockquote into a theorem/conjecture/etc."""
    theoremtype = "unknown"
    title_matcher = re.compile(r"([a-zA-z]*) ")  # first word in unprocessed_thm_title
    if title_match := re.search(title_matcher, unprocessed_thm_title):
        match title := title_match.group(1).lower():
            case "exercise" | "theorem" | "corollary" | "example" | "remark" | "conjecture" | "proposition" | "lemma" | "definition" | "note":
                theoremtype = title

    options = ""
    options_matcher = re.compile(
        r"\((.*)?\)"
    )  # first pair of brackets in unprocessed_thm_title
    if options_match := re.search(options_matcher, unprocessed_thm_title):
        options = "[" + options_match.group(1) + "]"
    return environment_wrapper(theoremtype, soup, options)


def tag_formatter(tag: str) -> str:
    "formats a tag as a label"
    return r"\label{" + tag + "}"


def child_processor(child: PageElement) -> list[str]:
    """Turns a child element into a list of legal LaTeX strings."""
    if isinstance(child, NavigableString):
        # TODO: check for and escape special chars here
        return [child.get_text()]
    elif child.name == "em":
        return em_wrapper(child)
    elif (
        child.name == "p" and "align" in child.attrs.keys() and len(child.contents) == 1
    ):
        if child.contents[0].name == "img" and "alt" in child.contents[0].attrs.keys():
            return [display_math_formatter(child.contents[0]["alt"])]
        elif child.contents[0].name == "b":
            return [section_formatter(child.contents[0].get_text())]
        else:
            return soup_processor(child)
    elif child.name == "img" and "alt" in child.attrs.keys():
        return [inline_math_formatter(child["alt"])]
    elif child.name == "img":
        # TODO: save images and appropriately format
        return ["\n unknown image found \n"]
    elif child.name == "a" and "href" in child.attrs.keys():
        return [ahref_formatter(child["href"], child.get_text())]
    elif (
        child.name == "a" and "name" in child.attrs.keys() and len(child.contents) == 0
    ):
        return [tag_formatter(child.attrs["name"])]
    elif child.name == "blockquote":
        if child.b:
            unprocessed_thm_name = (
                child.b.extract().get_text()
            )  # NB extract() removes the tag so that it is not processed twice.
        elif child.p and child.p.b:
            unprocessed_thm_name = (
                child.p.b.extract().get_text()
            )  # NB extract() removes the tag so that it is not processed twice.
        else:
            unprocessed_thm_name = "unknown"
        return theorem_wrapper(unprocessed_thm_name, child)
    elif child.name == "p":
        return soup_processor(child) + ["\n"]
    elif (
        child.name == "div"
        and ("class" in child.attrs.keys() and child.attrs["class"][0] == "sharedaddy")
        or ("id" in child.attrs.keys() and child.attrs["id"][0] == "jp-post-flair")
    ):
        return []
    else:
        # TODO: ordered and unordered lists?
        return [child.get_text()]


def soup_processor(soup: BeautifulSoup) -> list[str]:
    """converts a BeautifulSoup into a list of legal LaTeX strings"""
    out = []
    for child in soup.children:
        out.extend(child_processor(child))

    return out


def preamble_processor(template_filename: str, author: str, title: str) -> str:
    """spit out a preamble using the template
    CAUTION, something about this is making raw strings act weirdly,
    so that I still need double backslashes"""
    with open(template_filename, "r", encoding="UTF-8") as template:
        out = template.read()
        author_matcher = re.compile(r"TTT-AUTHOR")
        out = author_matcher.sub(author, out)
        title_matcher = re.compile(r"TTT-TITLE")
        out = title_matcher.sub(title, out)
        return out


def main():
    """Goes through a saved HTML version of a blogpost and spits out a LaTeX version"""

    tao2tex_signature = (
        r"Automatically generated using \texttt{tao2tex.py} from "
        + ahref_formatter(DEFAULT_HTML)
        + "."
    )

    header_strainer = SoupStrainer("div", id="header")
    header_soup = soup_maker(DEFAULT_HTML, header_strainer)
    blog_title = header_soup.find(id="blog-title").get_text()
    blog_tagline = header_soup.find(id="tagline").get_text()

    primary_strainer = SoupStrainer("div", id="primary")
    primary_soup = soup_maker(DEFAULT_HTML, primary_strainer)
    title = primary_soup.h1.get_text()
    metadata = soup_processor(primary_soup.find("p", "post-metadata"))
    metadata_as_string = "".join(metadata)

    slash_escaper = re.compile(r"\\")
    metadata_as_string = slash_escaper.sub(r"\\\\", metadata_as_string)
    tao2tex_signature = slash_escaper.sub(r"\\\\", tao2tex_signature)

    preamble = preamble_processor(
        template_filename="preamble.tex",
        author="",
        title=r"{\\normalsize "
        + blog_title
        + r"\\\\"
        + blog_tagline
        + r"}\\\\"
        + title
        + r"\\footnote{"
        + tao2tex_signature
        + r"}\\\\ \\footnotesize "
        + metadata_as_string,
    )
    # print(blog_title, blog_tagline)
    # print(title)

    content = primary_soup.find(attrs={"class": "post-content"})

    out = (
        [preamble, r"\begin{document}", r"\maketitle"]
        + soup_processor(content)
        + [r"\end{document}"]
    )

    with open("out.tex", "w", encoding="utf-8") as output_file:
        output_file.write("".join(out))

    # TODO: also parse the comments: potentially has bad tex
    # TODO: what about "" into ``''? then '' into `'? and {\bf} into \mathbf{}?
    # TODO: convert &nbsp; to '~' (which is precisely a nonbreaking space in LaTeX)
    # TODO: allow user to fetch from the internet
    # TODO: fix labels for displaystyle maths


if __name__ == "__main__":
    main()
