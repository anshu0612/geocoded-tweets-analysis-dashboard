def human_format(num):
    '''
     Formatting numbers in readable format
    '''
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

# import fasttext as ft
# def detect_lang(text):
#     lang_detect = ft.load_model("./model/lid.176.ftz")
#     return lang_detect.predict(lang_detect, k = 1)[0][0].split("__")[2]
