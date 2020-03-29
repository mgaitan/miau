miau
====

Remix speeches for fun and profit (**work in progress**)

.. |Travis| |PyPi| |PyPi Downloads|

:License: BSD

.. :Documentation: https://miau.readthedocs.org

``miau`` is a command line tool to easily generate remixes of clips like
political speeches.

Usage
-----

::

  tin@morochita:~/lab/miau$ miau --help
  Miau: Remix speeches for fun and profit

  Usage:
    miau <input_files>... -r <remix> [-o <output>] [-d <dump>] [--lang <lang>] [--debug]
    miau -h | --help
    miau --version

  Options:
    <input_files>             Input files patterns (clip/s and its transcripts)
    -r --remix <remix>        Script text (txt or json)
    -d --dump <json>          Dump remix as json.
                              Can be loaded with -r to reuse the aligment.
    -o --output <output>      Output filename
    -h --help                 Show this screen.
    --lang <lang>             Set language (2-letter code) for inputs (default autodetect)
    --version                 Show version.


Examples
--------


- `Macri: "Vamos a salir para arriba en cualquier momento" <https://github.com/mgaitan/miau/blob/master/examples/macri_2/>`_  (spanish)

.. image:: http://img.youtube.com/vi/YtY_CRiFKPY/0.jpg
  :target: https://youtu.be/YtY_CRiFKPY


- `Merkel on Europe <https://github.com/mgaitan/miau/blob/master/examples/merkel/>`_ (english)

.. image:: http://img.youtube.com/vi/5nzWXjNJ9d8/0.jpg
   :target: https://www.youtube.com/watch?v=5nzWXjNJ9d8


- `Macron "Autres sont des menaces" <https://github.com/mgaitan/miau/blob/master/examples/macron/>`_  (french)

.. image:: http://img.youtube.com/vi/MhTv5rPo_8A/0.jpg
   :target: https://www.youtube.com/watch?v=MhTv5rPo_8A


- `Macri: "Pobreza para nuestros docentes" <https://github.com/mgaitan/miau/blob/master/examples/macri_1/>`_  (spanish)

.. image:: http://img.youtube.com/vi/vYE9AJaPAIA/0.jpg
  :target: https://youtu.be/vYE9AJaPAIA


How it works?
-------------

It uses `aeneas <https://github.com/readbeyond/aeneas>`__ to syncronize
the transcription and the input audio/video file (force align), using as many iterations as needed.

Another text define the remix script (i.e. "output speech"), using fragments of the input transcription. ``miau`` cuts the proper parts and join each of them using
`moviepy <https://github.com/Zulko/moviepy>`__.

A detailed blog post (in spanish) is `here <http://mgaitan.github.io/posts/miau-cuando-el-gato-dice-la-verdad/>`_


Why *miau*?
-----------

``miau`` means ``meow`` in spanish. It's a joke about the popular
(pejorative) `nickname assigned to Argentina's
president <https://www.taringa.net/posts/noticias/19819104/Why-Macri-Cat.html>`__
Mauricio "Cat" Macri. As I started this tool to make fun of President Macri,
this was a pretty obvious choice.


.. |Travis| image:: https://img.shields.io/travis/mgaitan/miau.svg
   :target: https://travis-ci.org/mgaitan/miau
.. |PyPi| image:: https://img.shields.io/pypi/v/miau.svg
   :target: https://pypi.python.org/pypi/miau
.. |PyPi Downloads| image:: http://img.shields.io/pypi/dm/miau.svg
   :target: https://pypi.python.org/pypi/miau
