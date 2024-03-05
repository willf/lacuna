import sys
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET

from betacode import conv as convert

# from greekutils.beta2unicode import convert


def sentence_to_utf(sentence):
    """
    Given an XML element representing a sentence, return a string in UTF

    For example, given the following XML element:
    <sentence id="11" location="407">
        <word form="poi=" id="1">
          <lemma id="nlsj87788" entry="ποι" POS="adverb" disambiguated="0.5" TreeTagger="true">
            <analysis morph="enclitic indeclform (adverb)"/>
          </lemma>
        </word>
        <word form="fe/resqe" id="2">
          <lemma id="110598" entry="φέρω" POS="verb" TreeTagger="false" disambiguated="n/a">
            <analysis morph="pres imperat mp 2nd pl"/>
            <analysis morph="pres ind mp 2nd pl"/>
            <analysis morph="imperf ind mp 2nd pl (homeric ionic)"/>
          </lemma>
        </word>
        <punct mark=","/>
        <word form="w)/nqrwpoi" id="3">
          <lemma id="8909" entry="ἄνθρωπος" POS="noun" TreeTagger="false" disambiguated="n/a">
            <analysis morph="masc nom/voc pl"/>
          </lemma>
        </word>
        <punct mark=";"/>
      </sentence>

    The function should return:
    poi= fe/resqe w)/nqrwpoi;

    There should be a space between each word, but not punctuation marks.
    """
    # first get all the children of the sentence element
    buffer = []
    for element in sentence:
        # if the element is a word, then add the form attribute to the string
        if element.tag == "word":
            word = element.attrib["form"].upper()
            word = convert.beta_to_uni(word)
            buffer.append(" " + word)
        # if the element is a punctuation mark, then add the mark attribute to the string
        elif element.tag == "punct":
            mark = element.attrib["mark"]
            buffer.append(mark)
    return "".join(buffer).strip()


def doc_to_sentences(doc):
    """
    Given an XML element representing a document, return a list of strings in UTF

    """
    for element in doc:
        if element.tag == "sentence":
            yield sentence_to_utf(element)


def word_element_to_utf(word):
    """
    Given an XML element representing a word, add an attribute to the element with the word in UTF.

    For example, given the following XML element:
    <word form="poi=" id="1">
      <lemma id="nlsj87788" entry="ποι" POS="adverb" disambiguated="0.5" TreeTagger="true">
        <analysis morph="enclitic indeclform (adverb)"/>
      </lemma>
    </word>

    <word form="poi=" utf="ποι" id="1">
      <lemma id="nlsj87788" entry="ποι" POS="adverb" disambiguated="0.5" TreeTagger="true">
        <analysis morph="enclitic indeclform (adverb)"/>
      </lemma>
    </word>
    """
    if "form" in word.attrib:
        word.set("utf8", convert.beta_to_uni(word.attrib["form"].upper()))


def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    ET.indent(elem, space="  ")
    return ET.tostring(elem, "utf-8").decode()


if __name__ == "__main__":
    # Read the input from stdin
    tree = ET.parse(sys.stdin)
    root = tree.getroot()
    for element in root.iter():
        word_element_to_utf(element)
    print(prettify(root))
