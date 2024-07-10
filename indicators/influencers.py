import pandas as pd
import datetime as dt



def _age_to_agegroup(age):
    if age < 10:
        return "0-9"
    elif age < 15:
        return "10-14"
    elif age < 20:
        return "15-19"
    else:
        return ">19"

def load(file_path, endline):
    df = pd.read_spss(file_path)

    regions = {
        'Mbeya': 'Mbeya',
        'Songwe': 'Songwe',
        'Pemba (Zanzibar)': 'Zanzibar',
        'Unguja (Zanzibar)': 'Zanzibar',
        'Zanzibar': 'Zanzibar',
    }

    df['regions'] = df[('Q_5' if not endline else "1. Mkoa/Eneo la utafiti")].map(regions)

    df['age'] = df['Q_10']
    df['agegroup'] = df['age'].map(_age_to_agegroup)

    df['sex'] = df["Q_20"]
    df['gender_support'] = df['Q_3']

    return df

def load_endline(female, male):
    fdf = pd.read_excel(female)
    mdf = pd.read_excel(male)

    fdf['gender_support'] = 'Girls'
    mdf['gender_support'] = 'Boys'

    df = pd.concat([fdf,mdf])
    df['age'] = df['6. Umri wa mhojiwa']
    df['regions'] = df["1. Mkoa/Eneo la utafiti"]

    df['agegroup'] = df['age'].map(_age_to_agegroup)

    df['sex'] = df['Gender']
    return df


def indicator_1200a(df, endline):
    """Proportion of community influencers (Local govt officials / Parents / teachers / religious leaders / HCW)
    who demonstrate supportive attitudes towards adolescents’ SRHR and nutrition (disaggregated by support for boys and for girls)

    Numerator: Number of community influencers who demonstrated a supportive attitude.
    Denominator: Total number of community  interviewed.
    """

    filtered_df = df[df["gender_support"] == "Girls"]

    _questions_boys = ([
        'Q_21',
        'Q_23',
        'Q_24',
        'Q_25',
        'Q_26',
        'Q_27',
        'Q_28',
        'Q_29',
        'Q_32',
        'Q_33',
        'Q_34',
        'Q_35',
        'Q_36',
        'Q_37',
    ] if not endline else [
        '1. Wavulana waliobalehe wanapaswa kupata haki za afya ya uzazi',
        '3. Wavulana waliobalehe wenye umri wa miaka 10 – 19 ambaye ameshaanza kujamiiana, anapaswa kupata maarifa na mbinu za kupanga uzazi',
        '4. Wavulana waliobalehe wanapaswa kupata huduma za lishe',
        '5. Wazazi wanapaswa kujadili masuala yanayohusu afya ya uzazi wa kijinsia na wavulana wao',
        '6. Wazazi wanapaswa kujadili masuala yanayohusu lishe na wavulana wao',
        '7. Wazazi/Walimu wanapaswa kujadili / kufundisha wavulana vijana juu ya Hatari za tabia ya ndoa ya mapema',
        '8. Wavulana waliobalehe wanahitaji kuelimishwa kuhusu HIV na AIDS',
        '9. Wavulana waliobalehe wenye umri wa miaka 10-19 wanapaswa kupata Elimu kuhusu magonjwa ya zinaa.',
        '12. Wavulana waliobalehe wanapaswa kuwezeshwa ili kukabiliana na shinikizo la rika',
        '13. Wazazi wanahitaji kuwasaidia wavulana wao wanaobalehe kuelewa mabadiliko yanayotokea katika mwili wakati wa kubalehe',
        '14. Wazazi wanapaswa kuwaelimisha wavulana wao waliobalehe kuhusu Mimba za utotoni na matatizo yake',
        '15. Wahudumu wa afya na Wazazi wanahitaji kushirikiana na kuwafundisha wavulana waliobalehe juu ya Hatari ya kutoa mimba',
        '16. Wazazi/walimu wanapaswa kuwa watetezi wazuri na walio mstari wa mbele kuwaelimisha wavulana waliobalehe juu ya kukatisha tamaa mazoea mabaya ya kitamaduni (tohara kwa wanawake na ndoa za utotoni za kulazimishwa)',
        '17. Masomo ya lishe ni muhimu kwa lishe bora kwa wavulana hata wakati wa utoto wao',
    ])

    _questions_girls = [
        'Q_39',
        'Q_40',
        'Q_41',
        'Q_42',
        'Q_43',
        'Q_44',
        'Q_45',
        'Q_46',
        'Q_47',
        'Q_48',
        'Q_49',
        'Q_52',
        'Q_53',
        'Q_54',
        'Q_55',
        'Q_56',
        'Q_57',
        'Q_58',
        'Q_59',
        'Q_60',
    ] if not endline else [
        '1. Wasichana waliobalehe wanapaswa kupata haki za afya ya uzazi',
        '2. Wasichana waliobalehe wenye umri wa miaka 10 - 14 wanapaswa kupata maarifa juu ya uzazi wa mpango',
        '3. Wasichana waliobalehe umri wa miaka 10 -19 ambaye ameshaanza kujamiiana anapaswa kupata maarifa na mbinu za kupanga uzazi',
        '4. Wasichana waliobalehe (miaka 10-19) wanapaswa kupata huduma za lishe',
        '5. Wazazi wanapaswa kujadili masuala yanayohusu afya ya uzazi wa kijinsia na wasichana waliobalehe',
        '6. Wazazi wanapaswa kujadili masuala yanayohusu lishe na wasichana wao',
        '7. Wasichana waliobalehe wanaopata mimba wakiwa na umri wa miaka 10 – 19 wanapaswa kupata huduma za ANC, intrapartum, post-partum na baada ya kujifungua.',
        '8.Wasichana waliobalehe wana haki ya kupata huduma za lishe',
        '9. Wazazi/Walimu wanapaswa kujadili/wafundishe wasichana waliobalehe juu ya Hatari za tabia ya ndoa za utotoni.',
        '10. Wasichana waliobalehe wanahitaji kuelimishwa kuhusu HIV na AIDS',
        '11. Wasichana wenye umri wa miaka 10-19 wanapaswa kupata Elimu ya magonjwa ya zinaa.',
        '14. Wasichana wenye umri wa miaka 10-14 wanapaswa kupata huduma za chanjo ya saratani ya mlango wa kizazi',
        '15. Wasichana waliobalehe wanahitaji huduma za Mwongozo na ushauri',
        '16. Wasichana waliobalehe wanapaswa kuwezeshwa ili kukabiliana na shinikizo la rika',
        '17. Wazazi wanapaswa kuwasaidia watoto wao (wasichana) kuelewa mabadiliko yanayotokea katika miili yao wakati wa kubalehe',
        '18. Wazazi wanapaswa kuwaelimisha wasichana wao kuhusu mimba za utotoni na matatizo yake',
        '19. Wahudumu wa afya na Wazazi wanahitaji kushirikiana na kuwafundisha wasichana waliobalehe juu ya Hatari ya kuavya mimba.',
        '20. Wazazi/walimu wanapaswa kuwa watetezi wazuri na walio mstari wa mbele kuwaelimisha wasichana waliobalehe juu ya kukatisha tamaduni hatari (tohara kwa wanawake na ndoa za utotoni za kulazimishwa).',
        '21. Masomo ya lishe ni muhimu kwa lishe bora kwa wasichana hata wakati wa utoto wao',
        '22. Programu wa WIFAS shuleni ni muhimu kwa wasichana waliobalehe (miaka 10-19)',
    ]

    assert(len(_questions_boys) == 14)
    assert(len(_questions_girls) == 20)
    _valid_answers = {
        'Strongly Agree',
        'Slightly Agree',
        # Endline
        'Kukubaliana sana',
        'Kukubaliana kidogo',
    }

    _questions = _questions_boys + _questions_girls + ['gender_support']
    _debug_answered = set(_questions)

    def _score_row(row):
        qs = _questions_boys
        if row['gender_support'] == 'Girls':
            qs = _questions_girls

        score = 0
        for question in qs:
            # if endline:
            #     import pdb; pdb.set_trace()


            if row[question] in _valid_answers:
                score += 1
                _debug_answered.discard(question)
        score = score / len(qs)
        return score


    results = df[_questions].apply(_score_row, axis=1)

    # if endline:
    #     import pdb; pdb.set_trace()

    return results
