"""
tao2tex.py
by Calvin Khor

Goes through a saved HTML version of one of Tao's blogposts, and spits out a LaTeX version

A partial inverse for LaTeX2WP which can be found here:
https://lucatrevisan.wordpress.com/latex-to-wordpress/using-latex2wp/
At the moment, this is hard-coded to work only for Tao's blogposts.

naming conventions:
    a formatter function returns a string,
    a wrapper function calls soup_processor or child_processor somewhere
    and returns a list of strings.
"""
import argparse
import re  # https://regexkit.com/python-regex

import requests
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

TIMEOUT_IN_SECONDS = 10


def html2soup(user_html: str, strainer: SoupStrainer) -> BeautifulSoup:
    """Creates a new soup from the raw html with an optional SoupStrainer."""
    try:
        soup = BeautifulSoup(user_html, "lxml", parse_only=strainer)
    except FeatureNotFound:
        print(
            "You should install the lxml parser: pip install lxml\n Trying with default parser"
        )
        soup = BeautifulSoup(user_html, parse_only=strainer)
    return soup


def soup_maker(html_file_name: str, strainer: SoupStrainer) -> BeautifulSoup:
    """Creates a new soup from the raw html in the file with an optional SoupStrainer."""
    with open(html_file_name, "r", encoding="UTF-8") as html_doc:
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
    """Formats labelled display math"""
    # the equation number was hard-coded into the math by LaTeX2WP. So we need to remove it
    extra_eqno_matcher = re.compile(r"(?:\\displaystyle)?(.*?)(?:\\ )+\([0-9]+\)")
    if number_match := extra_eqno_matcher.match(text):
        text = number_match.group(1)
        left_delim = r"\begin{" + env_type + "}" + label_formatter(label) + "\n"
        right_delim = "\n" + r"\end{" + env_type + "}"
    return math_formatter(text, left_delim, right_delim)


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


def ol_wrapper(soup: BeautifulSoup) -> list[str]:
    """turns ol tags into enumerates"""
    return environment_wrapper("enumerate", soup)


def ul_wrapper(soup: BeautifulSoup) -> list[str]:
    """turns ul tags into itemizes"""
    return environment_wrapper("itemize", soup)


def li_wrapper(soup: BeautifulSoup, find_bullet: bool = True) -> list[str]:
    """adds an item command before continuing to process the soup"""
    bullet_option = ""
    if (
        find_bullet
        and len(soup.contents) > 0
        and (first_child := soup.contents[0])
        and isinstance(first_child, NavigableString)
    ):
        first_child = str(first_child.extract())
        bullet_matcher = re.compile(r"(?:[\(\[]?\w\w?\w?[\)\]\:.])|[\*->]")
        #  see  https://regexkit.com/python-regex,
        # matches common bullet or numberings
        # eg: "1.", "(2)", "[3]", "4)", "(v)", ">". ,"*", and "."
        # Doesn't match 1, because it will then match e.g "Therefore,".
        # only matches ≤3 chars in label to avoid (Diffusion)
        # Doesn't match Eg. 1, Eg. 2, Eg. 3.

        if bullet_match := bullet_matcher.match(first_child):
            bullet_option = "[" + bullet_match.group() + "]"
            first_child = bullet_matcher.sub("", first_child, count=1)

        return [r"\item" + bullet_option, first_child] + soup_processor(soup)
    # fallback
    print(f"using fallback in li_wrapper for {soup=}")
    return [r"\item"] + soup_processor(soup)


def child_processor(child: PageElement) -> list[str]:
    """The meat of this script. Turns a child element into a list of legal LaTeX strings.
    We return a list instead of a single string to enable some recursion.
    Code is arranged to attempt to split
        - detecting the required LaTeX commands (which happens here)
        - how the command should be typed (formatters and wrappers)
    """
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
            # fallback processing.
            print('fallback to basic processing in p align="..." tag')
            print(f"{child=}"[:50])
            return soup_processor(child)
    elif child.name == "img" and "alt" in child.attrs.keys():
        return [math_formatter(child["alt"])]
    elif child.name == "img":
        # TODO: save images and appropriately format. NB add graphicx package
        return [f"\n unknown image: {child=} \n"[:50]]
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
            print("unknown theorem: falling back to theorem")
            print(f"{child=}"[:50])
            unprocessed_thm_name = "theorem"
        return theorem_wrapper(unprocessed_thm_name, child)
    elif child.name == "p":
        return soup_processor(child)
    elif child.name == "ul":
        return ul_wrapper(child)
    elif child.name == "ol":
        return ol_wrapper(child)
    elif child.name == "li":
        return li_wrapper(child)
    elif (
        child.name == "div"
        and ("class" in child.attrs.keys() and child.attrs["class"][0] == "sharedaddy")
        or ("id" in child.attrs.keys() and child.attrs["id"][0] == "jp-post-flair")
    ):
        return []
    else:
        # fallback to get_text
        print("unknown tag:")
        print(f"{child=}"[:50])
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


def url2tex(url: str, local: bool, output):
    "opens a url (or file) and creates a tex file with name given by output"
    raw_html = ""
    if local:
        with open(url, "r", encoding="UTF-8") as html_doc:
            raw_html = html_doc.read()
    else:
        raw_html = requests.get(url, timeout=TIMEOUT_IN_SECONDS).text

    tao2tex_signature = (
        "Automatically generated from "
        + ahref_formatter(url)
        + r" using \texttt{tao2tex.py}."
    )

    header_strainer = SoupStrainer("div", id="header")
    header_soup = html2soup(raw_html, header_strainer)
    blog_title = header_soup.find(id="blog-title").get_text()
    blog_tagline = header_soup.find(id="tagline").get_text()

    primary_strainer = SoupStrainer("div", id="primary")
    primary_soup = html2soup(raw_html, primary_strainer)
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
    if not output:
        output = blog_title + "-" + title
    with open(output, "w", encoding="utf-8") as output_file:
        output_file.write("".join(out))


def main():
    """Goes through a HTML version of a blogpost and spits out a LaTeX version"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b", "--batch", help="batch process files", action="store_true"
    )
    parser.add_argument(
        "-l", "--local", help="treat url as a local file", action="store_true"
    )
    parser.add_argument("url", help="url of blog post to convert")
    parser.add_argument("-o", "--output", help="name of output file")
    args = parser.parse_args()

    if args.batch:
        with open(args.url, "w", encoding="utf8") as file:
            list_of_filenames = file.readlines()
            for filename, i in enumerate(list_of_filenames):
                numbered_name = None
                if args.output:
                    numbered_name = args.output + str(i)
                url2tex(filename, args.local, numbered_name)
    else:
        url2tex(args.url, args.local, args.output)

    # TODO: error handling for file opening? catch FileNotFoundError for locals
    # TODO: also parse the comments: potentially has bad tex
    # TODO: test batch processing
    # TODO: make preamble fancier
    # TODO: for speed reasons perhaps move all regexes into main
    # TODO: add more fallbacks e.g. title finding so that some sort of output is generated for other blogs
    # TODO: figure out how to state the required packages


if __name__ == "__main__":
    main()
