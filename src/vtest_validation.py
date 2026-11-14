from src.validation import note_valide


def test_note_valide():
    assert note_valide(15) is True


def test_note_invalide():
    assert note_valide(25) is False