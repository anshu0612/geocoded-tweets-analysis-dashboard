
import re
import spacy
from utils.contraction_mapping import *


def regex_or(*items):
    return '(?:' + '|'.join(items) + ')'


contractions = re.compile(
    "(?i)(\w+)(n[''′]t|[''′]ve|[''′]ll|[''′]d|[''′]re|[''′]s|[''′]m)$", re.UNICODE)
whitespace = re.compile(
    "[\s\u0020\u00a0\u1680\u180e\u202f\u205f\u3000\u2000-\u200a]+", re.UNICODE)
punct_chars = r"['\"""''.?!…,:;]"
# punct_seq = punct_chars + "+"    # 'anthem'. => ' anthem '.
punct_seq = r"['\"""'']+|[.?!,…]+|[:;]+"   # 'anthem'. => ' anthem ' .
entity = r"[&<>\"]"
url_start_1 = r"(?:https?://|\bwww\.)"
commonTLDs = r"(?:com|org|edu|gov|net|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|pro|tel|travel|xxx)"
cc_tlds = \
    r"(?:ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|" \
    r"bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|" \
    r"er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|" \
    r"hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|" \
    r"lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|" \
    r"nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|" \
    r"sl|sm|sn|so|sr|ss|st|su|sv|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|" \
    r"va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|za|zm|zw)"
url_start_2 = \
    r"\b(?:[A-Za-z\d-])+(?:\.[A-Za-z0-9]+){0,3}\." + regex_or(
        commonTLDs, cc_tlds) + r"(?:\." + cc_tlds + r")?(?=\W|$)"
url_body = r"(?:[^\.\s<>][^\s<>]*?)?"
url_extra_crap_before_end = regex_or(punct_chars, entity) + "+?"
url_end = r"(?:\.\.+|[<>]|\s|$)"
URL_REGEX = regex_or(url_start_1, url_start_2) + url_body + \
    "(?=(?:" + url_extra_crap_before_end + ")?" + url_end + ")"


class TwitterDataCleaning():

    def __init__(self):
        # self.nlp = spacy.load('en_core_web_sm')
        self.nlp = spacy.load('en')

    def remove_puctuations(self, text):
        text = re.sub("[!\.:;,!\"&\?_\-]", ' ', text)

        return text.replace('[', ' ').replace('[', ' ').replace('(', ' ').replace(')', ' ').replace('\'', '')

    def remove_html(self, text):
        return re.sub("<.*?>", '', text, re.DOTALL)

    def remove_RTs(self, text):
        return text.replace('RT', '')

    def remove_multiple_spaces(self, text):
        text = text.strip()
        return re.sub(' +', ' ', text)

    def remove_urls(self, text):
        return re.sub(URL_REGEX, '', text)

    def remove_two_characters_word(self, text):
        return re.sub(r'\b\w{1,2}\b', '', text)

    def remove_userid(self, text):
        return re.sub("@[A-Z_a-z0-9]+", "", text)

    def remove_numbers(self, text):
        return re.sub("^\d+\s|\s\d+\s|\s\d+$", " ", text)

    def remove_hashtags(self, text, replace=False):
        return re.sub("#[A-Za-z0-9]+", "", text)

    def remove_stopwords(self, text):
        my_text = self.nlp(text)
        token_list = []
        for token in my_text:
            token_list.append(token.text)
        filtered_sentence = []
        for word in token_list:
            lexeme = self.nlp.vocab[word]
            if lexeme.is_stop == False:
                filtered_sentence.append(word)
        return ' '.join(word for word in filtered_sentence)

    def remove_emojis(self, text):
        return text.encode('ascii', 'ignore').decode('ascii')

    def convert_to_lowercase(self, text):
        return str(text).lower()

    def expand_contractions(self, text):
        return ' '.join([contraction_mapping[t] if t in contraction_mapping else t for t in text.split(" ")])

    def lemmatization(self, text, allowed_tags=['NOUN', 'ADJ', 'VERB', 'ADV']):
        text = self.nlp(text)
        new_text = []
        for token in text:
            if token.pos_ in allowed_tags:
                new_text.append(token.lemma_)
        return " ".join(new_text)

    def remove_new_line(self, text):
        return re.sub('\s+', ' ', text)

    def replace_amp(self, text):
        return text.replace('&amp;', '&')

    def clean_text(self, text, for_sentiment_analysis=False):
        text = self.remove_userid(text)
        text = self.remove_urls(text)
        text = self.remove_RTs(text)
        text = self.remove_hashtags(text)

        text = self.remove_html(text)
        text = self.remove_numbers(text)
        text = self.expand_contractions(text)
        text = self.remove_puctuations(text)
        text = self.convert_to_lowercase(text)

        if not for_sentiment_analysis:
            text = self.remove_emojis(text)
            text = self.remove_stopwords(text)

        text = self.remove_new_line(text)
        # text = self.remove_two_characters_word(text)
        text = self.remove_multiple_spaces(text)
        return text
