import pathlib

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import TextTilingTokenizer

import spacy
from gensim.corpora.dictionary import Dictionary
from gensim.models import Nmf
from gensim.models.coherencemodel import CoherenceModel


def nltk_tryout_low_granularity(text):
    # Cuts the texts by lines in order for TextTilingTokenizer to be able to process them
    text = text.replace('\n', '\n\n')
    topic_tokenizer = TextTilingTokenizer(w=30,k=15,similarity_method=0, stopwords=stopwords.words('french'), cutoff_policy='LC')
    topics = topic_tokenizer.tokenize(text)

    # Delete the extra \n that are not needed to put the segments together   
    for i, topic in enumerate(topics,0):
        topics[i] = topic.replace('\n\n', '\n')
  
    return topics

def nltk_tryout_high_granularity(text):
    # Cuts the text by sentences to have a lower granularity than with a complete line
    text = text.replace('.', '.\n\n')
    topic_tokenizer = TextTilingTokenizer(w=35,k=12,similarity_method=0, stopwords=stopwords.words('french'))
    topics = topic_tokenizer.tokenize(text)
    
    # Delete the extra \n that are not needed to put the segments together 
    for i, topic in enumerate(topics,0):
        topics[i] = topic.replace('.\n\n', '.')
  
    return topics

# Do not use this function it does not give satisfactory results
def spacy_tryout(text):
    # Load the pre-trained SpaCy model
    nlp = spacy.load("fr_core_news_sm")

    start_num_topics = 2
    end_num_topics = 10

    # Preprocess the text
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    processed_text = [[token.lemma_ for token in nlp(sentence) if not token.is_stop and not token.is_punct] for sentence in sentences]

    # Create a dictionary and bag-of-words representation of the text
    dictionary = Dictionary(processed_text)
    corpus = [dictionary.doc2bow(text) for text in processed_text]

    # Choose the number of topics with the highest coherence score
    best_num_topics = None
    best_coherence_score = -1
    for num_topics in range(start_num_topics, end_num_topics+1):
        nmf = Nmf(corpus, num_topics=num_topics, random_state=42)
        cm = CoherenceModel(model=nmf, texts=processed_text, dictionary=dictionary, coherence='c_v')
        coherence_score = cm.get_coherence()
        print(f"Number of topics: {num_topics}, coherence score: {coherence_score}")
        if coherence_score > best_coherence_score:
            best_num_topics = num_topics
            best_coherence_score = coherence_score
    print(best_num_topics)

    # Perform topic modeling with the best number of topics
    nmf = Nmf(corpus, num_topics=best_num_topics, random_state=42)

    # Get the top words for each topic
    topic_top_words = []
    for _, topic in nmf.show_topics(num_words=10, formatted=False):
        top_words = [word for word, prob in topic]
        topic_top_words.append(top_words)

    # Assign topics to each sentence
    sentence_topics = []
    for sentence in processed_text:
        if sentence == []:
            sentence_topics.append(0)
            continue
        sentence_vector = dictionary.doc2bow(sentence)
        sentence_topic = nmf[sentence_vector]
        sentence_topics.append(max(sentence_topic, key=lambda x: x[1])[0])

    # Create slices based on the topics
    slices = [[] for _ in range(best_num_topics)]
    for i, sentence in enumerate(sentences):
        slices[sentence_topics[i]].append(sentence)
    return [' '.join(slice) for slice in slices]

def main():
    with open(f"{pathlib.Path().resolve()}/txt_files/Un Jour dans l'histoire_3004193.txt", mode='r') as file :
        nltk_res = nltk_tryout_high_granularity(file.read())
        with open(f"{pathlib.Path().resolve()}/txt_files_segmented/Un Jour dans l'histoire_3004193_segmented.txt", "w") as f:
            for topic in nltk_res:
                f.write(topic)
            file.close()

        file.close()

if __name__ == '__main__':
    main()