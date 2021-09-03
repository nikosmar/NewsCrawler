import nltk
import os.path
import string
import pandas
from scrapy.selector import Selector
from sklearn.feature_extraction.text import TfidfVectorizer

punctuation = set(string.punctuation)
closed_class_tags = {"CD", "CC", "DT", "EX", "IN", "LS", "MD", "PDT", "POS", "PRP", "PRP$", "RP", "TO", "UH", "WDT",
                     "WP", "WP$", "WRB"}


def html_to_tagged_text(html_file, xpath_rules):
    with open(html_file, 'r') as f:
        html_content = f.read()

    clear_text = Selector(text=html_content).xpath(xpath_rules).getall()

    # from the html's file path get the file name without ".html"
    file_name = os.path.split(html_file)[1].split('.')[0]
    output_file_path = os.path.join(os.path.pardir, "tagged_articles", file_name + ".txt")

    with open(output_file_path, 'w') as f:
        for phrase in clear_text:
            tagged_phrase = nltk.pos_tag(nltk.word_tokenize(phrase))

            for (word, tag) in tagged_phrase:
                if len(word) > 1:
                    f.write(word + " " + tag + "\n")

    return output_file_path


def tagged_text_vectorizer(tagged_articles):
    useful_tagged_texts = []
    lemmatizer = nltk.stem.WordNetLemmatizer()
    useful_word_counts = []

    for tagged_text_path in tagged_articles:
        with open(tagged_text_path, 'r') as f:
            tagged_text = f.readlines()

        useful_tagged_text = []
        useful_word_count = 0

        for line in tagged_text:
            word, tag = line.split()

            if not (tag in closed_class_tags or tag in punctuation):
                # useful_tagged_text.append(word)
                useful_word_count += 1

                if tag.startswith('J'):
                    tag = nltk.corpus.wordnet.ADJ
                elif tag.startswith('V'):
                    tag = nltk.corpus.wordnet.VERB
                elif tag.startswith('R'):
                    tag = nltk.corpus.wordnet.ADV
                else:
                    tag = nltk.corpus.wordnet.NOUN

                lemmatized_word = lemmatizer.lemmatize(word, pos=tag)

                useful_tagged_text.append(lemmatized_word.lower())

        useful_tagged_texts.append(' '.join(useful_tagged_text))
        useful_word_counts.append(useful_word_count)

    vectorizer = TfidfVectorizer()
    tf_idf_matrix = vectorizer.fit_transform(useful_tagged_texts)
    df = pandas.DataFrame(tf_idf_matrix.toarray(), columns=vectorizer.get_feature_names())

    return df

    # stemmer = nltk.stem.porter.PorterStemmer()
    # for word in phrase.split():
    #     lowered_word = word.lower()
    #
    #     if lowered_word not in stopwords:
    #         stemmed_word = stemmer.stem(word)
    #
    #         # strip punctuation before appending
    #         if stemmed_word[0] in punctuation:
    #             stemmed_word = stemmed_word[1:]
    #         # checks if stemmed_word is an empty string
    #         # happens when stemmed_word was a single punctuation character
    #         if stemmed_word:
    #             if stemmed_word[-1] in punctuation:
    #                 stemmed_word = stemmed_word[:-1]
    #
    #             tokenized_text.append(stemmed_word)

    # tf_idf_matrix = vectorizer.fit_transform(titles)
    # df = pandas.DataFrame(tf_idf_matrix.toarray(), columns=vectorizer.get_feature_names())
