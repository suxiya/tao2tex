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
    url_matcher = re.compile(r"(http|www).*")  # http or www, followed by anything
    ref_matcher = re.compile(r"[0-9]+")  # at least one number
    eqref_matcher = re.compile(r"\([0-9]+\)")  # at least one number in round brackets
    if url_matcher.match(href):
        if text == "":
            text = href
        return r"\href{" + href + "}{" + text + "}"
    elif href[0] == "#" and ref_matcher.match(text):
        return r"\ref{" + href[1:] + "}"
    elif href[0] == "#" and eqref_matcher.match(text):
        return r"\eqref{" + href[1:] + "}"
    else:
        return href


def em_wrapper(soup: BeautifulSoup) -> list[str]:
    """formats a soup inside an <em> tag with the emph LaTeX macro."""
    return [r"\emph{"] + soup_processor(soup) + ["}"]


def math_formatter(text: str, left_delim: str = r"\(", right_delim: str = r"\)") -> str:
    """adds math delimiters, hopefully around LaTeX formatted math text"""
    return left_delim + text + right_delim


def display_math_formatter(
    text: str, left_delim: str = r"\[", right_delim: str = r"\]"
) -> str:
    """adds display math delimiters"""
    return math_formatter(text, left_delim, right_delim)


def labelled_display_math_formatter(
    text: str, label: str, env_type: str = "align"
) -> str:
    # the equation number was hard-coded into the math by LaTeX2WP. So we need to remove it
    extra_eqno_matcher = re.compile(r"(?:\\displaystyle)?(.*?)(?:\\ )+\([0-9]+\)")
    if number_match := extra_eqno_matcher.match(text):
        text = number_match.group(1)
    return (
        r"\begin{"
        + env_type
        + "}"
        + label_formatter(label)
        + "\n"
        + text
        + "\n"
        + r"\end{"
        + env_type
        + "}"
    )


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
    """formats a blockquote into a theorem/conjecture/etc environment"""
    theoremtype = "unknown"
    title_matcher = re.compile(r"([a-zA-z]*) ")  # first word in unprocessed_thm_title
    if title_match := re.search(title_matcher, unprocessed_thm_title):
        match title := title_match.group(1).lower():
            case (
                "exercise"
                | "theorem"
                | "corollary"
                | "example"
                | "remark"
                | "conjecture"
                | "proposition"
                | "lemma"
                | "definition"
                | "note"
            ):
                theoremtype = title

    options = ""
    options_matcher = re.compile(
        r"\((.*)?\)"
    )  # look for a pair of brackets in unprocessed_thm_title
    if options_match := re.search(options_matcher, unprocessed_thm_title):
        options = "[" + options_match.group(1) + "]"
    return environment_wrapper(theoremtype, soup, options)


def label_formatter(tag: str) -> str:
    "formats a label as a LaTeX command"
    return r"\label{" + tag + "}"


def string_formatter(text: str) -> str:
    """Escapes special LaTeX characters."""
    latex_escaper = re.compile(r"[\\_^%&*{}@]")
    latex_subst = "\\\0"
    text = re.sub(latex_escaper, latex_subst, text)
    # pipes need special escaping
    pipe_escaper = re.compile(r"\|")
    pipe_subst = r"\\textbar"
    text = re.sub(pipe_escaper, pipe_subst, text)
    return text


def child_processor(child: PageElement) -> list[str]:
    """Turns a child element into a list of legal LaTeX strings.
    We return a list instead of a single string to enable recursion."""
    if isinstance(child, NavigableString):
        return [string_formatter(child.get_text())]
    elif child.name == "em":
        return em_wrapper(child)
    elif child.name == "p" and "align" in child.attrs.keys():
        if child.contents[0].name == "img" and "alt" in child.contents[0].attrs.keys():
            return [display_math_formatter(child.contents[0]["alt"])]
        if child.contents[0].name == "a" and child.contents[1].name == "img":
            # this may break if the case handling <a name="..."> below is changed.
            # specifically, we place the <a name="..."> at the beginning of the p tag.
            return [
                labelled_display_math_formatter(
                    child.contents[1]["alt"], child.contents[0]["name"]
                )
            ]

        elif child.contents[0].name == "b":
            return [section_formatter(child.contents[0].get_text())]
        else:
            return soup_processor(child)
    elif child.name == "img" and "alt" in child.attrs.keys():
        return [math_formatter(child["alt"])]
    elif child.name == "img":
        # TODO: save images and appropriately format
        return ["\n unknown image found \n"]
    elif child.name == "a" and "href" in child.attrs.keys():
        return [ahref_formatter(child["href"], child.get_text())]
    elif (
        child.name == "a" and "name" in child.attrs.keys() and len(child.contents) == 0
    ):
        # In LaTeX, labels need to appear inside of the environment it labels.
        # We move this into the heuristically determined correct environment and defer processing
        # this until processing <p align="..."> tags.
        # if this ever breaks, good luck whoever wants to debug this in the future...
        if (
            (parent := child.parent)
            and parent.name == "p"
            and "align" not in parent.attrs.keys()
            and parent.contents[-1] == child
            and (second_uncle := parent.next_sibling.next_sibling)
            and second_uncle.name == "p"
            and "align" in second_uncle.attrs.keys()
        ):
            # make second_uncle adopt child
            second_uncle.insert(0, child)
            return []
        # fallback
        return [label_formatter(child.attrs["name"])]
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
        return soup_processor(child)
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
    """A simple loop on child_processor that converts a BeautifulSoup
    into a list of legal LaTeX strings."""
    out = []
    for child in soup.children:
        out.extend(child_processor(child))

    return out


def preamble_formatter(template_filename: str, author: str, title: str) -> str:
    """spit out a preamble as a long string, using the template"""

    # if you don't escape the slahes, the regex will not work
    slash_escaper = re.compile(r"\\")
    author = slash_escaper.sub(r"\\\\", author)
    title = slash_escaper.sub(r"\\\\", title)

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

    preamble = preamble_formatter(
        template_filename="preamble.tex",
        author="",
        title=r"{\normalsize "
        + blog_title
        + r"\\"
        + blog_tagline
        + r"}\\"
        + title
        + r"\footnote{"
        + tao2tex_signature
        + r"}\\ \footnotesize "
        + metadata_as_string,
    )

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


if __name__ == "__main__":
    main()
