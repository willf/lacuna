import re
import unicodedata


def remove_diacritics(greek_text):
    """
    Remove the diacritics from a Greek text.
    including accents, breathings, iota subscripts, diaeresis, macrons, etc.
    >>> remove_diacritics('ἓν οἶδα ὅτι οὐδὲν οἶδα.')
    'εν οιδα οτι ουδεν οιδα.'
    """
    return "".join(
        c
        for c in unicodedata.normalize("NFD", greek_text)
        if unicodedata.category(c) != "Mn"
    )


# 27.22.20 Λέγει ὁ μαρτυρῶν ταῦτα· Ναί· ἔρχομαι ταχύ. Ἀμήν· ⸀ἔρχου, κύριε Ἰησοῦ.


def remove_book_chapter_verse(text):
    """
    Remove book, chapter, and verse references from a string.
    >>> remove_book_chapter_verse('27.22.20 Λέγει ὁ μαρτυρῶν ταῦτα· Ναί· ἔρχομαι ταχύ. Ἀμήν· ⸀ἔρχου, κύριε Ἰησοῦ.')
    'Λέγει ὁ μαρτυρῶν ταῦτα· Ναί· ἔρχομαι ταχύ. Ἀμήν· ⸀ἔρχου, κύριε Ἰησοῦ.'
    """
    return text[9:]


def remove_punctuation(text):
    """
    Remove punctuation from a string.
    >>> remove_punctuation('Λέγει ὁ μαρτυρῶν ταῦτα· Ναί· ἔρχομαι ταχύ. Ἀμήν· ⸀ἔρχου, κύριε Ἰησοῦ.')
    'Λέγει ὁ μαρτυρῶν ταῦτα Ναί ἔρχομαι ταχύ Ἀμήν ἔρχου κύριε Ἰησοῦ'
    """
    return re.sub(r"[.·;,⸀⸃⸂]", "", text)


def process_verse(text):
    """
    Process a verse for use in a language model.
    >>> process_verse('27.22.20 Λέγει ὁ μαρτυρῶν ταῦτα· Ναί· ἔρχομαι ταχύ. Ἀμήν· ⸀ἔρχου, κύριε Ἰησοῦ.')
    'λεγειομαρτυρωνταυταναιερχομαιταχυαμηνερχουκυριειησου'
    """
    return (
        remove_punctuation(remove_book_chapter_verse(remove_diacritics(text)))
        .lower()
        .replace(" ", "")
    )


if __name__ == "__main__":

    # import doctest

    # doctest.testmod()

    import sys

    # Read the input from stdin
    for line in sys.stdin:
        print(process_verse(line).strip())
