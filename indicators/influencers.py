import pandas as pd
import datetime as dt

def load(file_path):
    df = pd.read_spss(file_path)

    regions = {
        'Mbeya': 'Mbeya',
        'Songwe': 'Songwe',
        'Pemba (Zanzibar)': 'Zanzibar',
        'Unguja (Zanzibar)': 'Zanzibar',
    }

    df['regions'] = df['Q_5'].map(regions)


    def _age_to_agegroup(age):
        if age < 10:
            return "0-9"
        elif age < 15:
            return "10-14"
        elif age < 20:
            return "15-19"
        else:
            return ">19"

    df['age'] = df['Q_10']
    df['agegroup'] = df['age'].map(_age_to_agegroup)
    df['sex'] = df["Q_20"]
    df['gender_support'] = df['Q_3']
    return df

def indicator_1200a(df):
    """Proportion of community influencers (Local govt officials / Parents / teachers / religious leaders / HCW)
    who demonstrate supportive attitudes towards adolescents’ SRHR and nutrition (disaggregated by support for boys and for girls)

    Numerator: Number of community influencers who demonstrated a supportive attitude.
    Denominator: Total number of community  interviewed.
    """

    filtered_df = df[df["Q_3"] == "Girls"]

    _questions_boys = [
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
    ]

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
    ]
    assert(len(_questions_boys) == 14)
    assert(len(_questions_girls) == 20)
    _valid_answers = {
        'Strongly Agree',
        'Slightly Agree',
    }

    _questions = _questions_boys + _questions_girls + ['Q_3']

    def _score_row(row):
        qs = _questions_boys
        if row['Q_3'] == 'Girls':
            qs = _questions_girls

        score = 0
        for q in qs:
            if row[q] in _valid_answers:
                score += 1
        score = score / len(qs)
        return score


    results = df[_questions].apply(_score_row, axis=1)

    return results
