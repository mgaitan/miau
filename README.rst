miau
====

Remix speeches for fun and profit (**work in progress**)

|Travis| |PyPi| |PyPi Downloads|

:License: BSD
:Documentation: https://miau.readthedocs.org

``miau`` is a command line tool to easily generate remixes of clips like
political speeches.

Usage
-----

```
(mvp_examples)tin@morochita:~/lab/miau$ miau -h
Miau: Remix speeches for fun and profit

Usage:
  miau -i <input>... -t <transcript>... -r <remix> [-o <output>] [-d <dump>] [--debug]
  miau -h | --help
  miau --version

Options:
  -i --input <input>                Input clip/s
  -t --transcripts <transcript>     Raw transcript of audio (sorted respect -i)
  -r --remix <remix>                Script text (txt or json)
  -d --dump <json>                  Dump remix json. Can be loaded with -r to reuse aligment.
  -o --output <output>              Output filename
  -h --help                         Show this screen.
  --version                         Show version.
  --verbosity=<verbosity>           Set verbosity
```



how it works?
-------------

It uses `aeneas <https://github.com/readbeyond/aeneas>`__ to syncronize
the transcription (as a raw text) and the input audio/video file.
Another text define the "output speech" using fragment of the input
transcription, ``miau`` cuts them and joins each part using
`moviepy <https://github.com/Zulko/moviepy>`__.

why *miau*?
-----------

``miau`` means ``meow`` in spanish. It's a joke about the popular
(derogatory) `nickname assigned to Argentina's
president <https://www.taringa.net/posts/noticias/19819104/Why-Macri-Cat.html>`__
Mauricio "Cat" Macri. As I started this tool to make fun of Macri's
speeches, this was a pretty obvious choice.



.. |Travis| image:: https://img.shields.io/travis/mgaitan/miau.svg
   :target: https://travis-ci.org/mgaitan/miau
.. |PyPi| image:: https://img.shields.io/pypi/v/miau.svg
   :target: https://pypi.python.org/pypi/miau
.. |PyPi Downloads| image:: http://img.shields.io/pypi/dm/miau.svg
   :target: https://pypi.python.org/pypi/miau
