Toy CCG Parser
==============

OVERVIEW
--------

compact CCG Parser


Python 2.x or 3.x
-----------------
toyccg is tested with

- CPython 2.7.5
- pypy3  2.4.0 (Python3.2.5 compatible)


USAGE
-----

`python -m toyccg.english < sentences.txt`

`python -m toyccg.japanese < sentences.ja.txt`

```>>> import toyccg.japanese as jpn
>>> jpn.run(u"�\�[�X�R�[�h�������ɏ���")
test run : sentence=�\�[�X�R�[�h�������ɏ���
�\�[�X�R�[�h	N	(guess)
��	NP[obj]\N
����	N
��	((S[null]\NP[obj])/(S[null]\NP[obj]))\N
����	S[null]\NP[obj]

>>> import toyccg.japanese as jpn
>>> r = jpn.parser.parse(u"�d�����������Ȃ��B")
>>> t = r.next()
>>> for c in t.leaves():
...     print (c.token , c.catname)
... 
(u'\u4ed5\u4e8b', u'N')
(u'\u3092', 'NP[obj]\\N')
(u'\u3057', u'TV[cont]')
(u'\u305f\u304f', 'TV[neg]\\TV[cont]')
(u'\u306a\u3044', '(S[null]\\NP[obj])\\TV[neg]')
(u'\u3002', 'ROOT\\S[null]')
```


TODO
----

* brush up lexicons

* apply to other languages(e.g. Klingon,Chinese,etc.)

* semantic parsing support

* supporting unsupervised inference of syntactic categories

* solve CCG grammatical inference


References
----------

* The Syntactic Process (MIT Press, Mark Steedman, 2000)

* ���{�ꕶ�@�̌`�����_�F���p�̌n�E����\���E�Ӗ����� (���낵���o��, �ˎ����, 2010)

* Efficient Normal-Form Parsing for Combiantory Categorial Grammar (Jason Eisner, 1996)

* Normal-form parsing for Combinatory Categorial Grammars with generalized composition and type-raising (2010)

* Unsupervised syntax learning with categorial grammars using inference rules (2009)

* A* CCG Parsing with a Supertag-factored Model (2014)
([paper](http://www.aclweb.org/anthology/D14-1107))


