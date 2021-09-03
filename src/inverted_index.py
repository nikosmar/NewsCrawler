import lxml.etree as et
import os.path


def create(tfidf_matrix, articles):
    inverted_index = {}
    serialized_articles = []

    for site in articles:
        serialized_articles += site[1:]

    for word, weights in tfidf_matrix.items():
        value = []

        for article_index, weight in weights.items():
            if weight > 0:
                value.append((serialized_articles[article_index][1], weight))

        inverted_index[word] = value

    return inverted_index


def store_to_file(inverted_index, xml_path=os.path.join(os.path.pardir, "inverted_index.xml")):
    inverted_index_xml = et.Element('inverted_index')

    for word, values in inverted_index.items():
        lemma = et.SubElement(inverted_index_xml, "lemma", name=word)

        for article_id, weight in values:
            et.SubElement(lemma, "document", {"id": str(article_id), "weight": str(weight)})

    # pretty string
    xml_string = et.tostring(inverted_index_xml, encoding="UTF-8", xml_declaration=True, pretty_print=True)

    with open(xml_path, "wb") as xml_file:
        xml_file.write(xml_string)

    return


def create_from_file(xml_path=os.path.join(os.path.pardir, "inverted_index.xml")):
    inverted_index = {}
    inverted_index_xml = et.parse(xml_path)
    inverted_index_xml = inverted_index_xml.getroot()

    for lemma in inverted_index_xml:
        value = []
        for document in lemma:
            value.append((document.get("id"), document.get("weight")))

        inverted_index[lemma.get("name")] = value

    return inverted_index
