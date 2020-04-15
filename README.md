# meteor

An implementation of the METEOR score for machine translation.

See [Denkowski and Lavie 2014](https://www.aclweb.org/anthology/W14-3348.pdf),
[Lavie and Agarwal 2007](https://www.aclweb.org/anthology/W07-0734.pdf),
[Banerjee and Lavie 2005](https://www.aclweb.org/anthology/W05-0909.pdf)  
TLDR: https://en.wikipedia.org/wiki/METEOR

Currently supports German and English but any language supported by NLTK's
tokenization and stemming is trivial to add.


### Disclaimer

I've built this for fun and because I wanted to know how it works.
This is neither battle-tested nor has it ever been used in any serious machine
translation context. Don't use this unless you know what you're doing.

Meteor is not a simple metric and different implementations will create
slightly different results. **If you want to compare your results to others,
use the tool they were using.** The [implementation by Denkowski and Lavie](https://www.cs.cmu.edu/~alavie/METEOR/)
 seems to be the one that is used most widely. (Especially don't use
NLTK's meteor implementation, the alignment is broken (NLTK version 3.5).)


### Usage

Building it will install a command line script called `meteor` which will run
the metric on two files, one with system output and one with translation
references. Both files must have one sentence per line and be of the same length.
Default language is German. Type `meteor --help` to see a description of all options.

If you don't want to use it with files, you can use it programmatically:
```python
from meteor import IdentityStage
from meteor import Language
from meteor import StemmingStage
from meteor import meteor

# setup matching stages with weights
stages = [IdentityStage(1.0), StemmingStage(0.6, Language.german)]

hypothesis = "Die Katze sitzt auf der Matte."
reference = "Auf der Matte sitzt die Katze."

score = meteor(hypothesis, reference, stages, Language.german)
```

If you want to implement your own matching stage, derive from `meteor.StageBase`
and implement `process_tokens()`.


### Development

Build by typing `make`. This will build the project for development.
It will also download some nltk resources for the tokenizer and the stemmer.

Tokenization and stemming are done with NLTK's `word_tokenize()` and `SnowballStemmer`.

To find the best alignment, it relies on https://python-mip.com to solve
a mixed integer linear program.


### Dependencies

* python 3.8
* virtualenv
* make
