import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
from constants.dash_constants import DASH_TEMPLATE
from constants.country_config import COUNTRY

def plotly_wordcloud(tweets_text, filtered_for, bar_color='#1ca9c9'):

    if len(tweets_text) < 10:
        return None

    text = ' '.join(tweets_text)

    # remove `COUNTRY` from the `STOPWORDS`
    if COUNTRY:
        STOPWORDS.update([COUNTRY])

    word_cloud = WordCloud(
        stopwords=set(STOPWORDS)
    )

    word_cloud.generate(text)
    word_list = []
    freq_list = []

    for (word, freq), _, _, _, _ in word_cloud.layout_:
        word_list.append(word)
        freq_list.append(freq)

    word_list_top = word_list[:25]
    freq_list_top = freq_list[:25]

    frequency_fig_data = px.bar(
        template=DASH_TEMPLATE,
        x=freq_list_top[::-1],
        y=word_list_top[::-1],
        orientation='h'
    )

    frequency_fig_data.update_traces(marker_color=bar_color)
    frequency_fig_data.update_layout(
        title='Frequent words on {} tweets for {}'.format(
            len(tweets_text), filtered_for),
        font=dict(
            family='Verdana, monospace',
            size=10
        ),
        margin=dict(l=10, r=10, t=40, b=60),
        xaxis_title=None,
        yaxis_title=None
    )
    return frequency_fig_data
