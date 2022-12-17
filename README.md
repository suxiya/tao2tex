# tao2tex
#### Video Demo: TODO

## Description
Goes through the HTML of a wordpress math blogpost using a combination of regexes and BeautifulSoup, and spits out a $`\LaTeX`$ version. In some ways, a partial inverse for [LaTeX2WP](https://lucatrevisan.wordpress.com/latex-to-wordpress/using-latex2wp/). At the moment, this will work perfectly only for Tao's newer blogposts, but usable output is generated for the older blogposts as well.

## Requirements and Installation
You need reasonably up-to-date installations of Python 3 and LaTeX (to compile the output of `tao2tex.py`). In addition, we also require the following to be installed (e.g. via pip)
 - lxml
 - bs4 ([Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/))
 - requests

## Usage

 1. clone the repo
 2. Go to [Terry’s blog](terrytao.wordpress.com) and find a post you want to convert to $`\LaTeX`$.

2. Copy the URL. 
3. `cd` to the repo and run `python3 URL`. 
4. Wait a few seconds and a `.tex` file will be produced.
5. Run the `.tex` file in your favourite $`\LaTeX`$ program to create a finished PDF.

For instance if we copied [this](https://terrytao.wordpress.com/2018/12/09/254a-supplemental-weak-solutions-from-the-perspective-of-nonstandard-analysis-optional/) url, we should type `python3 tao2tex.py https://terrytao.wordpress.com/2018/12/09/254a-supplemental-weak-solutions-from-the-perspective-of-nonstandard-analysis-optional/ `. 

tao2tex also supports a local mode, and a batch mode:
 - For local mode, save the html of the page and then use the name of the file in place of the url, with the option `-l`. e.g. python3 tao2tex.py file.html -l
 - For batch mode, save the list of urls in a file, e.g. batch.txt and call `python3 tao2tex.py batch.txt -b. If you have a list of local files, you can use `-b -l`.

Finally, you can specify the name of the .tex file with the -o option.

## Customizing the output
The easiest way to customise the output is to modify preamble.tex. The theorems look very close to how they appear online. This is achieved with `\usepackage[framemethod=tikz]{mdframed}` and the simple style `\mdfdefinestyle{tao}{outerlinewidth = 1,roundcorner=2pt,innertopmargin=0}
`. The more standard `amsthm` environments are provided as a commented-out block.

There are a number of keywords in the preamble; they are in all-caps and begin with `TTT-`, e.g. `TTT-BLOG-TITLE`. These are substituted via regex by tao2tex.py to create the `.tex` output. It is possible to create more of these keywords; to make tao2tex see them, you should modify the `preamble_formatter` function.

## Known Limitations
 - Since we pull website data using the `requests` module, we do not see any HTML generated from javascript. In particular, in the case of Tao's blogs, tao2tex is unable to retrieve the up/downvotes for each comment. This should be easy to fix by using Selenium.

 - We did not implement logging properly, instead comments are directly printed to the command line.
 
 - We did not attempt to deal with Emoji; $`\LaTeX`$ is unable to render these without help (e.g. the `emoji` package in LuaTeX, and even this requires processing 😂 into `\emoji{face_with_tears_of_joy}`. This processing can be easily added, as python has easy to use emoji packages, but we opted to not treat this edgecase and add to the requirements. 

 - Most likely, modification is needed to work with other blogs, even those that are on wordpress, like https://mathproblems123.wordpress.com/. Despite looking quite similar, the precise way that the tags are laid out are different. 


Beijing
