# tao2tex

#### Video Demo: <https://youtu.be/-3nFLI_w1ao>

## Description

Goes through the HTML of a wordpress math blogpost (mainly, [Prof. Terry Tao’s blog](https://terrytao.wordpress.com)) using a combination of regexes and BeautifulSoup, and spits out a $\rm\LaTeX$ version. In some ways, a partial inverse for [LaTeX2WP](https://lucatrevisan.wordpress.com/latex-to-wordpress/using-latex2wp/). However, we also include the comments (which sometimes has great information.) This should work well for many of Tao's blog posts, and errors should be few and easy to fix.

## Requirements and Installation

You need reasonably up-to-date installations of [Python 3](https://www.python.org/) and $\rm\LaTeX$ ([software](https://www.latex-project.org/get/) to compile the output of `tao2tex.py`). In addition, we also require the following to be installed (e.g. via pip)

- [`lxml`](https://lxml.de/)
- `bs4` ([Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/))
- [`requests`](https://requests.readthedocs.io/en/latest/)
- [`emoji`](https://pypi.org/project/emoji/)

You could also use a cloud service like [Overleaf](https://www.overleaf.com/) in lieu of a new $\rm\TeX$ installation.

## Usage

 1. clone the repo
 2. Go to [Terry’s blog](terrytao.wordpress.com) and find a post you want to convert to $\rm\LaTeX$.

 3. Copy the URL.
 4. `cd` to the repo and run `python3 tao2tex.py URL`.
 5. Wait a few seconds and a `.tex` file will be produced.
 6. Run the `.tex` file in your favourite $\rm\LaTeX$ workflow to create a finished PDF.

For instance if we copied [this](https://terrytao.wordpress.com/2018/12/09/254a-supplemental-weak-solutions-from-the-perspective-of-nonstandard-analysis-optional/) url, we should type `python3 tao2tex.py https://terrytao.wordpress.com/2018/12/09/254a-supplemental-weak-solutions-from-the-perspective-of-nonstandard-analysis-optional/`.

tao2tex also supports a local mode, and a batch mode:

- For local mode, save the html of the page and then use the name of the file in place of the url, with the option `-l`. e.g. `python3 tao2tex.py file.html -l`
- For batch mode, save the list of urls in a file, e.g. batch.txt and call `python3 tao2tex.py batch.txt -b`. If you have a list of local files, you can use `-b -l`.

In addition, you can specify the name of the .tex file with the `-o` option, the `-p` option prints the output to the command-line, and `-d` enables a rudimentary debugger.

## Testing

Since the desired output is not precisely defined, we provide a `test.html` file which may be used for debugging (in particular, for adding features, adjusting to breaking changes, or for adapting to other blogs). It is a short sample HTML file that can be used to test the output of tao2tex via the command `python3 tao2tex.py test.html -l`.

## Customizing the output

The easiest way to customise the output is to modify `preamble.tex`. The theorems look very close to how they appear online. This is achieved with `\usepackage[framemethod=tikz]{mdframed}` and the simple style `\mdfdefinestyle{tao}{outerlinewidth = 1,roundcorner=2pt,innertopmargin=0}`. The more standard `amsthm` environments are provided as a commented-out block.

There are a number of keywords in the given `preamble.tex`; they are in all-caps and begin with `TTT-`, e.g. `TTT-BLOG-TITLE`. These are substituted via regex by tao2tex.py to create the `.tex` output. It is possible to create more of these keywords; to make tao2tex see them, you should modify the `preamble_formatter` function.

Emoji that appear (for instance, in [certain](https://terrytao.wordpress.com/2022/10/07/a-bayesian-probability-worksheet/#comment-659640) comments) are processed (e.g. 😂 becomes `\emoji{face_with_tears_of_joy}`); `\emoji` is defined to simply be `\texttt`, as $\rm\LaTeX$ is unable to render emoji without help. But you can get the actual emoji if you comment out this definition, import the [`emoji`](https://www.ctan.org/pkg/emoji) package, and compile with $\rm Lua\TeX$, [a variant](https://www.luatex.org/) of $\rm pdf\TeX$.

## Known Limitations or Issues

- the more recent versions (since 2018) of $\rm pdf\LaTeX$ will cope with many unicode symbols (but not all) because [UTF8 is assumed to be the default input encoding](https://tex.stackexchange.com/questions/34604/entering-unicode-characters-in-latex). If you do not want to install a newer version, you can try using [Overleaf](https://www.overleaf.com/). You might be able to get away with adding `\usepackage[TU]{inputenc}` or `\usepackage[T1]{inputenc}` to the preamble...

- In `string_formatter`, we escape only a few unicode characters to attempt to please the $\rm\TeX$ engine. We replace greek characters, which do appear on [some](https://terrytao.wordpress.com/2022/10/03/what-are-the-odds/#comment-658396) of the blog posts, in an arguably naive and counterproductive manner (e.g. alpha into`\(\alpha\)`). $\rm{}pdf\LaTeX$ will complain, and $\rm{}Xe\LaTeX$ and $\rm{}Lua\LaTeX$ will work if you switch to a font that has the glyphs (without, these two will still compile.)

- Since we pull website data using the `requests` module, we do not see any HTML generated from Javascript. This should be easy to adapt by using Selenium.

- For the same reason, we are unable to process the occasional polls that Tao makes. However, the rest of the post should work as expected.

- In some posts, e.g. [this one](https://terrytao.wordpress.com/2020/04/13/247b-notes-2-decoupling-theory/#comments), there are so many comments that we should actually check multiple pages. We do not currently do this.

- It is possible though unlikely that two different images of the same name are downloaded from two different posts. To avoid this, run `tao2tex.py` in different folders.

- Most likely, modification of the `BeautifulSoup` part is needed to work with other blogs, even those that are on Wordpress. Despite looking quite similar, the precise way that the tags are laid out seem to differ from blog to blog.

- For similar reasons, if Prof Tao ever updates the layout of the blog, this tool will break. Hopefully such a new version will directly support a good print option, but in any case the posts pre-update with the older layout will still be accessible, thanks to the [Internet Archive](https://web.archive.org/web/20220000000000*/terrytao.wordpress.com).
