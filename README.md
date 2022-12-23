# tao2tex

#### Video Demo: <https://youtu.be/-3nFLI_w1ao>

## Description

Goes through the HTML of a wordpress math blogpost (mainly, [Prof. Terry Tao’s blog](terrytao.wordpress.com)) using a combination of regexes and BeautifulSoup, and spits out a $\LaTeX$ version. In some ways, a partial inverse for [LaTeX2WP](https://lucatrevisan.wordpress.com/latex-to-wordpress/using-latex2wp/). However, we also include the comments (which sometimes has great information.) At the moment, this will work perfectly only for Tao's newer blogposts, but usable output is generated for the older blogposts as well.

## Requirements and Installation

You need reasonably up-to-date installations of Python 3 and $\LaTeX$ (to compile the output of `tao2tex.py`). In addition, we also require the following to be installed (e.g. via pip)

- lxml
- bs4 ([Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/))
- requests

## Usage

 1. clone the repo
 2. Go to [Terry’s blog](terrytao.wordpress.com) and find a post you want to convert to $\LaTeX$.

 3. Copy the URL.
 4. `cd` to the repo and run `python3 tao2tex.py URL`.
 5. Wait a few seconds and a `.tex` file will be produced.
 6. Run the `.tex` file in your favourite $\LaTeX$ program to create a finished PDF.

For instance if we copied [this](https://terrytao.wordpress.com/2018/12/09/254a-supplemental-weak-solutions-from-the-perspective-of-nonstandard-analysis-optional/) url, we should type `python3 tao2tex.py https://terrytao.wordpress.com/2018/12/09/254a-supplemental-weak-solutions-from-the-perspective-of-nonstandard-analysis-optional/`.

tao2tex also supports a local mode, and a batch mode:

- For local mode, save the html of the page and then use the name of the file in place of the url, with the option `-l`. e.g. `python3 tao2tex.py file.html -l`
- For batch mode, save the list of urls in a file, e.g. batch.txt and call `python3 tao2tex.py batch.txt -b`. If you have a list of local files, you can use `-b -l`.

In addition, you can specify the name of the .tex file with the `-o` option, the `-p` option prints the output to the command-line, and `-d` enables a rudimentary debugger.

## Customizing the output

The easiest way to customise the output is to modify preamble.tex. The theorems look very close to how they appear online. This is achieved with `\usepackage[framemethod=tikz]{mdframed}` and the simple style `\mdfdefinestyle{tao}{outerlinewidth = 1,roundcorner=2pt,innertopmargin=0}`. The more standard `amsthm` environments are provided as a commented-out block.

There are a number of keywords in the given `preamble.tex`; they are in all-caps and begin with `TTT-`, e.g. `TTT-BLOG-TITLE`. These are substituted via regex by tao2tex.py to create the `.tex` output. It is possible to create more of these keywords; to make tao2tex see them, you should modify the `preamble_formatter` function.

## Known Limitations or Issues

- Since we pull website data using the `requests` module, we do not see any HTML generated from Javascript.  This should be easy to fix by using Selenium.

- For the same reason, we are unable to process the occasional polls that Tao makes. However, the rest of the post should work as expected.

- We did not attempt to deal with Emoji; $`\LaTeX`$ is unable to render these without help (e.g. the [`emoji`](https://www.ctan.org/pkg/emoji) package with LuaTeX, and even this requires processing e.g. 😂 into `\emoji{face_with_tears_of_joy}`.) This processing can be easily added, as python has easy to use emoji packages, but we opted to not treat this edgecase and add to the requirements.

- It is possible though unlikely that two different images of the same name are downloaded from two different posts. To avoid this, run `tao2tex.py` in different folders.

- Most likely, modification of the BeautifulSoup part is needed to work with other blogs, even those that are on wordpress. Despite looking quite similar, the precise way that the tags are laid out seem to be different.
