import pandas as pd

def load(file_path, endline):
    df = None
    if file_path.endswith(".sav"):
        df = pd.read_spss(file_path)
    else:
        df = pd.read_excel(file_path)

    if not endline:
        _regions = {
            "Mbeya": {
                "Ituha Dispensary",
                "Madibira HC",
                "Mawindi HC"

        },
            "Songwe": {
                "Isana HC",
                "Itaka HC",
                "Ndalambo HC",
                "Machimbo Dispensary",
            },
            "Zanzibar": {
                "Mwera PHCU",
                "Mbuzini PHCU",
                "Bwejuu HCU",
                "KMKM Hospital",
                "Konde PHCU",
                "Mkoani Hospital",
                "Bwagamoyo"
            }
        }
        _names_to_regions = dict()

        for k, hospitals in _regions.items():
            for v in hospitals:
                _names_to_regions[v] = k

        facility_name = df["Q_3"]
        df['facility_name'] = df['Q_3']
        df['regions'] = facility_name.map(_names_to_regions)
    else:
        df['regions'] = df["1. Mkoa/Eneo la utafiti"]
        df['facility_name'] = df['6. Jina la kituo cha afya']

    return df

def indicator_1100a(df, endline):
    """Proportion of health facilities meeting national adolescent sexual and reproductive health standards in the selected districts in Mainland and Zanzibar

    Numerator: Number of health facilities meeting national adolescent sexual and reproductive health standards by scoring 80% and above.
    Denominator: Total number of health facilities visited.
    """
    # gen qn27mefe=1 if q27>0 | qn27>0
    # replace qn27mefe=0 if qn27mefe==.
    # lab var qn27mefe "Availability of atleast one Sexual transmitted disease"
    # tab qn27mefe
    # print(df[['Q_45', 'regions']])

    qn27mefe = df[(['T_Q_26_1', 'T_Q_26_2'] if not endline else [
        '27A. Magonjwa ya zinaa: Wanaume',
        '27B. Magonjwa ya zinaa: Wanawake'
    ])].sum(axis=1).apply(lambda x: 1 if x > 0 else 0) # TODO CHECK WITH HILLARY


    # gen qn46mefe=1 if q46>0 | qn46>0
    # replace qn46mefe=0 if qn46mefe==.
    # lab var qn46mefe"Availability of atleast one male or female CHW’s/volunteers trained to deliver counselling services on adolescent nutrition"
    # tab qn46mefe

    qn46mefe = df[(['T_Q_44_1', 'T_Q_44_2'] if not endline else [
                       '46A. Wahudumu wa afya jamii wangapi wamepata mafunzo ya utoaji ushauri nasaha kuhusu lishe kwa vijana rika? Wanaume',
                       '46B. Wahudumu wa afya jamii wangapi wamepata mafunzo ya utoaji ushauri nasaha kuhusu lishe kwa vijana rika? Wanawake'
                   ])].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)

    # gen qn47b=1 if qn47==0
    # replace qn47b=0 if qn47b==.
    # lab var qn47b "The facility did not record stock out of any contraceptive commodities in the last quarter (Sept to December 2019)"
    # tab qn47b
    _qn47 = 'Q_45' if not endline else '47. Katika robo mwaka iliyopita (Aprili-Juni 2022) kituo chako kiliweza kunakili (kurekodi) kuisha (stock out) kwa bidhaa yoyote ya uzazi wa mpango?'
    qn47b = pd.to_numeric(df[_qn47].apply(lambda x: 1 if x == "No\t" or x == "Hapana" else 0))


    # ****Generate overall standard
    # egen srhr_stands=rowtotal(qn27mefe qn29 qn31 qn32 qn46mefe qn47b Support_adolescents)
    # lab var srhr_stands"Number of national adolescent sexual and reproductive health standards attained by health facilities"
    # tab srhr_stands
    # gen srhr_stands_cat=1 if srhr_stands==7
    # replace srhr_stands_cat=0 if srhr_stands_cat==.
    # tab Region2 srhr_stands_cat,row

    qn29 = pd.to_numeric(df[('Q_28' if not endline else '29. Je kipo chumba/eneo maalumu kwa ajili ya huduma Rafiki kwa vijana')].apply(lambda x: 1 if x == "Yes" or x == "Ndio" else 0))
    qn31 = pd.to_numeric(df[('Q_30' if not endline else '31. Je kuna tangazo lolote katika kuta au mbao za matangazo kuhusu huduma kwa vijana linaloonesha muda wa huduma husika?')].apply(lambda x: 1 if x == "Yes" or x == "Ndio" else 0))
    qn32 = pd.to_numeric(df[('Q_31' if not endline else '32. Je huwa mnatoa rufaa kwa vijana wa umri wa miaka 10-19 kwa ajili ya huduma za afya na uzazi ambazo hamtoi hapa?')].apply(lambda x: 1 if x == "Yes" or x == "Ndio" else 0)).fillna(0)
    Support_adolescents = pd.to_numeric(df[('Q_46' if not endline else '48. Je kwa kawaida, kituo huwa kinawashirikisha vijana kuwasaidia watoa huduma kuweka mipango au kuandaa shughuli zozote za uboreshaji wa huduma kama vile tafiti, kushiriki katika vikao, kujadili ubora wa huduma, na mambo kama hayo?')].apply(lambda x: 1 if x == "Yes" or x == "Ndio" else 0))

    srhr_stands = qn27mefe + qn46mefe + qn29 + qn31 + qn32 +qn47b + Support_adolescents

    # NOTE BUG Midline says 80% and up is acceptable,
    # (Bloom), but the baseline actually just did anyone who
    # scored 7/7 (6 and 7 are both over 80%)

    srhr_stands_cat = srhr_stands.apply(lambda x: 1 if x >= 7 else 0)
    results = srhr_stands_cat

    return results

def table_1100a(df, endline, out):
    table_1100a = pd.concat([indicator_1100a(df, endline), df], axis=1)
    table_1100a = table_1100a[["regions", "facility_name", 0]]

    out_path = './output/' + out
    table_1100a.to_excel(out_path)
