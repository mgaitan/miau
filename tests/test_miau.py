import pytest
from miau.miau import fragmenter


SPEECH_1 = """Escucharemos las palabras del señor presidente de La Nación,
Mauricio Macri.

Buenos días, buenos días. Una alegría estar acá a punto de ser otro vehículo
experimental en el espacio con este viento, vamos a salir para arriba en cualquier momento con la Gobernadora
que con el viento se emociona y le caen las lágrimas."""

@pytest.mark.parametrize('remix, expected', [("""Buenos días, buenos días.
vamos a salir para arriba
con la Gobernadora
con el viento
en el espacio """,

["""Escucharemos las palabras del señor presidente de La Nación, Mauricio Macri.

Buenos días, buenos días.
Una alegría estar acá a punto de ser otro vehículo experimental
en el espacio
con este viento,
vamos a salir para arriba
en cualquier momento
con la Gobernadora
que
con el viento
se emociona y le caen las lágrimas."""]
)
])
def test_fragment(remix, expected):
    result = fragment(SPEECH_1, remix)
    assert result == expected
