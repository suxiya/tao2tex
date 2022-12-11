"""
tao2tex.py
by Calvin Khor

Goes through a saved HTML version of one of Tao's blogposts, and spits out a LaTeX version

A partial inverse for LaTeX2WP which can be found here:
https://lucatrevisan.wordpress.com/latex-to-wordpress/using-latex2wp/
This will work perfectly only for Tao's newer blogposts.

naming conventions: (NB if this gets more complicated, abstract into a class)
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
from requests.exceptions import ConnectTimeout

TIMEOUT_IN_SECONDS = 60


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


def add_to_download_queue(url: str):
    # TODO: figure out how to queue downloads and then download it
    return


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


def ahref_wrapper(href, soup: BeautifulSoup) -> list[str]:
    "figures out how to format hrefs"
    # TODO: this and the formatter should ideally be just one function
    soup_out = soup_processor(soup)
    return [ahref_formatter(href, "".join(soup_out))]


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
    displaystyle_matcher = re.compile(r"(?:\\displaystyle)? *(.*)")
    if displaystyle_match := displaystyle_matcher.match(text):
        text = displaystyle_match.group(1)
    return math_formatter(text, left_delim, right_delim)


def labelled_math_formatter(text: str, label: str, env_type: str = "align") -> str:
    """Formats labelled display math"""
    # the equation number was hard-coded into the math by LaTeX2WP. So we need to remove it
    extra_eqno_matcher = re.compile(r"(?:\\displaystyle)?(.*?)(?:\\ )+\([0-9]+\)")
    if number_match := extra_eqno_matcher.match(text):
        text = number_match.group(1)
        left_delim = r"\begin{" + env_type + "}" + label_formatter(label)
        right_delim = r"\end{" + env_type + "}"
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
        [r"\begin{" + env_type + "}" + options]
        + soup_processor(soup)
        + [r"\end{" + env_type + "}"]
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


def string_formatter(text: str, remove_newlines: bool = False) -> str:
    """Escapes special LaTeX characters and unusual whitespaces (sorry foreign languages)."""
    unusual_whitespace = (
        "\t\u0009\u00A0\u00AD\u034F\u061c\u115f\u1160\u17b4\u17b5\u180e"
        + "\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009"
        + "\u200A\u200B\u200C\u200D\u200E\u200F\u202F"
        + "\u205F\u2060\u2061\u2062\u2063\u2064\u206A\u206b\u206c"
        + "\u206d\u206e\u206f\u3000\u2800\u3164\ufeff\uffa0\U0001D159"
        + "\U0001D173\U0001D174\U0001D175\U0001D176\U0001D177\U0001D178\U0001D179\U0001D17A"
    )
    if remove_newlines:
        unusual_whitespace += "\n"
    unusual_whitespace_matcher = re.compile("[" + unusual_whitespace + "]+")

    text = re.sub(unusual_whitespace_matcher, " ", text)
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
        bullet_matcher = re.compile(r"(?:[\(\[]?[0-9]?\w?\w[\)\]\:.])|[\*->]")
        #  see  https://regexkit.com/python-regex,
        # matches common bullet or numberings
        # eg: "1.", "(2)", "[3]", "4)", "(v)", ">". ,"*", and "."
        # Doesn't match 1, because it will then match e.g "Therefore,".
        # only matches ≤3 chars in label to avoid e.g. (Diffusion)
        # Doesn't match Eg. 1, Eg. 2, Eg. 3.

        if bullet_match := bullet_matcher.match(first_child):
            bullet_option = "[" + bullet_match.group() + "]"
            first_child = bullet_matcher.sub("", first_child, count=1)

        return [r"\item " + bullet_option, first_child] + soup_processor(soup)
    # fallback
    print(f"using fallback in li_wrapper for {soup=}")
    return [r"\item "] + soup_processor(soup)


def child_processor(child: PageElement) -> list[str]:
    """The meat of this script. Turns a child element into a list of legal LaTeX strings.
    We return a list instead of a single string to enable some recursion.
    Unfortunately this is all just heuristics.
    Code is arranged to attempt to split
        - detecting what LaTeX commands are required (which happens here)
        - how the command should be typed (formatters and wrappers)
    """
    if isinstance(child, NavigableString):
        return [string_formatter(child.get_text())]

    elif child.name == "em" or child.name == "i":
        return em_wrapper(child)

    elif child.name == "p" and (
        "align" in child.attrs.keys()
        or ("style" in child.attrs.keys() and "text-align:center;" in child["style"])
    ):
        extra_string = ""
        for grandchild in child.children:
            if isinstance(grandchild, NavigableString):
                extra_string += grandchild.get_text()
        if extra_string != "":
            extra_string = r"\quad" + extra_string
        if (
            child.contents[0].name == "img"
            and "alt" in child.contents[0].attrs.keys()
            and "class" in child.contents[0].attrs.keys()
            and child.contents[0]["class"] == ["latex"]
        ):
            return [display_math_formatter(child.contents[0]["alt"] + extra_string)]
        if (
            child.contents[0].name == "a"
            and child.contents[1].name == "img"
            and "class" in child.contents[1].attrs.keys()
            and child.contents[1]["class"] == ["latex"]
        ):
            # this may break if the case handling <a name="..."> below is changed.
            # specifically, we place the <a name="..."> at the beginning of the p tag.
            return [
                labelled_math_formatter(
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
    elif (
        child.name == "img"
        and "alt" in child.attrs.keys()
        and "class" in child.attrs.keys()
        and child["class"] == ["latex"]
    ):
        return [math_formatter(child["alt"])]
    elif child.name == "img":
        # if 'src' in child.attrs.keys():
        # TODO: save images and appropriately format.
        # attempt to figure out dimensions
        if (
            "src" in child.attrs.keys()
            and "width" in child.attrs.keys()
            and "height" in child.attrs.keys()
        ):
            src, width, height = child["src"], child["width"], child["height"]
            add_to_download_queue(src)

            print(f"img tag with {src=},{width=},{height=}")
        return [f"\n img tag with no src attr: {child=} \n"]

    elif child.name == "a" and "href" in child.attrs.keys():
        for grandchild in child.children:
            if not isinstance(grandchild, NavigableString) and not isinstance(
                grandchild, str
            ):
                return ahref_wrapper(child["href"], child)
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
        return soup_processor(child) + ["\n"]
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
    blog_title = string_formatter(
        header_soup.find(id="blog-title").get_text(), remove_newlines=True
    )
    blog_tagline = string_formatter(
        header_soup.find(id="tagline").get_text(), remove_newlines=True
    )

    primary_strainer = SoupStrainer("div", id="primary")
    primary_soup = html2soup(raw_html, primary_strainer)
    title = string_formatter(primary_soup.h1.get_text(), remove_newlines=True)
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
        output = blog_title + "-" + title + ".tex"
    with open(output, "w", encoding="utf-8") as output_file:
        output_file.write("".join(out))


def main():
    """parses the command line arguments and passes them to url2tex"""

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
        with open(args.url, "r", encoding="utf8") as file:
            list_of_filenames = file.readlines()
            for filename, i in enumerate(list_of_filenames):
                numbered_name = None
                if args.output:
                    numbered_name = args.output + str(i)
                try:
                    url2tex(filename, args.local, numbered_name)
                except FileNotFoundError:
                    print(f"file no. {i}, {filename=} not found. Skipping")
                except ConnectTimeout:
                    print(f"url no. {i}, {filename=} timed out. Skipping")
    else:
        url2tex(args.url, args.local, args.output)

    # TODO: also parse the comments: potentially has bad tex
    # TODO: test batch processing
    # TODO: test timeouts and requests handling
    # TODO: make preamble fancier
    # TODO: add more fallbacks e.g. title finding
    # so that some sort of output is generated for other blogs
    # TODO: figure out how to state the required imports that don't
    # come with python (requests, bs4, lxml)


if __name__ == "__main__":
    main()
