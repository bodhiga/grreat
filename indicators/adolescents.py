import pandas as pd
import datetime as dt
import functools as functools

def _bloom(df):
    """Apply Bloom's Taxonomy to the dataframe"""

    def _categorise(value):
        if value < 60:
            return "Low"
        elif value < 80:
            return "Moderate"
        else:
            return "High"

    return df.apply(_categorise)

def _count_strings(row, endline):
    """Used with apply on a dataframe. Counts selected values (they are 0.0) if not selected"""
    n = 0
    for _, val in row.items():
        if (isinstance(val, str) and not endline) or val == 1:
            n += 1
    return n

def load(file_path, endline=False):
    def _age_to_agegroup(age):
        if age < 10:
            return "0-9"
        elif age < 15:
            return "10-14"
        elif age < 20:
            return "15-19"
        else:
            return ">19"

    def date_to_age(born, endline=False):
        today = dt.datetime(2022, 8, 12) # Day data collection started # TODO Add date data collection started
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    df = None
    if endline:
        df = pd.read_excel(file_path)
    else:
        df = pd.read_spss(file_path)
    # Collapse Zanzibar into one region
    regions = {
        'Mbeya': 'Mbeya',
        'Songwe': 'Songwe',
        'Pemba (Zanzibar)': 'Zanzibar',
        'Unguja (Zanzibar)': 'Zanzibar',
        'Zanzibar': 'Zanzibar',
    }

    from collections import defaultdict
    _settings_map = defaultdict(lambda: "rural",{
        "Madibira": "mixed",
        "Ruanda": "urban",
        "Ndalambo": "rural",
        "Mawindi": "rural",
        "Itaka": "rural",
        "Isansa": "rural",
        "Itaka": "rural",
        "Ubaruku": "mixed",
        "Myunga": "rural",
        "Isansa": "rural",
        "Ilomba": "urban",
        "Mawindi": "rural",
        "Igamba (pilot)": "rural",
        "Ndalambo": "rural",
        "Isansa": "rural",
        "Madibira": "mixed",
        "Itaka": "rural",
        "Isansa": "rural",
        "Itaka": "rural",
        "Myunga": "rural",
        "Igamba (pilot)": "rural",
        "Itaka": "rural",
        "Ruanda": "urban",
        "Mawindi": "rural",
        "Ruanda": "urban",
        "Mfikiwa": "rural",
        "Kanganini": "rural",
        "Shumba Mijni": "rural",
        "Ngombeni": "urban",
        "Changaweni": "mixed",
        "Vitongoji": "rural",
        "Bumbwini": "rural",
        "Potoa": "rural",
        "Limbani": "urban",
        "Micheweni": "mixed",
        "Donge Majenzu": "rural",
        "Kilindi": "rural",
        "Mapofu": "rural",
        "Mkwajuni Sekondari": "rural",
        "Chwale": "rural",
        "Mbuyuni": "urban",
        "Kilombero": "rural",
        "Ng'ambwa Secondary": "mixed",
        "Chutama (pilot)": "rural",
        "Mtowapwani (pilot)": "rural",
        "Kidoti": "rural",
        "Kivunge": "rural",
        "Gombani": "mixed",
        "Kipangani": "urban",
    })

    df['regions'] = df[('Q_3' if not endline else '1. Mkoa')].map(regions)

    _sexmap = ({'Male': 'Male',
               'Female': 'Female'} if not endline else {'Mke': 'Female', 'Mme': 'Male'})
    df['sex'] = df[('Q_21' if not endline else '14. Jinsia')].map(_sexmap)

    df['age'] = df[('Q_8' if not endline else '5. Tarehe ya kuzaliwa')].map(lambda x: date_to_age(x, endline))

    df['schooling'] = df[('Q_9' if not endline else '6. Bado unasoma')] # TODO map here
    df['occupation'] = df['Q_15' if not endline else '10. Unajishughulisha na nini?'] # TODO map here
    df['education'] = df['Q_11' if not endline else '8. Kama jibu ni Hapana, kiwango chako cha elimu cha juu ni kipi?'] # TODO map here
    df['setting'] = df['Q_5' if not endline else '3. Kata unayoishi'].map(_settings_map)

    # Remove everyone whose age is not provided
    # df = df[df['age'] > 0]

    df['agegroup'] = df['age'].map(_age_to_agegroup)

    return df

def indicator_1000_categories(df, endline):
    """Average score of the Girls Empowerment Index

    Following baseline methodology, respondents will be scored on a scale of 1 to 50;
    the percentage of points scored equates to the empowerment level, within three categories."""

    def _education_score(row, endline):
            # BUG!!! If you're not a student you get zero points here
            # gen grl_ecoemp6=1 if QN6=="Ndiyo" | QN8=="Nimemaliza elimu ya msingi"| QN8=="Nimemaliza kidato cha nne" | QN8a=="HAKUMALIZA  ELIMU  YA  MSINGI" | QN8a=="SIJAMALIZA ELIMU YA MSINGI"
        results = 0
        _answers = { # TODO Which question does this correspond to?
                "Primary school completed",
                "A-Level completed",
                "Primary school completed",
                "O-Level completed",
                "A-Level completed",
                "Primary school completed + vocational training completed",
                "O-Level completed + vocational training completed",
                "A-Level completed + vocational training completed",
                "University",
        }
        _endline_answers = {
            "Nimemaliza elimu ya msingi",
            "Nimemaliza kidato cha nne",
            "Nimemaliza kidato cha sita",
            "Mafunzo ya ufundi",
            "Nimemaliza elimu ya msingi na mafunzo ya ufundi",
            "Nimemaliza kidato cha nne na mafunzo ya ufundi",
            "Nimemaliza kidato cha sita na mafunzo ya ufundi",
            "Chuo kikuu",
            "Mafunzo mengine kama ujasiriamali, kutengeneza bidhaa n.k",
        }
        if row[("Q_9" if not endline else "6. Bado unasoma")] == ("No" if not endline else "Hapana") or row[("Q_11" if not endline else "9. Ungependa usome mpaka ngazi gani ya elimu?")] in (_answers if not endline else _endline_answers):
            results = 1
        return results

    _empowerment = {
        "economic_empowerment": {
            # gen grl_ecoemp1=1 if QN9b==1 | QN9b==2 |
            # QN9b==3 | QN9b==5 | QN9b==6 | QN9b==7
            # replace grl_ecoemp1=0 if grl_ecoemp1==.
            # lab var grl_ecoemp1 "QN9. What level would you wish to attain? / what level would you have wished to attain?"
            # lab define grl_ecoemp1 0"Not empowered" 1"Empowered"
            # lab values grl_ecoemp1 grl_ecoemp1
            # tab grl_ecoemp1
            "Q_13": {
                'At least complete primary school;',
                "Higher education MSc's and PhD's",
                'Higher education 1st degree;',
                'A level',
                'Completing O level',
                # 'Not completing primary school;', # BUG should be secondary school?
                },
            # gen grl_ecoemp2=1 if QN18=="Ndiyo"
            # replace grl_ecoemp2=0 if QN18=="Hapana" | QN18=="Sijui/Sina uhakika"
            # lab var  grl_ecoemp2 "QN18.Do you wish to save money in the future?"
            # lab define grl_ecoemp2 0"Not empowered" 1"Empowered"
            # lab values grl_ecoemp2 grl_ecoemp2
            # tab grl_ecoemp2
            "Q_25": {
                'Yes',
            },
            # destring QN20a QN20b QN20c QN20d QN20e QN20f QN20g,replace
            # gen grl_ecoemp3=1 if QN20a==1 | QN20b==1 |
            # QN20c==1 | QN20d==1 | QN20e==1 | QN20f==1 | QN20g==1
            # replace grl_ecoemp3=0 if grl_ecoemp3==. & QN14b==1
            # lab var  grl_ecoemp3 "QQN20. Have you ever saved money in any of these or anywhere else? (circle all that applies, probe for all responses)"
            # lab define grl_ecoemp3 0"Not empowered" 1"Empowered"
            # lab values grl_ecoemp3 grl_ecoemp3
            # tab grl_ecoemp3
            "Q_28": # A_Q_28_1 etc
                [
                    'A_Q_28_1',
                    'A_Q_28_3', # Vikoba, Saccosec
                    'A_Q_28_2', # Mpesa
                    'A_Q_28_5', # table banks
                    'A_Q_28_4', # piggy banks
                    'A_Q_28_6', # Parents/sibling/partners
                    #  7, # No # BUG  # NOTE I've removed no from here
                 ],
            # destring QN23a QN23b QN23c QN23d QN23e, replace
            # gen grl_ecoemp4=1 if QN23a==1 | QN23b==1 | QN23c==1 | QN23d==1 | QN23e==1
            # replace grl_ecoemp4=0 if grl_ecoemp4==. & QN14b==1
            # lab var  grl_ecoemp4 "QN23. ave you ever borrowed money from any of these or anywhere else? (circle all that applies, probe for all responses)"
            # lab define grl_ecoemp4 0"Not empowered" 1"Empowered"
            # lab values grl_ecoemp4 grl_ecoemp4
            # tab grl_ecoemp4
            "Q_33": [
                'A_Q_33_1', # bank account
                'A_Q_33_3', # Vikoba, Saccosec
                'A_Q_33_2', # Mpesa
                'A_Q_33_5', # table banks
                'A_Q_33_4', # piggy banks
            ],
            # gen grl_ecoemp5=0 if QN25=="Mkulima"
            # replace grl_ecoemp5=1 if grl_ecoemp5==. & QN14b==1
            # lab var grl_ecoemp5 "QN25. What do you want to be/to do when you grow up?  "
            # lab define grl_ecoemp5 0"Not empowered" 1"Empowered"
            # lab values grl_ecoemp5 grl_ecoemp5
            # tab grl_ecoemp5
            "Q_36": { # everything except farmer
                'Accountant',
                'Businessman/woman',
                'Doctor/Nurse',
                'Engineer/Architect',
                'Lawyer',
                'Others, specify',
                'Politician',
                'Soldier/Police',
                'Teacher'
            },
            "education_1000": _education_score,
            # BUG!!! If you're not a student you get zero points here
            # gen grl_ecoemp6=1 if QN6=="Ndiyo" | QN8=="Nimemaliza elimu ya msingi"| QN8=="Nimemaliza kidato cha nne" | QN8a=="HAKUMALIZA  ELIMU  YA  MSINGI" | QN8a=="SIJAMALIZA ELIMU YA MSINGI"
            # replace grl_ecoemp6=0 if QN8a=="SIJASOMA KABISA"
            # lab var grl_ecoemp6 "Educated (acquired formal or informal education/technical skills)"
            # lab define grl_ecoemp6 0"Not empowered" 1"Empowered"
            # lab values grl_ecoemp6 grl_ecoemp6
            # tab grl_ecoemp6
        },
        "political_participation": {
            # gen grl_leademp1=1 if QN68=="Nakubali kabisa" | QN68=="Nakubali kiasi"
            # replace grl_leademp1=0 if grl_leademp1==.
            # lab var grl_leademp1 "QN68. Girls/women can be good leaders at school, community, family etc or participate in leadership groups or community/school committees just like men "
            # lab define grl_leademp1 0"Not empowered" 1"Empowered"
            # lab values grl_leademp1 grl_leademp1
            # tab grl_leademp1
            "Q_86": { # BUG NOTE There is a question missing
                'Strongly agree',
                'Partly agree',
            },
                # gen grl_leademp2=1 if QN69=="Sikubali kabisa" | QN69=="Sikubali kiasi"
            # replace grl_leademp2=0 if grl_leademp2==.
            # lab var grl_leademp2 "QN69.Boys/men in schools, family, community and at country level, tends to be better leaders than girls/women."
            # lab define grl_leademp2 0"Not empowered" 1"Empowered"
            # lab values grl_leademp2 grl_leademp2
            # tab grl_leademp2
            "Q_84": {
                'Partly disagree',
                'Strongly disagree',
            },
            # gen grl_leademp3=1 if QN71=="Nakubali kabisa" | QN71=="Nakubali kiasi"
            # replace grl_leademp3=0 if grl_leademp3==.
            # lab var grl_leademp3 "QN71. Girls/woman have the right to participate in politics (selected as political leaders, voting etc) just like boys/men."
            # lab define grl_leademp3 0"Not empowered" 1"Empowered"
            # lab values grl_leademp3 grl_leademp3
            # tab grl_leademp3
            "Q_86": {
                'Strongly agree',
                'Partly agree',
            },
            # gen grl_leademp4=1 if QN72=="Nakubali kabisa" | QN72=="Nakubali kiasi"
            # replace grl_leademp4=0 if grl_leademp4==.
            # lab var grl_leademp4 "QN72. I feel that I am involved in the decisions that affect me, For example, I had an opportunity to express my opinion or preference for the school/community/sports club/social clubs/ Saccos I attend, and my opinion was listened to, and heard. "
            # lab define grl_leademp4 0"Not empowered" 1"Empowered"
            # lab values grl_leademp4 grl_leademp4
            # tab grl_leademp4
            "Q_87": {
                'Strongly agree',
                'Partly agree',
            },
            # gen grl_leademp5=1 if QN73=="Nakubali kabisa" | QN73=="Nakubali kiasi"
            # replace grl_leademp5=0 if grl_leademp5==.
            # lab var grl_leademp5 "QN73. I usually/sometimes participate in household/school/community discussions "
            # lab define grl_leademp5 0"Not empowered" 1"Empowered"
            # lab values grl_leademp5 grl_leademp5
            # tab grl_leademp5
            "Q_88": {
                'Strongly agree',
                'Partly agree',
            },
            # gen grl_leademp6=1 if QN74=="Nakubali kabisa" | QN74=="Nakubali kiasi"
            # replace grl_leademp6=0 if grl_leademp6==.
            # lab var grl_leademp6 "QN74. I usually/sometimes talk to parents, partners, teachers, community etc and sometimes influence decisions"
            # lab define grl_leademp6 0"Not empowered" 1"Empowered"
            # lab values grl_leademp6 grl_leademp6
            # tab grl_leademp6
            "Q_89": {
                'Strongly agree',
                'Partly agree',
            },
            # gen grl_leademp7=1 if QN76=="Nakubali kabisa" | QN76=="Nakubali kiasi"
            # replace grl_leademp7=0 if grl_leademp7==.
            # lab var grl_leademp7 "QN76.I have high aspirations to be a leader such as a class monitor or a head girl or community leader or political leader in future?"
            # lab define grl_leademp7 0"Not empowered" 1"Empowered"
            # lab values grl_leademp7 grl_leademp7
            # tab grl_leademp7
            "Q_91": {
                'Strongly agree',
                'Partly agree',
            },
            # gen grl_leademp8=1 if QN77=="Ndiyo"
            # replace grl_leademp8=0 if grl_leademp8==.
            # lab var grl_leademp8 "QN77. Do you know/have access to any programs to empower girls/boys to be a leader or acquire leadership skills?"
            # lab define grl_leademp8 0"Not empowered" 1"Empowered"
            # lab values grl_leademp8 grl_leademp8
            # tab grl_leademp8
            "Q_92": { 'Yes' }, # yes
            # gen grl_leademp9=1 if QN81=="Ndiyo"
            # replace grl_leademp9=0 if grl_leademp9==.
            # lab var grl_leademp9 "QN81.Have you ever voted to select a leader (such as in your family, school or community)"
            # lab define grl_leademp9 0"Not empowered" 1"Empowered"
            # lab values grl_leademp9 grl_leademp9
            # tab grl_leademp9
            "Q_96": { 'Yes' }, # yes
            # gen grl_leademp10=1 if QN82=="Ndiyo"
            # replace grl_leademp10=0 if grl_leademp10==.
            # lab var grl_leademp10 "QN82. In the past 12 months have you voted to select a leader (such as in your family, school or community)"
            # lab define grl_leademp10 0"Not empowered" 1"Empowered"
            # lab values grl_leademp10 grl_leademp10
            # tab grl_leademp10
            "Q_97": { 'Yes' }, # yes
            # gen grl_leademp11=1 if QN84=="Ndiyo"
            # replace grl_leademp11=0 if QN84=="Hapana"
            # lab var grl_leademp11 "QN84. Do you have any ideas on how adolescents could get more involved in planning, designing and implementing good quality health care in this community?"
            # lab define grl_leademp11 0"Not empowered" 1"Empowered"
            # lab values grl_leademp11 grl_leademp11
            # tab grl_leademp11
            "Q_99": { 'Yes' }, # yes
        },
        "violence_against_women": {
            # ****DOMAIN NO 3: Disagree on violence against girls and women
            # destring QN47h QN47j,replace
            # gen grl_vioemp1=1 if QN47h==1 | QN47j==1
            # replace grl_vioemp1=0 if grl_vioemp1==. & QN14b==1
            # lab var grl_vioemp1 "QN47. Where will you/your friends report in case of violence against girls in future?"
            # lab define grl_vioemp1 0"Not empowered" 1"Empowered"
            # lab values grl_vioemp1 grl_vioemp1
            # tab grl_vioemp1
            "Q_61": [
                'A_Q_61_5', # police
                'A_Q_61_8', # child helpline
            ],
            # gen grl_vioemp2=1 if QN86=="Sikubali kabisa" | QN86=="Sikubali kiasi;"
            # replace grl_vioemp2=0 if grl_vioemp2==.
            # lab var grl_vioemp2 "QN86.It is acceptable for a boy/man to humiliate, threaten or insult a girl if she disobeys him"
            # lab define grl_vioemp2 0"Not empowered" 1"Empowered"
            # lab values grl_vioemp2 grl_vioemp2
            # tab grl_vioemp2
            "Q_102": {
                'Partly disagree',
                'Strongly disagree',
            },
            # gen grl_vioemp3=1 if QN87=="Sikubali kabisa" | QN87=="Sikubali kiasi;"
            # replace grl_vioemp3=0 if grl_vioemp3==.
            # lab var grl_vioemp3 "QN87.It is acceptable for a boy/man to have a possessive behavior (such as controlling decisions and activities) over his girlfriend/wife just because she is his girlfriend/wife"
            # lab define grl_vioemp3 0"Not empowered" 1"Empowered"
            # lab values grl_vioemp3 grl_vioemp3
            # tab grl_vioemp3
            "Q_103": {
                'Partly disagree',
                'Strongly disagree',
            },
            # gen grl_vioemp4=1 if QN88=="Sikubali kabisa" | QN88=="Sikubali kiasi;"
            # replace grl_vioemp4=0 if grl_vioemp4==.
            # lab var grl_vioemp4 "QN88.It is acceptable for a boy/man to control his girlfriend/wife movements just because she is his girlfriend/wife"
            # lab define grl_vioemp4 0"Not empowered" 1"Empowered"
            # lab values grl_vioemp4 grl_vioemp4
            # tab grl_vioemp4
            "Q_103": {
                'Partly disagree',
                'Strongly disagree',
            },
            # gen grl_vioemp5=1 if QN89=="Sikubali kabisa" | QN89=="Sikubali kiasi;"
            # replace grl_vioemp5=0 if grl_vioemp5==.
            # lab var grl_vioemp5 "QQN89.It is acceptable for a boy/man to force someone to perform sexual acts including kissing, touching, sex against their will"
            # lab define grl_vioemp5 0"Not empowered" 1"Empowered"
            # lab values grl_vioemp5 grl_vioemp5
            # tab grl_vioemp5
            "Q_105": {
                'Partly disagree',
                'Strongly disagree',
            },
            # gen grl_vioemp6=1 if QN90=="Sikubali kabisa" | QN90=="Sikubali kiasi;"
            # replace grl_vioemp6=0 if grl_vioemp6==.
            # lab var grl_vioemp6 "QN90.It is acceptable for a boy/man to make sexual comments that make someone feel humiliated or uncomfortable"
            # lab define grl_vioemp6 0"Not empowered" 1"Empowered"
            # lab values grl_vioemp6 grl_vioemp6
            # tab grl_vioemp6
            "Q_106": {
                'Partly disagree',
                'Strongly disagree',
            },
            # gen grl_ecoemp7=1 if QN91=="Sikubali kabisa" | QN91=="Sikubali kiasi;"
            # replace grl_ecoemp7=-0 if grl_ecoemp7==.
            # lab var grl_ecoemp7 "QN91.It is acceptable for a boy/man to have a complete control over his girlfriend’s/wife money and other economic resources"
            # lab define grl_ecoemp7 0"Not empowered" 1"Empowered"
            # lab values grl_ecoemp7 grl_ecoemp7
            # tab grl_ecoemp7 # NOTE This oen was baked into violence though named as if economic. I double checked it's correct
            "Q_106": {
                'Partly disagree',
                'Strongly disagree',
            },
        },
        "self_confidence": {
            # ****DOMAIN NO 4:Self-confidence and esteem
            # gen grl_selfconfemp1=1 if QN27=="Ndiyo"
            # replace grl_selfconfemp1=0 if QN27=="Hapana" | QN27=="Sijui/sina uhakika"
            # lab var grl_selfconfemp1 "QN27.Are you a member of any debate club/school club/community group and have you ever involved in a debate at school or speak in the community meetings, church, family meetings etc?"
            # lab define grl_selfconfemp1 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp1 grl_selfconfemp1
            # tab grl_selfconfemp1
            "Q_39": { 'Yes' }, # yes
            # gen grl_selfconfemp2=1 if QN28=="Ndiyo"
            # replace grl_selfconfemp2=0 if QN28=="Hapana" | QN28=="Sijui/sina uhakika"
            # lab var grl_selfconfemp2 "QN28.Have you ever been given an opportunity to voice your opinion in a family or community meeting?"
            # lab define grl_selfconfemp2 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp2 grl_selfconfemp2
            # tab grl_selfconfemp2
            "Q_40": { 'Yes' }, # yes
            # gen grl_selfconfemp3=1 if QN48=="Nakubali kiasi" | QN48=="Nakubali sana"
            # replace grl_selfconfemp3=0 if QN48=="Sikubali kabisa" | QN48=="Sikubali kiasi"
            # lab var grl_selfconfemp3 "QN48 On the whole, I am satisfied with myself"
            # lab define grl_selfconfemp3 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp3 grl_selfconfemp3
            # tab grl_selfconfemp3
            "Q_63": {
                'Strongly agree',
                'Partly agree',
            },
            # gen grl_selfconfemp4=1  if QN49=="Sikubali kabisa" | QN49=="Sikubali kiasi"
            # replace grl_selfconfemp4=0  if QN49=="Nakubali kiasi" | QN49=="Nakubali sana"
            # lab var grl_selfconfemp4 "QN49.At times I think I am no good at all"
            # lab define grl_selfconfemp4 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp4 grl_selfconfemp4
            # tab grl_selfconfemp4
            "Q_64": {
                'Partly disagree',
                'Strongly disagree',
            },
            # gen grl_selfconfemp5=1 if QN50=="Nakubali kiasi" | QN50=="Nakubali sana"
            # replace grl_selfconfemp5=0 if QN50=="Sikubali kabisa" | QN50=="Sikubali kiasi"
            # lab var grl_selfconfemp5 "QN50.I feel that I have a number of good qualities"
            # lab define grl_selfconfemp5 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp5 grl_selfconfemp5
            # tab grl_selfconfemp5
            "Q_65": {
                'Strongly agree',
                'Partly agree',
            },
            # gen grl_selfconfemp6=1 if QN51=="Nakubali kiasi" | QN51=="Nakubali sana"
            # replace grl_selfconfemp6=0 if QN51=="Sikubali kabisa" | QN51=="Sikubali kiasi"
            # lab var grl_selfconfemp6 "QN51.I am able to do things as well as most other people "
            # lab define grl_selfconfemp6 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp6 grl_selfconfemp6
            # tab grl_selfconfemp6
            "Q_66": {
                'Strongly agree',
                'Partly agree',
            },
            # gen grl_selfconfemp7=1  if QN52=="Sikubali kabisa" | QN52=="Sikubali kiasi"
            # replace grl_selfconfemp7=0  if QN52=="Nakubali kiasi" | QN52=="Nakubali sana"
            # lab var grl_selfconfemp7 "QN52.I feel I don’t have much to be proud of "
            # lab define grl_selfconfemp7 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp7 grl_selfconfemp7
            # tab grl_selfconfemp7
            "Q_67": {
                'Partly disagree',
                'Strongly disagree',
            },
            # gen grl_selfconfemp8=1  if QN53=="Nakubali kiasi" | QN53=="Nakubali sana"
            # replace grl_selfconfemp8=0 if QN53=="Sikubali kabisa" | QN53=="Sikubali kiasi"
            # lab var grl_selfconfemp8 "QN53.I feel that I am worth person at least like others"
            # lab define grl_selfconfemp8 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp8 grl_selfconfemp8
            # tab grl_selfconfemp8
            "Q_68": {
                'Strongly agree',
                'Partly agree',
            },
            # gen grl_selfconfemp9=1  if QN54=="Nakubali kiasi" | QN54=="Nakubali sana"
            # replace grl_selfconfemp9=0 if QN54=="Sikubali kabisa" | QN54=="Sikubali kiasi"
            # lab var grl_selfconfemp9 "QN54.I wish I was more respected"
            # lab define grl_selfconfemp9 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp9 grl_selfconfemp9
            # tab grl_selfconfemp9
            "Q_69": { # BUG! NOTE I've swapped these backwards
                'Strongly disagree',
                'Partly disagree',
            },
            # gen grl_selfconfemp10=1  if QN55=="Sikubali kabisa" | QN55=="Sikubali kiasi"
            # replace grl_selfconfemp10=0  if QN55=="Nakubali kiasi" | QN55=="Nakubali sana"
            # lab var grl_selfconfemp10 "QN55.All in all, I am inclined to feel that I am a failure"
            # lab define grl_selfconfemp10 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp10 grl_selfconfemp10
            # tab grl_selfconfemp10
            "Q_70": {
                'Partly disagree',
                'Strongly disagree',
            },
            # gen grl_selfconfemp20=1  if QN56=="Nakubali kiasi" | QN56=="Nakubali sana"
            # replace grl_selfconfemp20=0  if QN56=="Sikubali kabisa" | QN56=="Sikubali kiasi"
            # lab var grl_selfconfemp20 "QN56.I perceive myself positively"
            # lab define grl_selfconfemp20 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp20 grl_selfconfemp20
            # tab grl_selfconfemp20
            "Q_71": {
                'Strongly agree',
                'Partly agree',
            },
            # gen grl_selfconfemp11=1 if QN30a=="Nakubali kabisa" | QN30a=="Nakubali kiasi"
            # replace grl_selfconfemp11=0 if QN30a=="Sikubali Kabisa" | QN30a=="Sikubali kiasi" | QN30a=="Sitaki kujibu"
            # lab var grl_selfconfemp11 "QN30a.Alcohol is not good for people under 18 years"
            # lab define grl_selfconfemp11 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp11 grl_selfconfemp11
            # tab grl_selfconfemp11
            "T_Q_42_1": {
                'Strongly agree',
                'Partly agree',
            },
            # gen grl_selfconfemp12=1 if QN30b=="Nakubali kabisa" | QN30b=="Nakubali kiasi"
            # replace grl_selfconfemp12=0 if QN30b=="Sikubali Kabisa" | QN30b=="Sikubali kiasi" | QN30b=="Sitaki kujibu"
            # lab var grl_selfconfemp12 "QN30b.Too much alcohol intake is not good for any person regardless of his/her age"
            # lab define grl_selfconfemp12 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp12 grl_selfconfemp12
            # tab grl_selfconfemp12
            "T_Q_42_2": {
                'Strongly agree',
                'Partly agree',
            },
            # gen grl_selfconfemp13=1 if QN30c=="Nakubali kabisa" | QN30c=="Nakubali kiasi"
            # replace grl_selfconfemp13=0 if QN30c=="Sikubali Kabisa" | QN30c=="Sikubali kiasi" | QN30c=="Sitaki kujibu"
            # lab var grl_selfconfemp13 "QN30c.Cigarette smoking and use of drugs such as khat (Mirungi), marijuana (bangi), heroin or cocaine is not good for any person regardless of his/her age"
            # lab define grl_selfconfemp13 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp13 grl_selfconfemp13
            # tab grl_selfconfemp13
            "T_Q_42_3": {
                'Strongly agree',
                'Partly agree',
            },
            # gen grl_selfconfemp14=1 if QN31=="Hapana"
            # replace grl_selfconfemp14=0 if QN31=="Ndiyo"
            # lab var grl_selfconfemp14 "QN31. Have you ever consumed alcohol?"
            # lab define grl_selfconfemp14 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp14 grl_selfconfemp14
            # tab grl_selfconfemp14
            "Q_43": {
                'No',
            },
            # gen grl_selfconfemp15=1 if QN33=="Hapana" | QN33=="Sina uhakika/Sijui"
            # replace grl_selfconfemp15=0 if QN33=="Ndiyo"
            # lab var grl_selfconfemp15 "QN33. Do any of your friend/s drink alcohol"
            # lab define grl_selfconfemp15 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp15 grl_selfconfemp15
            # tab grl_selfconfemp15
            "Q_45": {
                'No',
            },
            # gen grl_selfconfemp16=1 if QN34=="Hapana"
            # replace grl_selfconfemp16=0 if QN34=="Ndiyo"
            # lab var grl_selfconfemp16 "QN34. Have you ever smoked cigarette? "
            # lab define grl_selfconfemp16 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp16 grl_selfconfemp16
            # tab grl_selfconfemp16
             "Q_46": {
                 'No',
            },
            # gen grl_selfconfemp17=1 if QN35=="Hapana"
            # replace grl_selfconfemp17=0 if QN35=="Ndiyo"
            # lab var grl_selfconfemp17 "QN35. Have you ever used drugs such as khat, marijuana, cocaine or heroin?"
            # lab define grl_selfconfemp17 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp17 grl_selfconfemp17
            # tab grl_selfconfemp17
            "Q_47": {
                'No',
            },
            # gen grl_selfconfemp18=1 if QN36=="Hapana"
            # replace grl_selfconfemp18=0 if QN36=="Ndiyo" | QN36=="Sijui/Sina uhakika"
            # lab var grl_selfconfemp18 "QN36. Do any of your friend/s smoke or use drugs such as khat, marijuana, heroin or cocaine"
            # lab define grl_selfconfemp18 0"Not empowered" 1"Empowered"
            # lab values grl_selfconfemp18 grl_selfconfemp18
            # tab grl_selfconfemp18
            "Q_48": {
                'No',
            },
        },
        "srhr_nutrition_knowledge": {

            # gen grl_knowemp1=1 if QN106=="Nakubali kabisa" | QN106=="Nakubali kiasi"
            # replace grl_knowemp1=0 if QN106=="Sikubali kabisan" | QN106=="Sikubali kiasi"
            # lab var grl_knowemp1 "QN106.Child marriage for girls (below 18 years) is a harmful culture"
            # lab define grl_knowemp1 0"Not empowered" 1"Empowered"
            # lab values grl_knowemp1 grl_knowemp1
            # tab grl_knowemp1
            "Q_122": {
                'Strongly agree',
                'Partly agree',
            },
            # gen grl_knowemp2=1 if Qn108b>0
            # replace grl_knowemp2=0 if Qn108b==0
            # lab var grl_knowemp2 "QN108.What is the benefit of delayed marriage and first pregnancy to a girl?"
            # lab define grl_knowemp2 0"Not empowered" 1"Empowered"
            # lab values grl_knowemp2 grl_knowemp2
            # tab grl_knowemp2
            "Q_124": [
                'Q_124_O1',
                'Q_124_O2',
                'Q_124_O3',
                'Q_124_O4',
                'Q_124_O5',
                'Q_124_O6',
                'Q_124_O7',
                'Q_124_O8'
            ],
            # gen grl_knowemp3=1 if QN109=="Kituo cha Afya"
            # replace grl_knowemp3=0 if grl_knowemp3==.
            # lab var grl_knowemp3 "QN109.Where can you seek care in case you need services for SRHR (ANC, delivery, post-natal, FP, PACF, cervical cancer screening etc) (circle all that applies and explain to the adolescent in simple terms what these services mean)"
            # lab define grl_knowemp3 0"Not empowered" 1"Empowered"
            # lab values grl_knowemp3 grl_knowemp3
            # tab grl_knowemp3
            "Q_125": ['Q_125_O1'], # health centre
            # gen grl_knowemp4=1 if QN120=="Nakubaliana kabisa" | QN120=="Nakubaliana kiasi"
            # replace grl_knowemp4=0 if QN120=="Sikubaliani kabisa" | QN120=="Sikubaliani kiasi"
            # lab var grl_knowemp4 "QN120. Good nutrition is very important for girls from the time they are born to help them have healthy babies in future"
            # lab define grl_knowemp4 0"Not empowered" 1"Empowered"
            # lab values grl_knowemp4 grl_knowemp4
            # tab grl_knowemp4
            "Q_143": {
                'Strongly agree',
                'Partly agree',
            },
            # gen grl_knowemp5=1 if QN126b=="Ndiyo"
            # replace grl_knowemp5=0 if grl_knowemp5==.
            # lab var grl_knowemp5 "QN126b.A person can reduce risk for contracting HIV by using condom"
            # lab define grl_knowemp5 0"Not empowered" 1"Empowered"
            # lab values grl_knowemp5 grl_knowemp5
            # tab grl_knowemp5
            "T_Q_151_2": {
                'Yes',
            },
            # gen grl_knowemp6=1 if QN126c=="Ndiyo"
            # replace grl_knowemp6=0 if grl_knowemp6==.
            # lab var grl_knowemp6 "QN126c.A healthy looking person can have HIV as well"
            # lab define grl_knowemp6 0"Not empowered" 1"Empowered"
            # lab values grl_knowemp6 grl_knowemp6
            # tab grl_knowemp6
            "T_Q_151_3": {
                'Yes',
            },
            # gen grl_knowemp7=1 if QN126d=="Hapana"
            # replace grl_knowemp7=0 if grl_knowemp7==.
            # lab var grl_knowemp7 "QN126d.Mosquito bite can't transmit HIV"
            # lab define grl_knowemp7 0"Not empowered" 1"Empowered"
            # lab values grl_knowemp7 grl_knowemp7
            # tab grl_knowemp7
            "T_Q_151_4": {
                'No',
            },

            # gen grl_knowemp8=1 if QN126e=="Hapana"
            # replace grl_knowemp8=0 if grl_knowemp8==.
            # lab var grl_knowemp8 "QN126e.Eating together with HIV positive person does not transmit HIV"
            # lab define grl_knowemp8 0"Not empowered" 1"Empowered"
            # lab values grl_knowemp8 grl_knowemp8
            # tab grl_knowemp8
            "T_Q_151_5": {
                'No',
            },
        }

    }

    _endline_empowerment = {
        "economic_empowerment": {
            "9. Ungependa usome mpaka ngazi gani ya elimu?": {
                'Angalau nimalize elimu ya msingi;',
                "Elimu ya juu (Shahada ya uzamili na PhD's);",
                'Elimu ya juu (Shahada);',
                'Nimalize kidato cha nne',
                'Kidato cha sita',
                # 'Nisimalize elimu ya msingi;', # BUG should be secondary school?
                },
            "18. Je! Ungetaka kuweka akiba katika siku zijazo?": { # TODO BUG
                'Ndio',
            },
            "20. Umeshawahi kuweka akiba ya pesa kupitia njia hizi au mahali pengine popote?": # A_Q_28_1 etc
                {
                    'Akaunti ya benki',#Column BJ, DENOTED AS 0 FOR NO and 1 for YES
                    'Mitandao ya simu (Airtel money, Tigopesa ,Mpesa)', #Column BK
                    'Vikoba Saccos nk', #Column BL
                    'Vibubu', # table banks, Column BM
                    'vikundi vidogo', # piggy banks, Column BN
                    'Kwa wazazi wangu / ndugu / marafiki / msiri wangu', # Parents/sibling/partners Column BO
                    #  7, # No # BUG  # NOTE I've removed no from here
                 },
            "23. Je! Umewahi kukopa pesa kutoka kwa makundi haya au mahali pengine popote?": [
                '23. Je! Umewahi kukopa pesa kutoka kwa makundi haya au mahali pengine popote?/Benki', # Column CN- bank account
                '23. Je! Umewahi kukopa pesa kutoka kwa makundi haya au mahali pengine popote?/Mitandao ya simu ( Airtel fedha, Tigopesa , Mpesa nk) ', # Mpesa Column CO
                '23. Je! Umewahi kukopa pesa kutoka kwa makundi haya au mahali pengine popote?/Vikoba, Saccos nk ', # Column CP
                '23. Je! Umewahi kukopa pesa kutoka kwa makundi haya au mahali pengine popote?/Vibubu', # Column CQ
                '23. Je! Umewahi kukopa pesa kutoka kwa makundi haya au mahali pengine popote?/Makundi / vikundi vidogo', # Column CR
                # 'Makundi / vikundi vidogo', # Column CR
            ],
            "25. Je, Unataka kuwa nani / kufanya nini ukiwa mkubwa?": { # everything except farmer
                'Accountant',
                'Mfanyabiashara',
                'Daktari/Nurse',
                'Engineer/Architect',
                'Mwanasheria ',
                'Nyingine',
                'Politician',
                'Mwanajeshi/Askari',
                'Mwalimu'
            },
            "education_1000": _education_score,
            # BUG!!! If you're not a student you get zero points here
        },
        "political_participation": {
            "68. Wasichana/ wanawake wanaweza kuwa viongozi wazuri mashuleni, kwenye jamii, familia n.k au washiriki katika uongozi wa kamati za vikundi au jamii/ shule kama vile wanaume": { # BUG NOTE There is a question missing
                'Nakubali kabisa',
                'Nakubali kiasi',
            },
            "69. Wavulana/wanaume mashuleni, kwenye familia /jamii na ngazi ya nchi huwa ni viongozi wazuri kuliko wasichana/ wanawake": {
                'Nakubali kabisa',
                'Nakubali kiasi',
            },
            "71. Wasichana/ wanawake wanahaki ya kushiriki katika siasa.( wachaguliwe kama viongozi wa kisiasa, wapiga kura n.k) kama wavulana/ wanaume": {
                'Nakubali kabisa',
                'Nakubali kiasi',
            },
            "72. Ninahisi kwamba nimehusishwa katika utoaji wa maamuzi utakaoniathiri mimi. Mfano nilikuwa na fursa ya kuelezea maoni au mapenedekezo kwenye shule / jamii/vilabu vya michezo/ social clubs/Saccos nilizohudhuria na maoni yangu yalisikilizwa na kusikika.": {
                'Nakubali kabisa',
                'Nakubali kiasi',
            },
            "73. Kwa kawaida / mara nyingine ninashiriki katika mazungumzo ya kaya / shuleni/ au kwenye jamii": {
                'Nakubali kabisa',
                'Nakubali kiasi',
            },
            "74. Kwa kawaida au mara nyingine naongea na wazazi, washirika, waalimu, jamii n.k na mara nyingine ninahimiza katika utoaji wa maamuzi.": {
                'Nakubali kabisa',
                'Nakubali kiasi',
            },
            "76. Nina shauku kubwa ya kuwa kiongozi baadae kama vile kiongozi wa darasa, dada/kaka mkuu wa shule, kiongozi wa jamii au kiongozi wa siasa": {
                'Nakubali kabisa',
                'Nakubali kiasi',
            },
            "77. Je unafahamu/unapata nafasi katika mpango wowote wa kuwawezesha wasichana/wavulana kuwa viongozi au kupata mbinu za uongozi": { 'Ndiyo' }, # yes
            "81. Ulishawahi kupiga kura kuchagua kiongozi (kama Vile kwenye familia, shuleni au kwenye jamii?)": { 'Ndiyo' }, # yes
            "82. Katika miezi 12 iliyopita ulishawahi kupiga kura ya kumchagua kiongozi (kama vile kwenye familia yako, shulemi au kweney jamii)": { 'Ndiyo' }, # yes
            "84. Je una mawazo yoyote kuhusu namna gani vijana wanaweza kuhusishwa kupanga, kuandaa na kutekeleza huduma bora ya afya katika jamii": { 'Ndiyo' }, # yes
        },
        "violence_against_women": {
            "47. Ni wapi wewe au rafiki zako mtatoa taarifa za unyanyasaji dhidi ya wasichana": [ # TODO check if 1 or "1"
                '47. Ni wapi wewe au rafiki zako mtatoa taarifa za unyanyasaji dhidi ya wasichana/Polisi', # police, Column EN with 1 being Yes, Question 47. Ni wapi wewe au rafiki zako mtatoa taarifa za unyanyasaji dhidi ya wasichana/Polisi
                '47. Ni wapi wewe au rafiki zako mtatoa taarifa za unyanyasaji dhidi ya wasichana/Mstari wa kusaidia watoto', # child helpline, Comumn EQ wih 1 being Yes, Question 47. Ni wapi wewe au rafiki zako mtatoa taarifa za unyanyasaji dhidi ya wasichana/Mstari wa kusaidia watoto
            ],
            "86. Inakubalika kwa mvulana / mwanaume kumdhalilisha, kumtishia au kumtukana msichana/mwanamke asiyemtii?": {
                'Sikubali kiasi', # Partly disagree
                'Sikubali kabisa', # Strongly disagree
            },
            "87. Inakubalika kwa mvulana/ mwanaume kuwa na tabia za umiliki ( kudhibiti maamuzi na shughuli za rafiki wa kike / mke sababu tu ni rafiki yake wa kike au mke wake)": {
                'Sikubali kiasi',
                'Sikubali kabisa',
            },
            "88. Inakubalika Kwa mvulana / mwanaume kudhibiti mienendo ya rafiki wa kike / mke kwa sababu tu ni Rafiki yake wa kike au mke wake": {
                'Sikubali kiasi',
                'Sikubali kabisa',
            },
            "89. Inakubalika kwa mvulana / mwanaume kulazimisha mtu kubusiana, kushikana , Kujamiiana bila ridhaa yake": {
                'Sikubali kiasi',
                'Sikubali kabisa',
            },
            "90. Inakubalika kwa mvulana / mwanaume kutoa maneno kwa msichana/mwanamke ya kumfanya adhalilike kijinsia au asijiskie vizuri": {
                'Sikubali kiasi',
                'Sikubali kabisa',
            },
            "91. Inakubalika kwa mvulana/ mwanaume kuwa na udhibiti wote kwenye pesa na rasilimali zote za uchumi za rafiki wa kike / mke": {
                'Sikubali kiasi',
                'Sikubali kabisa',
            },
        },
        "self_confidence": {
            "27. Je wewe ni mwanachama wa club yeyote ya majadiliano shuleni, kwenye jamii? Je ulishawahi kufanya majadiliano shuleni au kuzungumza katika mikutano ya kijamii, kanisani/msikitini au mikutano ya kifamilia?": { 'Ndiyo' }, # yes
            "28. Je ulishawahi kupewa fursa ya kutoa maoni yako kwenye familia au mikutano ya kijamii": { 'Ndiyo' }, # yes
            "48. Kwa ujumla, nimeridhika na mimi mwenyewe": {
                'Nakubali sana',
                'Nakubali kiasi',
            },
            "49. Wakati mwingine nadhani mimi sifai hata kidogo": {
                'Sikubali kiasi',
                'Sikubali kabisa',
            },
            "50. Ninahisi nina sifa kadhaa nzuri": {
                'Nakubali sana',
                'Nakubali kiasi',
            },
            "51. Nina uwezo wa kufanya vitu kama watu wengine": {
                'Nakubali sana',
                'Nakubali kiasi',
            },
            "62. Ni jukumu la msichana kuepuka kupata mimba": { # TODO Was Q_67, check it
                'Sikubali kiasi',
                'Sikubali kabisa',
            },
            "53. Ninahisi kuwa mimi ni mtu wa thamani, angalau kwenye usawa mmoja na wengine": {
                'Nakubali sana',
                'Nakubali kiasi',
            },
            "54. Natamani ningeweza kuheshimiwa zaidi.": { # BUG! NOTE I've swapped these backwards
                'Sikubali kabisa',
                'Sikubali kiasi',
            },
            "55. Kwa ujumla, huwa nahisi mimi ni mtu wa kushindwa": {
                'Sikubali kiasi',
                'Sikubali kabisa',
            },
            "56. Nina mtazamo chanya juu yangu": {
                'Nakubali sana',
                'Nakubali kiasi',
            },
            "30 a) Unywaji wa Pombe sio mzuri kwa watu chini ya miaka 18": {
                'Nakubali kabisa',
                'Nakubali  kiasi',
            },
            "30 b) Unywaji wa pombe kupita kiasi ni hatari kwa mtu yeyote bila kujali umri wake": {
                'Nakubali kabisa',
                'Nakubali kiasi',
            },
            "30 c) Uvutaji wa sigara ma matumizi ya madawa kama khat( mirungi), marijuana( bangi), heroin au cocaine ni hatari kwa mtu yeyote bila kujali umri.": {
                'Nakubali kabisa',
                'Nakubali kiasi',
            },
            "31. Je! Umewahi kunywa pombe": {
                'Hapana',
            },
            "33. Je una rafiki/ marafiki anae/ wanao kunywa pombe": {
                'Hapana',
            },
             "34. Ulishawahi kuvuta sigara": {
                 'Hapana',
            },
            "35. Ulishawahi kutumia madawa kama mirungi, bangi, cocaine au heroin?": {
                'Hapana',
            },
            "36. Je una marafiki wanaovuta au kutumia madawa kama mirungi, bangi, heroin au cocaine?": {
                'Hapana',
            },
        },
        "srhr_nutrition_knowledge": {
            "106. Ndoa kwa mtoto mdogo (chini ya miaka 18) ni mila mbaya": {
                'Nakubali kabisa',
                'Nakubali kiasi',
            },
            # TODO Check if '1' or 1
            "108. Kuna faida gani ya kusubiri kuolewa na kupata Mimba ya kwanza kwa msichana mpaka katika muda muafaka?/Inamsaidia kukaa vizuri kusaikolojia na kupunguza uwezekano wa kupata msongo wa mawazo kwa msichana": [
                '108. Kuna faida gani ya kusubiri kuolewa na kupata Mimba ya kwanza kwa msichana mpaka katika muda muafaka?/Ni fursa ya kuongeza elimu kwa msichana',
                '108. Kuna faida gani ya kusubiri kuolewa na kupata Mimba ya kwanza kwa msichana mpaka katika muda muafaka?/Ni fursa ya kuweza kuolewa na mtu anayefaa baadae', # Column IC
                '108. Kuna faida gani ya kusubiri kuolewa na kupata Mimba ya kwanza kwa msichana mpaka katika muda muafaka?/Inazuia msichana asinyanyapaliwe, kukejeliwa na kusemwa na marafiki, familia na jamii kwa ujumla', # Column ID
                '108. Kuna faida gani ya kusubiri kuolewa na kupata Mimba ya kwanza kwa msichana mpaka katika muda muafaka?/Ni fursa kwa msichana kupata mtoto na kuanzisha familia kwa muda unaofaa akiwa ameshakomaa', # Column IE
                '108. Kuna faida gani ya kusubiri kuolewa na kupata Mimba ya kwanza kwa msichana mpaka katika muda muafaka?/Inamkinga msichana dhidi ya matatizo ya uzazi kama vile fistula, kuzaa mtoto mwenye matatizo ya ubongo na kifo kitokanacho na mimba au kujifungua', # Column IF
                '108. Kuna faida gani ya kusubiri kuolewa na kupata Mimba ya kwanza kwa msichana mpaka katika muda muafaka?/Inamsaidia kukaa vizuri kusaikolojia na kupunguza uwezekano wa kupata msongo wa mawazo kwa msichana', # Column IG
                '108. Kuna faida gani ya kusubiri kuolewa na kupata Mimba ya kwanza kwa msichana mpaka katika muda muafaka?/Inawezesha wasichana kupata watoto wenye afya hapo baadae', # Column IH # TODO NOTE CHECK THIS
                '108. Kuna faida gani ya kusubiri kuolewa na kupata Mimba ya kwanza kwa msichana mpaka katika muda muafaka?/Inmuepusha msichana na magonjwa ya zinaa pamoja na HIV, na magonjwa ya saratani', # Column II
            ],
            "109. Ikitokea una uhitaji wa huduma za afya ya uzazi (mfano huduma za mama mjamzito, huduma ya kujifungua, huduma ya baada ya kujifungua, uzazi wa mpango, huduma ya baada ya mimba kuharibika, upimaji wa saratani ya shingo ya kizazi), Utaenda wapi?": [
                '109. Ikitokea una uhitaji wa huduma za afya ya uzazi (mfano huduma za mama mjamzito, huduma ya kujifungua, huduma ya baada ya kujifungua, uzazi wa mpango, huduma ya baada ya mimba kuharibika, upimaji wa saratani ya shingo ya kizazi), Utaenda wapi?/Kituo cha Afya', # health centre (Kituo cha Afya) Column IM
            ],
            "120. Lishe bora ni muhimu kwa wasichana toka muda anazaliwa ili iweze kuwasaidia kupata watoto wenye afya hapo baadaye": {
                'Nakubaliana kabisa',
                'Nakubaliana kiasi',
            },
            "126b. Je mtu anaweza kupunguza hatari ya kupata maambukizi ya VVU kwa kutumia kondomu kila anapo jamiiana?": {
                'Ndio',
            },
            "126c. Je mtu anaweza kupata maambukizi ya VVU kwa kula chakula na mtu mwenye maambukizi?": {
                'Ndio',
            },
            "126d. Je Mtu mwenye afya nzuri anaweza kuwa na VVU": {
                'Hapana',
            },
            "126e.  Je mtu anaweza kupata VVU kwa kung’atwa na mbu?": {
                'Hapana',
            },
        }
    }

    results = pd.DataFrame()

    _debug_answer_is_present_at_least_once = set()

    _items = (_empowerment if not endline else _endline_empowerment).items()
    for empowerment_domain, questions in _items:
        def _domain_score(row):
            """The GEI score for the domain
            Calculated by counting each valid answer as one point,
            then averaging over the number of questions within the domain"""

            score = 0
            for k, v in questions.items():
                if isinstance(v, set): # single choice
                    if row[k] in v:
                        score += 1
                        _debug_answer_is_present_at_least_once.add(k)

                elif isinstance(v, list): # multi choice
                    already_counted = False
                    for subq in v:
                        if isinstance(row[subq], str):
                            _debug_answer_is_present_at_least_once.add(subq)

                            if not already_counted:
                                already_counted = True
                                score += 1
                elif callable(v):
                    score += v(row, endline)

            return 100 * (score / len(questions.keys()))

        results[empowerment_domain] = df.apply(_domain_score, axis=1)

    # _debug_single_choice_questions = [sq for domain in _empowerment.values() for sq in domain if isinstance(domain[sq], set)]
    # _debug_multi_choice_answers = [a for domain in _empowerment.values() for mq in domain.keys() if isinstance(domain[mq], list) for a in domain[mq]]
    # _debug_all_answers = [a for qs in [_debug_single_choice_questions, _debug_multi_choice_answers] for a in qs]
    # print('missing:')
    # _debug_missing = set(_debug_all_answers).difference(_debug_answer_is_present_at_least_once)
    # print(_debug_missing)
    # print(df[_debug_missing].head())
    return results

def indicator_1000(df, endline):
    results = indicator_1000_categories(df, endline)

    # Finally calculate each rows girls empowerment index value by taking the average of the 5 domains
    girls_empowerment_index = results[list(results.keys())].mean(axis=1).apply(lambda x: x / 100)

    return girls_empowerment_index

def _total_acc(row, endline):
    # egen total_acc=rowtotal(QN19b QN19c QN19d QN19e QN19f QN19g)
    # gen total_acc_scores=1 if total_acc>0 & total_acc<=5
    _q = [
        'A_Q_26_1',
        'A_Q_26_2',
        'A_Q_26_3',
        'A_Q_26_4',
        'A_Q_26_5',
        'A_Q_26_98'
    ]
    _q_endline = [
        '19. Unamiliki, ni mwanachama au ungependa kuwa mwanachama wa taasisi yoyote kati ya hizi/Akaunti ya benki', #Bank Column BB
        '19. Unamiliki, ni mwanachama au ungependa kuwa mwanachama wa taasisi yoyote kati ya hizi/Mitandao ya simu (Airtel, Tigopesa, Mpesa nk)',
        '19. Unamiliki, ni mwanachama au ungependa kuwa mwanachama wa taasisi yoyote kati ya hizi/Vikoba, Saccosetc',
        '19. Unamiliki, ni mwanachama au ungependa kuwa mwanachama wa taasisi yoyote kati ya hizi/Vibubu',
        '19. Unamiliki, ni mwanachama au ungependa kuwa mwanachama wa taasisi yoyote kati ya hizi/Makundi / vikundi vidogo',
        '19. Unamiliki, ni mwanachama au ungependa kuwa mwanachama wa taasisi yoyote kati ya hizi/Mengine'
    ]

    x = _count_strings(row[(_q if not endline else _q_endine)], endline)
    if x > 0 and x <= 5: # BUG?
        return 1
    return 0

def _grl_ecoemp3(row, endline):
    _q = ['A_Q_28_1',
          'A_Q_28_2',
          'A_Q_28_3',
          'A_Q_28_4',
          'A_Q_28_5']

    _q_endline = ['20. Umeshawahi kuweka akiba ya pesa kupitia njia hizi au mahali pengine popote?/Akaunti ya benki', #COLUMN BJ
                  '20. Umeshawahi kuweka akiba ya pesa kupitia njia hizi au mahali pengine popote?/Mitandao ya simu (Airtel money, Tigopesa ,Mpesa)',
                  '20. Umeshawahi kuweka akiba ya pesa kupitia njia hizi au mahali pengine popote?/Vikoba Saccos nk',
                  '20. Umeshawahi kuweka akiba ya pesa kupitia njia hizi au mahali pengine popote?/Vibubu',
                  '20. Umeshawahi kuweka akiba ya pesa kupitia njia hizi au mahali pengine popote?/Makundi / vikundi vidogo']

    if _count_strings(row[(_q if not endline else _q_endline)], endline) > 0:
        return 1
    return 0

def _anemia_preve(row, endline):
    x = _count_strings(row[(_anemia_prevention_answers if not endline else _anemia_prevention_answers_endline)])
    if x >= 3 and x <=6:
        return 1
    return 0

def _facility_cat(row, endline):
    # BUG! The answers here are probably wrong
    if endline:
        _c = '118. Utaenda wapi kutafuta huduma ya virutubisho vya mwili na msaada ikitokea unahuitaji? ● Dawa za hospitali za kuongeza damu, mizizi lishe, matunda, mbegu lishe n.k/Kituo cha afya'
        _c2 = '118. Utaenda wapi kutafuta huduma ya virutubisho vya mwili na msaada ikitokea unahuitaji? ● Dawa za hospitali za kuongeza damu, mizizi lishe, matunda, mbegu lishe n.k/Wazazi / Ndugu/Marafiki/siri'
        if row[_c] == 1 or row[_c2] == 1:
            return 1
    else:
        if isinstance(row['A_Q_140_1'], str) or isinstance(row['A_Q_140_2'], str):
            return 1
    return 0

def indicator_1000_v2(df, endline):
    def _domain_score(qs, row):
        """The GEI score for the domain
        Calculated by counting each valid answer as one point,
        then averaging over the number of questions within the domain"""

        # import pdb; pdb.set_trace()
        score = 0
        for k, v in qs.items():
            if isinstance(v, set): # single choice
                if row[k] in v:
                    score += 1
                    _debug_answer_is_present_at_least_once.add(k)

            elif isinstance(v, list): # multi choice
                already_counted = False
                for subq in v:
                    if isinstance(row[subq], str):
                        _debug_answer_is_present_at_least_once.add(subq)

                        if not already_counted:
                            already_counted = True
                            score += 1
            elif callable(v):
                score += v(row)

        return (score / len(qs.keys()))

    def _expedom_viol_scores2(row, endline):
#        egen expedom_viol_scores=rowtotal(QN47b QN47c QN47d QN47e QN47g)
        # BUG This is wrong! Wrong answers
        _x = ["A_Q_61_2", "A_Q_61_3", "A_Q_61_4", "A_Q_61_5", "A_Q_61_7"]
        _x_endline = [
            "47. Ni wapi wewe au rafiki zako mtatoa taarifa za unyanyasaji dhidi ya wasichana/Mume, rafiki wa kiume au mpenzi",
            "47. Ni wapi wewe au rafiki zako mtatoa taarifa za unyanyasaji dhidi ya wasichana/Rafiki au jirani",
            "47. Ni wapi wewe au rafiki zako mtatoa taarifa za unyanyasaji dhidi ya wasichana/Mwalimu",
            "47. Ni wapi wewe au rafiki zako mtatoa taarifa za unyanyasaji dhidi ya wasichana/Polisi",
            "47. Ni wapi wewe au rafiki zako mtatoa taarifa za unyanyasaji dhidi ya wasichana/Mstari wa kusaidia watoto"
        ]

        if _count_strings(row[(_x if not endline else _x_endline)], endline) >= 2:
            return 1
        return 0

    def _hiv_trans_scores2(row, endline):
        _q = {
            'T_Q_151_1': { 'Yes' },
            'T_Q_151_2': { 'Yes' },
            'T_Q_151_3': { 'Yes' },
            'T_Q_151_4': { 'No' },
            'T_Q_151_5': { 'No' },
        }
        _q_endline = {
            '126a. Je inawezekana kupunguza hatari ya kusambaa kwa maambukizi ya VVU kwa kujamiiana na mwenza mmoja asiye na maambukizi, na hana wenza wengine?': { 'Ndio' },
            '126b. Je mtu anaweza kupunguza hatari ya kupata maambukizi ya VVU kwa kutumia kondomu kila anapo jamiiana?': { 'Ndio' },
            '126d. Je Mtu mwenye afya nzuri anaweza kuwa na VVU': { 'Ndio' },
            '126e.  Je mtu anaweza kupata VVU kwa kung’atwa na mbu?': { 'Hapana' },
            '126c. Je mtu anaweza kupata maambukizi ya VVU kwa kula chakula na mtu mwenye maambukizi?': { 'Hapana' },
        }
        score = _domain_score((_q if not endline else _q_endline), row)
        if score == 1:
            return 1
        return 0

    def _preq_prevent(row, endline):
         _q = ['A_Q_132_1',
               'A_Q_132_2',
               'A_Q_132_3',
               'A_Q_132_4',
               'A_Q_132_5',
               'A_Q_132_6',
               'A_Q_132_7',
               'A_Q_132_8',
               'A_Q_132_9',
               'A_Q_132_10']

         _q_endline = ['113. Nitajie njia zozote za kuzuia mimba unazozifahamu/Kondom',
                       '113. Nitajie njia zozote za kuzuia mimba unazozifahamu/Vidonge vya kuzuia mimb/majira',
                       '113. Nitajie njia zozote za kuzuia mimba unazozifahamu/Vidonge vya dharura vya kuzuia mimba/ P2',
                       '113. Nitajie njia zozote za kuzuia mimba unazozifahamu/Kitanzi',
                       '113. Nitajie njia zozote za kuzuia mimba unazozifahamu/Sindano',
                       '113. Nitajie njia zozote za kuzuia mimba unazozifahamu/Vipandikizi',
                       '113. Nitajie njia zozote za kuzuia mimba unazozifahamu/Kutokujamiiana',
                       '113. Nitajie njia zozote za kuzuia mimba unazozifahamu/Kunyonyesha',
                       '113. Nitajie njia zozote za kuzuia mimba unazozifahamu/Kutumia kalenda',
                       '113. Nitajie njia zozote za kuzuia mimba unazozifahamu/Kumwaga pembeni /withdraw']

         n = _count_strings(row[(_q if not endline else _q_endline)], endline)
         if n >= 3:
             return 1
         return 0

    _dimensions_midline = {
        "self_perception": {
            "Q_63": {
                'Strongly agree',
                'Partly agree',
            },
            "Q_64": {
                'Partly disagree',
                'Strongly disagree',
            },
            "Q_65": {
                'Strongly agree',
                'Partly agree',
            },
            "Q_66": {
                'Strongly agree',
                'Partly agree',
            },
            "Q_67": {
                'Partly disagree',
                'Strongly disagree',
            },
            "Q_69": { # BUG! NOTE I've swapped these backwards
                'Strongly disagree',
                'Partly disagree',
            },
            "Q_70": {
                'Partly disagree',
                'Strongly disagree',
            },
            "Q_71": {
                'Strongly agree',
                'Partly agree',
            },
            "Q_94": {
                'Yes',
            },
            "Q_95": {
                'Yes',
            },
            'Q_72': {
                'Partly disagree',
                'Strongly disagree',
            },
            "Q_49": {
                'Strongly agree',
                'Partly agree',
            },
        },
        "personal_freedom": {
            'T_Q_108_1': {
                'No'
            },
            'T_Q_108_2': {
                'No'
            },
            'T_Q_108_3': {
                'No'
            },
            'T_Q_108_4': {
                'No'
            },
            'T_Q_108_8': {
                'No'
            },
            "expedom_viol_scores2": lambda x: _expedom_viol_scores2(x, endline),
        },
        'access_to_and_control_over_resources': {
            "grl_ecoemp3": lambda x: _grl_ecoemp3(x, endline),
            "Q_25": {
                'Yes',
            },
            "Q_24": {
                'Yes',
            },
            "total_acc": lambda x: _total_acc(x, endline),
        },
        "decision_and_influence": {
            "Q_85": {
                'Strongly agree',
            },
            "Q_86": {
                'Strongly agree',
            },
            "Q_87": {
                'Strongly agree',
            },
            "Q_88": {
                'Strongly agree',
            },
            "Q_89": {
                'Strongly agree',
            },
        },
        "care_and_unpaid_works": {
            'T_Q_82_1': {'Both'},
            'T_Q_82_2': {'Both'},
            'T_Q_82_3': {'Both'},
            'T_Q_82_4': {'Both'},
            'T_Q_82_5': {'Both'},
        },
        "knowledge_and_nutrition": {
            "anemia_knowledge": _anemia_knowledge,
            "anemia_preve": _anemia_preve,
            "facility_cat": _facility_cat,
            "Q_143": { 'Strongly agree' },
        },
        "support_from_social_network": {
            'Q_39': {'Yes'},
        },
        "control_over_body": {
            # HIV
            "hiv": _hiv_trans_scores2,
            # SRHR Knowledge
            'Q_125': ['Q_125_O1'],
            'Q_129': { 'Four' },
            "preq_prevent": _preq_prevent,
            'Q_152': { 'Yes' },
            'Q_154': { 'Yes' },
            'Q_135': { 'Yes' },
            # Marriage
            'Q_121': { 'Strongly agree' },
            'Q_122': { 'Strongly agree' },
            'Q_123': { 'Strongly agree' },
            # Sexual assault including rape
            'Q_102': { 'Strongly disagree' },
            'Q_103': { 'Strongly disagree' },
            'Q_104': { 'Strongly disagree' },
            'Q_105': { 'Strongly disagree' },
            'Q_106': { 'Strongly disagree' },
            'Q_107': { 'Strongly disagree' },
        },
        "leadership": {
            'Q_84': { 'Strongly agree' }, # BUG!
            'Q_85': { 'Strongly agree' },
            'Q_90': { 'Strongly agree' },
            'Q_91': { 'Strongly agree' },
        },
        "economic_empowerment": {
            'Q_76': { 'Strongly agree' },
        }
    }

    _dimensions_endline = {
        "self_perception": {
            "48. Kwa ujumla, nimeridhika na mimi mwenyewe": {
                'Nakubali sana',
                'Nakubali kiasi',
            },
            "49. Wakati mwingine nadhani mimi sifai hata kidogo": {
                'Sikubali kiasi',
                'Sikubali kabisa',
            },
            "50. Ninahisi nina sifa kadhaa nzuri5": {
                'Nakubali sana',
                'Nakubali kiasi',
            },
            "51. Nina uwezo wa kufanya vitu kama watu wengine": {
                'Nakubali sana',
                'Nakubali kiasi',
            },
            "52. Ninahisi sina mengi ya kujivunia.": {
                'Sikubali kiasi',
                'Sikubali kabisa',
            },
            "53. Ninahisi kuwa mimi ni mtu wa thamani, angalau kwenye usawa mmoja na wengine": { # BUG! NOTE I've swapped these backwards
                'Sikubali kabisa',
                'Sikubali kiasi',
            },
            "54. Natamani ningeweza kuheshimiwa zaidi.": {
                'Sikubali kiasi',
                'Sikubali kabisa',
            },
            "55. Kwa ujumla, huwa nahisi mimi ni mtu wa kushindwa": {
                'Nakubali sana',
                'Nakubali kiasi',
            },
            "79. Ninajiamini kwamba ninaweza kukabiliana na matukio yasiyotarajiwa": {
                'Ndiyo',
            },
            "80. Kama nikipatwa na tatizo naweza kutafuta suluhisho": {
                'Ndiyo',
            },
            '57. Kwa kiwango gani unakubali au kukataa sentensi ifuatayo? Kazi ya mwanaume ni kutafuta/ kupata pesa, mwanamke kazi yake ni kuangalia nyumba na familia': {
                'Sikubali kiasi',
                'Sikubali kabisa',
            },
            "37. Kwa kiwango gani unakubali au kukataa na sentensi zifuatazo?   Ninaamini nina uhuru wa kutembea( naweza kutembea kutoka kijiji kimoja hadi kingine/ nina uhuru wa kwenda shuleni mwenyewe)": {
                'Nakubali kabisa',
                'Nakubali kiasi',
            },
        },
        "personal_freedom": {
            '92a asipomtii mume / rafiki wa kiume na ndugu na jamaa wengine': {
                'Hapana'
            },
            '92b Akihisi kua sio muaminifu': {
                'Hapana'
            },
            '93c akitelekeza watoto': {
                'Hapana'
            },
            '92d Akitumia pesa na rasilimali zingine kama chakula bila ruhusa': {
                'Hapana'
            },
            '92h Akitoka bila kumwambia': {
                'Hapana'
            },
            "expedom_viol_scores2": lambda x: _expedom_viol_scores2(x, endline),
        },
        'access_to_and_control_over_resources': {
            "grl_ecoemp3": lambda x: _grl_ecoemp3(x, endline),
            # "18. Je! Ungetaka kuweka akiba katika siku zijazo?": {
            #     'Ndio',
            # },
            "17. Je! Unafikiri kuweka akiba ni muhimu?": {
                'Ndio',
            },
            "total_acc": lambda x: _total_acc(x, endline),
        },
        "decision_and_influence": {
            "70. Wasichana/ wanawake wanaweza wakafanya maamuzi mazuri kuhusiana na chochote pamoja na maamuzi kwenye rasilimali( fedha,muda) shuleni, kwenye jamii, familia n.k kama vile wavulana/ wanaume wanavyoweza": {
                'Nakubali kabisa',
            },
            "71. Wasichana/ wanawake wanahaki ya kushiriki katika siasa.( wachaguliwe kama viongozi wa kisiasa, wapiga kura n.k) kama wavulana/ wanaume": {
                'Nakubali kabisa',
            },
            "72. Ninahisi kwamba nimehusishwa katika utoaji wa maamuzi utakaoniathiri mimi. Mfano nilikuwa na fursa ya kuelezea maoni au mapenedekezo kwenye shule / jamii/vilabu vya michezo/ social clubs/Saccos nilizohudhuria na maoni yangu yalisikilizwa na kusikika.": {
                'Nakubali kabisa',
            },
            "73. Kwa kawaida / mara nyingine ninashiriki katika mazungumzo ya kaya / shuleni/ au kwenye jamii": {
                'Nakubali kabisa',
            },
            "74. Kwa kawaida au mara nyingine naongea na wazazi, washirika, waalimu, jamii n.k na mara nyingine ninahimiza katika utoaji wa maamuzi.": {
                'Nakubali kabisa',
            },
        },
        "care_and_unpaid_works": {
            '67 a) Kuchota maji': {'Wote'},
            '67 b) Kulisha na kuogesha watoto': {'Wote'},
            '67 c) Kuwasaidia watoto masomo wakiwa nyumbani': {'Wote'},
            '67 d) Kumhudumia mgonjwa': {'Wote'},
            '67 e) Kuosha, kupika na kufanya usafi': {'Wote'},
        },
        "knowledge_and_nutrition": {
            "anemia_knowledge": lambda x: _anemia_knowledge(x, endline),
            "anemia_preve": lambda x: _anemia_preve(x, endline),
            "facility_cat": lambda x: _facility_cat(x, endline),
            "120. Lishe bora ni muhimu kwa wasichana toka muda anazaliwa ili iweze kuwasaidia kupata watoto wenye afya hapo baadaye": { 'Nakubaliana kabisa' },
        },
        "support_from_social_network": {
            '27. Je wewe ni mwanachama wa club yeyote ya majadiliano shuleni, kwenye jamii? Je ulishawahi kufanya majadiliano shuleni au kuzungumza katika mikutano ya kijamii, kanisani/msikitini au mikutano ya kifamilia?': {'Ndiyo'},
        },
        "control_over_body": {
            # HIV
            "hiv": lambda x: _hiv_trans_scores2(x, endline),
            # SRHR Knowledge
            '109. Ikitokea una uhitaji wa huduma za afya ya uzazi (mfano huduma za mama mjamzito, huduma ya kujifungua, huduma ya baada ya kujifungua, uzazi wa mpango, huduma ya baada ya mimba kuharibika, upimaji wa saratani ya shingo ya kizazi), Utaenda wapi?': ['109. Ikitokea una uhitaji wa huduma za afya ya uzazi (mfano huduma za mama mjamzito, huduma ya kujifungua, huduma ya baada ya kujifungua, uzazi wa mpango, huduma ya baada ya mimba kuharibika, upimaji wa saratani ya shingo ya kizazi), Utaenda wapi?/Kituo cha Afya'], #was selected if response is 1
            '111. Mama mjamzito anatakiwa kuhudhuria walau mara ngapi katika kituo cha huduma za afya?': { 'Nne' },
            "preq_prevent": lambda x: _preq_prevent(x, endline),
            '127. Ulishawahi kupima maambukizi ya VVU?': { 'Ndio' },
            '129. Katika jamii yako, umewahi kupata taarifa, ushauri, au huduma za afya zinazohusiana na afya za uzazi na haki zake, pamoja na lishe (kwa mfano shuleni, klabu, mikutano ya kijamii au sehemu nyingine yoyote kwenye jamii?)': { 'Ndio' },
            '115. Umewahi kusikia kuhusu vidonge vya dharura vya kuzuia ujauzito?': { 'Ndiyo' },
            # Marriage
            '105. Kwa kiwango gani unakubaliana au hukubaliani na sentensi zifuatazo? Kuhairisha ndoa na mimba ya kwanza ni nzuri kwa msichana inampa fursa ya kuendelea kusoma na kufikia ndoto zake, lakini pia inamsaidia kuepuka matatizo wakati wa kujifungua.': { 'Nakubali kabisa' },
            '106. Ndoa kwa mtoto mdogo (chini ya miaka 18) ni mila mbaya': { 'Nakubali kabisa' },
            '107. Serikali kudhibiti ndoa za utotoni': { 'Nakubali kabisa' },
            # Sexual assault including rape
            '86. Inakubalika kwa mvulana / mwanaume kumdhalilisha, kumtishia au kumtukana msichana/mwanamke asiyemtii?': { 'Sikubali kabisa' },
            '87. Inakubalika kwa mvulana/ mwanaume kuwa na tabia za umiliki ( kudhibiti maamuzi na shughuli za rafiki wa kike / mke sababu tu ni rafiki yake wa kike au mke wake)': { 'Sikubali kabisa' },
            '88. Inakubalika Kwa mvulana / mwanaume kudhibiti mienendo ya rafiki wa kike / mke kwa sababu tu ni Rafiki yake wa kike au mke wake': { 'Sikubali kabisa' },
            '89. Inakubalika kwa mvulana / mwanaume kulazimisha mtu kubusiana, kushikana , Kujamiiana bila ridhaa yake': { 'Sikubali kabisa' },
            '90. Inakubalika kwa mvulana / mwanaume kutoa maneno kwa msichana/mwanamke ya kumfanya adhalilike kijinsia au asijiskie vizuri': { 'Sikubali kabisa' },
            '91. Inakubalika kwa mvulana/ mwanaume kuwa na udhibiti wote kwenye pesa na rasilimali zote za uchumi za rafiki wa kike / mke': { 'Sikubali kabisa' },
        },
        "leadership": {
            '69. Wavulana/wanaume mashuleni, kwenye familia /jamii na ngazi ya nchi huwa ni viongozi wazuri kuliko wasichana/ wanawake': { 'Nakubali kabisa' }, # BUG!
            '70. Wasichana/ wanawake wanaweza wakafanya maamuzi mazuri kuhusiana na chochote pamoja na maamuzi kwenye rasilimali( fedha,muda) shuleni, kwenye jamii, familia n.k kama vile wavulana/ wanaume wanavyoweza': { 'Nakubali kabisa' },
            '75. Ninayo furaha kushiriki katika Kaya/ shule/ jamii katika kufanya maamuzi': { 'Nakubali kabisa' },
            '76. Nina shauku kubwa ya kuwa kiongozi baadae kama vile kiongozi wa darasa, dada/kaka mkuu wa shule, kiongozi wa jamii au kiongozi wa siasa': { 'Nakubali kabisa' },
        },
        "economic_empowerment": {
            '61. Kwa kiwango gani unakubali au kukataa sentensi ifuatayo? Wanawake/ wasichana wanauwezo wa kuchangia pato la kaya kama wanaume/wavulana': { 'Nakubali kabisa' },
        }
    }

    _dimensions = (_dimensions_midline if not endline else _dimensions_endline)
    components = _dimensions.items()
    _dimensions['aggregate'] = {}
    for _, v in components:
        _dimensions['aggregate'] = _dimensions['aggregate'] | v

    print("Num aggs: {}".format(len(_dimensions['aggregate'].keys())))

    results = pd.DataFrame()

    _debug_answer_is_present_at_least_once = set()

    for empowerment_domain, questions in _dimensions.items():
        results[empowerment_domain] = df.apply(lambda x: 100 * _domain_score(questions, x) , axis=1)

    # _debug_single_choice_questions = [sq for domain in _dimensions.values() for sq in domain if isinstance(domain[sq], set)]
    # _debug_multi_choice_answers = [a for domain in _dimensions.values() for mq in domain.keys() if isinstance(domain[mq], list) for a in domain[mq]]
    # _debug_all_answers = [a for qs in [_debug_single_choice_questions, _debug_multi_choice_answers] for a in qs]
    # print('missing:')
    # _debug_missing = set(_debug_all_answers).difference(_debug_answer_is_present_at_least_once)
    # print(_debug_missing)
    # print(df[_debug_missing].head())
    return results



_s_n_rights_questions = [
    'A_Q_157_1', # Physical and pubertal development
    'A_Q_157_3', # Nutrition
    'A_Q_157_2', # Menstrual hygiene/ problems
    'A_Q_157_5', # Oral contraceptive pills
    'A_Q_157_4', # Anemia
    'A_Q_157_6', # Comdoms
    'A_Q_157_8', # Emergency Contraceptive pills
    'A_Q_157_11', # Antenatal care
    'A_Q_157_13', # Postpartum care
    'A_Q_157_12', # Safe delivery
    'A_Q_157_14', # Cervical cancer
]

def indicator_1300b_tables(df):
    results = df[_s_n_rights_questions].apply(lambda x: pd.Series.value_counts(x,normalize=True)).sum(axis=1)
    return results


def indicator_1300b(df):
    """Proportion of adolescent girls and boys (10-19 years) who know their SRHR and nutrition rights (disaggregated by sex)

    Numerator: Number of adolescent girls and boys (10-19 years) who know their SRHR and nutrition rights by scoring 80% and above.
    Denominator: Total number of adolescent girls and boys aged 10-19 years who were interviewed.
    """

    results = pd.DataFrame()

    # SRHR and Nutrition rights
    # egen s_n_rights=rowtotal(QN131f QN131g QN131h QN131i QN131j  QN131l QN131n QN131o QN131q QN131r QN131t)
    # QN131 is Q_157 in our dataset
    # BUG the composition of this answer seems flawed too

    # NOTE _s_n_rights_questions is defined globally in this package
    s_n_rights = df[_s_n_rights_questions].apply(_count_strings, axis=1)

    # Rights absolute scores into % scores
    # gen s_n_rights_pc=s_n_rights/11*100
    s_n_rights_pc = s_n_rights * (100 / len(_s_n_rights_questions))
    # gen s_n_rights_cat=1 if s_n_rights_pc>=0 & s_n_rights_pc<60
    # replace s_n_rights_cat=2 if s_n_rights_pc>=60 & s_n_rights_pc<80
    # replace s_n_rights_cat=3 if s_n_rights_pc>=80 & s_n_rights_pc<=100
    # lab var s_n_rights_cat "Level of knowledge of SRHR and Nutrition services rights"
    # lab define s_n_rights_cat 1"Low"2"Moderate"3"High"
    # lab values s_n_rights_cat s_n_rights_cat

    s_n_rights_cat = _bloom(s_n_rights_pc)

    results = s_n_rights_cat.apply(lambda x: 1 if x == "High" else 0)

    return results


def indicator_1210(df, endline):
    """Degree to which girls are perceived as equal to boys by adolescent girls / boys / parents / caregivers / community leaders (disaggregated by sex)

    Numerator: Number of boys and girls who strongly agree with the following statement: “Girls are equal to boys as such they should be given equal opportunity for education and considered in decision making etc”.
    Denominator: Total number of boys and girls interviewed
    """
    # NOTE The exact formulation of the asked question is (which mimics the baseline):
    # Tell me your perception, do you think girls are equal to boys and therefore should also be  given opportunities such as schooling etc.?

    boys_and_girls = df['Q_80']

    def _strongly_agree (val):
        if val == "Strongly agree":
            return 1
        else:
            return 0

    results = pd.DataFrame()
    results[0] = boys_and_girls.apply(_strongly_agree)
    return results

def indicator_1220a(df):
    intermediary = indicator_1220cat(df)
    return pd.to_numeric(intermediary.apply(lambda x: 1 if x == "High" else 0)) # TODO

def indicator_1220ab(df):
    intermediary = indicator_1220cat(df)
    return pd.to_numeric(intermediary.apply(lambda x: 1 if (x == "High" or x == "Moderate") else 0)) # TODO


# gen anemia=1 if QN116a==1 | QN116b==1 # Q_136 for us
# # QN116a = Lack of red blood cells
# # QN116b = Lack of appetite
# replace anemia=0 if anemia==.
_anemia_knowledge_correct_answers = [
    'A_Q_136_1', # lower red blood cells
    'A_Q_136_3', # Loss of appetite
]

_anemia_knowledge_correct_answers_endline = [
    '116, Unafahamu nini kuhusu upungufu wa damu?/Upungufu wa chembe nyekundu za damu', # lower red blood cells
    '116, Unafahamu nini kuhusu upungufu wa damu?/Kukosa hamu ya kula', # Loss of appetite
]

def _anemia_knowledge(row):
    row = row[_anemia_knowledge_correct_answers]
    result = 0
    for key, val in row.items():
        if isinstance(val, str):
            result = 1
    return result

# egen anemia_preve=rowtotal(QN117a QN117b QN117c QN117d QN117e QN117g) # That's Q_138 for us
_anemia_prevention_answers = [
    'A_Q_138_1', # Iron and folic acid tablets
    'A_Q_138_3', # Eat vegetables
    'A_Q_138_2', # Eat leafy greens
    'A_Q_138_5', # Drink milk
    'A_Q_138_4', # Eat meat, liver
    'A_Q_138_7', # Balanced diet
]
_anemia_prevention_answers_endline = [
    '117. Unawezaje kuzuia upungufu wa damu?/Vidonge vya kuongeza damu', # Iron and folic acid tablets, Column KM
    '117. Unawezaje kuzuia upungufu wa damu?/Kula mboga mboga kama bilinganya, carroti, nyanya chungu', # Eat vegetables
    '117. Unawezaje kuzuia upungufu wa damu?/Kula mboga za majani kama mchicha, matembele, spinach', # Eat leafy greens
    '117. Unawezaje kuzuia upungufu wa damu?/Kunywa maziwa', # Drink milk
    '117. Unawezaje kuzuia upungufu wa damu?/Kula nyama, maini', # Eat meat, liver
    '117. Unawezaje kuzuia upungufu wa damu?/Kula mlo ulio kamili ', # Balanced diet
]

def indicator_1220breakdown(df):
    """Proportion of adolescent girls and boys under 19 years who have correct knowledge of contraceptive methods, HIV and nutrition (disaggregated by sex)

    Numerator: Number of adolescent girls and boys under 19 years who have correct knowledge of contraceptive methods, HIV and nutrition by scoring 80% and above.
    Denominator: Total number of adolescent girls and boys aged 10-19 years who were interviewed.
    """
    results = pd.DataFrame()


    anemia = df[_anemia_knowledge_correct_answers].apply(_anemia_knowledge, axis=1)

    anemia_preve = df[(_anemia_prevention_answers if not endline else _anemia_prevention_answers_endline)].apply(_count_strings, axis=1)
    # BUG This is another mistake here ...
    # gen anemia_preve_stat=1 if anemia_preve>=3 & anemia_preve<=6

    def _within_bounds(value):
        if value >= 3 and value <= 6:
            return 1
        else:
            return 0
    anemia_preve_stat = anemia_preve.apply(_within_bounds)

    # destring QN118a QN118b,replace # Q_140 in our dataset
    # egen facility_score=rowtotal(QN118a QN118b)
    _health_services_correct_answers = [
        'A_Q_140_1', # Health centre
        # 'A_Q_140_3', # Traditional healers # NOTE BUG Traditional healers were included in the baseline,
        # but Jaya and Nicholas advised on 6/10/22 that it is not correct
    ]
    facility_score = df[_health_services_correct_answers].apply(_count_strings, axis=1)

    # gen facility_cat=1 if facility_score!=0
    # replace facility_cat=0 if facility_cat==.

    # egen nutri_know_scores=rowtotal(anemia anemia_preve_stat facility_cat QN119c QN120c QN121c QN122c)

    # NOTE BUG The baseline had marked "2" for incorrect answers here, when they should have been
    # 0. Jaya and Nicholas advised to address this in an email on 6/10/2022
    _agreement_map = {
        'Decline to answer': 0, # 2 in the baseline
        'Partly agree': 1,
        'Partly disagree': 0, # 2 in the baseline
        'Strongly agree': 1,
        'Strongly disagree': 0, # 2 in the baseline
    }

    _disagreement_map = {
        'Decline to answer': 0,
        'Partly agree': 0,
        'Partly disagree': 1,
        'Strongly agree': 0,
        'Strongly disagree': 1,
    }

    # NOTE BUG This was _agreement_map in the baseline, but the question is framed in the reverse, so
    # _disagreement_map is correct here
    QN119c = df['Q_142'].map(_disagreement_map).apply(pd.to_numeric) # It is proper to give boy children more and proper balanced ...

    QN120c = df['Q_143'].map(_agreement_map).apply(pd.to_numeric) # Good nutrition is very important for girls ...
    QN121c = df['Q_144'].map(_agreement_map).apply(pd.to_numeric) # Good nutrition is very important for pregnant women ...
    QN122 = df['Q_145'].map(_agreement_map).apply(pd.to_numeric) # Nutrition is important for adolescent girls in general ...

    nutri_know_scores = anemia + anemia_preve_stat + QN119c + QN120c + QN121c + QN122

    # NOTE this appears to be unused
    # gen nutri_know_pc=nutri_know_scores/7*100
    # nutri_know_pc = (nutri_know_scores / 7) * 100

    # print('nutri_know_pc')
    # print(nutri_know_pc)

    # QN111 : How often should a pregnant mother attend a health care center? # Q_129 in our dataset
    # gen QN111b=1 if QN111 =="Nne" # 4
    # replace QN111b=2 if QN111=="7" | QN111=="Mbili" | QN111=="Moja" | QN111=="Sijui" | QN111=="Tano" | QN111=="Tatu"
    # lab var QN111b "Mention the minimum numbers of check-ups that a pregnant woman should get are four"
    # lab define QN111b 1"Aware" 2"Not aware"
    # lab values QN111b QN111b
    # tab QN111b
    # NOTE BUG 0 was 2 in the baseline, after meeting w/ Jaya and Nicholas we agreed to correct this
    knows_checkups = df['Q_129'].apply(lambda x: 1 if x == 4 else 0).apply(pd.to_numeric)

    # QN113: Tell me any birth control pills you know of ... corresponds to Q_132
    # NOTE There appears to be a BUG here. 1 means the respondent was aware, 2 means not aware ... but we total them together ...
    # NOTE but it should've been 1 and 0. So their calculations would've been incorrect here.
    # egen fp_know_scores=rowtotal(QN111b QN113b_1 QN113c_1 QN113d_1 QN113e_1 QN113f_1 QN113g_1 QN113h_1 QN113i_1 QN113j_1 QN113k_1)
    # # withdraw, condom, day_after_pills, birth_control_pills,
    # # injectable, loop, abstinence, implants, calendar method, and LAM

    # NOTE BUG 0 was 2 in the baseline
    # NOTE we should filter out those that decline to answer, but that was not done in baseline,
    # and they were counted as zero scores.
    # Decline to answer is Q_132_11
    def _is_string(x):
        if isinstance(x, str):
            return 1
        return 0

    fp_know_scores = \
    knows_checkups + \
    df['A_Q_132_10'].apply(_is_string).astype('int64') + \
    df['A_Q_132_1'].apply(_is_string).astype('int64') + \
    df['A_Q_132_3'].apply(_is_string).astype('int64') + \
    df['A_Q_132_2'].apply(_is_string).astype('int64') + \
    df['A_Q_132_5'].apply(_is_string).astype('int64') + \
    df['A_Q_132_4'].apply(_is_string).astype('int64') + \
    df['A_Q_132_7'].apply(_is_string).astype('int64') + \
    df['A_Q_132_6'].apply(_is_string).astype('int64') + \
    df['A_Q_132_9'].apply(_is_string).astype('int64') + \
    df['A_Q_132_8'].apply(_is_string).astype('int64')

    # egen hiv_trans_scores=rowtotal(QN126a_1 QN126b_1 QN126c_1 QN126d_1 QN126e_1)
    # gen hiv_trans_cat=1 if hiv_trans_scores==5
    # replace hiv_trans_cat=0 if hiv_trans_cat==.
    # Q_151 in our dataset
    _hiv_answers = ['T_Q_151_1', 'T_Q_151_2', 'T_Q_151_3', 'T_Q_151_4', 'T_Q_151_5']
    def _count_yeses(row):
        n = 0
        for key, value in row.items():
            if value == "Yes":
                n = n + 1
        return n

    hiv_trans_scores = df[_hiv_answers].apply(_count_yeses, axis=1)

    # ****
    # Generate combined (HIV, Nutrition and Family Planning knowledge Indicator)
    # ****Nutri_know_scores (7), fp_know_scores (11) and hiv_trans_scores(5)
    # egen hiv_nutr_fp_knowscores=rowtotal(nutri_know_scores fp_know_scores hiv_trans_scores)
    hiv_nutr_fp_knowscores = nutri_know_scores + fp_know_scores + hiv_trans_scores

    # gen hiv_nutr_fp_know_pc=hiv_nutr_fp_knowscores/23*100

    # ****Overall mean scores (%) HIV, Nutrition and Family Planning knowledge by site, sex and age
    # oneway hiv_nutr_fp_know_pc region,tabulate
    # ttest hiv_nutr_fp_know_pc,by(QN14b) # NOTE QN14b is 'sex' in our dataframe
    # ttest hiv_nutr_fp_know_pc,by(age_group)

    results = pd.DataFrame()
    results['nutri_know_scores'] = nutri_know_scores
    results['fp_know_scores'] = fp_know_scores
    results['hiv_trans_scores'] = hiv_trans_scores

    results['fp_know_scores_pc'] = results['fp_know_scores'] / 11
    results['nutri_know_scores_pc'] = results['nutri_know_scores'] / 7
    results['hiv_trans_scores_pc'] = results['hiv_trans_scores'] / 5

    return results

def indicator_1220cat(df):
    breakdown = indicator_1220breakdown(df)

    results = breakdown['nutri_know_scores'] + breakdown['fp_know_scores'] + breakdown['hiv_trans_scores']
    results = 100 * results / (11 + 7 + 5)


    # ****Generate HIV, Nutrition and FP knowledge level
    # gen hiv_nutr_fp_know_cat=1 if hiv_nutr_fp_know_pc<60
    # replace hiv_nutr_fp_know_cat=2 if hiv_nutr_fp_know_pc>=60 & hiv_nutr_fp_know_pc<80
    # replace hiv_nutr_fp_know_cat=3 if hiv_nutr_fp_know_pc>=80 & hiv_nutr_fp_know_pc<=100
    # lab var hiv_nutr_fp_know_cat"HIV, Nutrition and FP knowledge level"
    # lab define hiv_nutr_fp_know_cat 1"Low"2"Moderate"3"High"
    # lab values hiv_nutr_fp_know_cat hiv_nutr_fp_know_cat
    # tab hiv_nutr_fp_know_cat
    return _bloom(results)

def indicator_1220hiv(df):
    bd = indicator_1220breakdown(df)
    results = pd.DataFrame()
    results[0] = bd['hiv_trans_scores_pc']
    return results

def indicator_1220fp(df):
    bd = indicator_1220breakdown(df)
    results = pd.DataFrame()
    results[0] = bd['fp_know_scores_pc']
    return results

def indicator_1220nutri(df):
    bd = indicator_1220breakdown(df)
    results = pd.DataFrame()
    results[0] = bd['nutri_know_scores_pc']
    return results

def indicator_1200b(df, endline):

    df = df[(df["agegroup"] == "15-19") | (df["agegroup"] == "10-14")]
    # Calculation of indicator 1200b: As suggested by PEP and as agreed by Bodhi in the excel matrix, if changing the denominator makes more sense, can’t we do that and mention in the inception report that this is a change since baseline for improvement of the indicator? While we do want comparability, we shouldn’t go ahead with an indicator that doesn’t make sense. But I would also request you to consider the feasibility of collecting the data for denominator as suggested by PEP.
    # Table 3 Indicatori1200b: The proposed calculation for this indicator is not appropriate. Two thoughts: (1) FP is relevant as a proxy of SRHR service utilization, but how is nutrition measured in this study? Is the assumption that nutrition services are bundled with antenatal care visits? This is a big assumption, especially given the participants. (2) There is potentially a big problem with the denominator -- only those adolescents who are either pregnant (or accompanying a pregnant partner, potentially), or those who are sexually active or planning to be would access ANC and FP services to begin with. If you have the entire population of adolescents as the denominator, this indicator is not going to mean much. Would you not want to know this instead: among those who had a reason to access ANC or FP, what % actually sought the services?
    inclusion_criteria = ([
        'Q_118',
        'Q_119',
        'Q_110',
        ] if not endline else [
            '102. Umeshawahi kutumia uzazi wa mpango (kama condom, vidonge, sindano)?',
            '103. Ulitumia condom ulivyojamiiana kwa mara ya mwisho (ulivyojamiiana kabla ya mahojiano haya)?',
            '94. Umeshawahi kufanya mapenzi?',
        ])

    selection_criteria = [
        'Q_114',
        'Q_152',
        'Q_153',
    ] if not endline else [
        '98. Umewahi kupata mimba?',
        '127. Ulishawahi kupima maambukizi ya VVU?',
        '128. Ulishawahi kuumwa magonjwa ya zinaa?',
    ]

    _yes = 'Yes' if not endline else 'Ndiyo'

    def _filter(row):
        for ic in selection_criteria:
            if row[ic] == _yes:
                return 1
        return 0

    def _score(row):
        for ic in inclusion_criteria:
            if row[ic] == _yes:
                return 1
        return 0

    # df[selection_criteria].map({"Yes": 1, "No": 0}).any()
    filtered_df = df[df[selection_criteria].apply(_filter, axis=1) == 1]
    results = filtered_df[inclusion_criteria].apply(_score, axis=1)

    return results

def indicator_1113(df, endline):
    filtered = df[(df["agegroup"] == "15-19") | (df["agegroup"] == "10-14")]

    results = pd.DataFrame()
    _q = 'Q_154' if not endline else '129. Katika jamii yako, umewahi kupata taarifa, ushauri, au huduma za afya zinazohusiana na afya za uzazi na haki zake, pamoja na lishe (kwa mfano shuleni, klabu, mikutano ya kijamii au sehemu nyingine yoyote kwenye jamii?)'

    # NOTE Ndiyo is mispelled here, it is not a bug.
    results[0] = filtered[_q].map(({"Yes": 1, "No": 0} if not endline else {'Hapana': 0, 'Ndio': 1}))

    return results
