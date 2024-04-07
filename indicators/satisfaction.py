import pandas as pd

def load(file_path, endline=False):
    df = pd.read_excel(file_path)

    def _age_to_agegroup(age):
        if age < 10:
            return "0-9"
        elif age < 15:
            return "10-14"
        elif age < 20:
            return "15-19"
        else:
            return ">19"

    _agecol = 'Q_4' if not endline else "Umri"
    df['age'] = df[_agecol]
    df['agegroup'] = df['age'].map(_age_to_agegroup)

    df = df[(df["age"] >= 10) & (df["age"] <= 19)]

    _regions = {
        "Mbeya": {
            1, # "Ituha Dispensary": ,
            2, # "Madibira HC",
            3, # "Mawindi HC"

    },
        "Songwe": {
            4, #"Isana HC",
            5, #"Itaka HC",
            6, #"Ndalambo HC",
            7, #"Machimbo Dispensary",
        },
        "Zanzibar": {
            8, "Mwera PHCU",
            9, #"Mbuzini PHCU",
            10, #"Bwejuu HCU",
            11, #"KMKM Hospital",
            12, #"Konde PHCU",
            13,#"Mkoani Hospital",
            14,#"Bwagamoyo"
        }


    }
    _endline_regions = {
        "Mbeya": {
            "Ituha HC",
            "Madibira Health Centre (HC)",
            "Mawindi HC",
    },
        "Songwe": {
            "Isansa HC",
            "Itaka HC",
            "Ndalambo HC",
            "Mchindo Dispensary",
        },
        "Zanzibar": {
            "Mwera Primary Health Care Unit (PHCU)",
            "Mbuzini PHCU",
            "Dongwe Dispensary",
            "Selem hospital",
            "Konde PHCU",
            "Mkoani Youth Services Clinic",
            "Bwagamoyo",
        }
    }
    _names_to_regions = dict()
    for k, hospitals in (_regions if not endline else _endline_regions).items():
        for v in hospitals:
            _names_to_regions[v] = k

    _facility_col = 'Q_2' if not endline else "6. Jina la kituo cha afya"
    facility_name = df[_facility_col]
    df['regions'] = facility_name.map(_names_to_regions)

    if endline:
        df['sex'] = df['Jinsia'].map({'Mme': 'Male',
                                      'Mke': 'Female'})
    return df

def indicator_1100b(df, endline):
    """Proportion of adolescent girls and boys who report receiving quality sexual and reproductive health and
    nutrition services in the selected districts in Mainland and Zanzibar (disaggregated by sex and age)

    Numerator: Number of adolescent girls and boys who report receiving quality sexual and reproductive health and nutrition services by scoring 80% and above.
    Denominator: Total number of adolescent girls and boys who were interviewed."""

    _questions = {
        # 1 is Yes, 2 is No
        'Q_8': 1, # "Did you notice any signboard in a language you understand that mentions the operating hours of the facility?"
        'Q_9': 1, # "Today, did you get the services that you came for?"
        'Q_10': 1, # "Did anybody tell you, today what other services you can obtain in this facility?"
        'Q_12': 1, # "Did you see informational materials for adolescents, including video or TV, in the waiting area?"
        'Q_14': 1, # "Working hours for adolescent’s services are convenient for you?"
        'Q_15': 1, # "Have you seen a display that mentions that services will be provided to all adolescents without discrimination?"
        'Q_17': 1,# "During your consultation or counselling session did any service provider talk to you about how to prevent diseases and what to do to stay healthy?"
        'Q_18': 1,# "During your consultation or counselling session did the service provider inform you about the services available?"
        'Q_23': 1,# "During your consultation or counselling session did the service provider ask you questions about sexual relationships?"
        'Q_26': 1,# "Did the service provider treat you in a friendly manner?"
        'Q_27': 1,# "Was the service provider respectful of your needs?"
        'Q_28': 2,# "Did anyone else enter the room during your consultation?"
        'Q_29': 1,# "Did the service provider assure you at the beginning of the consultation that your information will not be shared with anyone without your consent?"
        'Q_30': 1,# "Do you feel confident that the information you shared with service provider today will not be disclosed to anyone else without your consent?"
        'Q_31': 1,# "Do you feel that the health information provided during the consultation was clear and that you understood it well?"
        'Q_32': 1,# "Did the provider ask you if you agree with the treatment/ procedure/ solution that was proposed?"
        'Q_33': 1,# "Overall, did you feel that you were involved in the decisions regarding your care? For example, you had a chance to express your opinion or preference for the care provided, and your opinion was listened to, and heard?"
        'Q_38': 2, # "Today, were you denied necessary services at this health facility?"
    }

    _questions_endline = {
        # 1 is Yes, 2 is No
        "2. Je umepata kuona tangazo (kwa lugha yoyote unayoweza kuelewa) kuhusu muda wa kazi kwa hiki kituo.": "Ndiyo", # "Did you notice any signboard in a language you understand that mentions the operating hours of the facility?": "Ndiyo",
        "3. Leo, umepata huduma uliyoifuata?": "Ndiyo", # "Today, did you get the services that you came for?"
        "4. Kuna mtu yoyote amekuambia hii leo, kwamba kuna huduma nyingine yoyote inayotolewa katika kituo hiki?": "Ndiyo", # "Did anybody tell you, today what other services you can obtain in this facility?"
        "6. Je umeona taarifa ama matangazo yoyote yenye ujumbe kwa vijana rika kupitia njia mbalimbali kama TV au kwenye eneo la kusubiria huduma?" : "Ndio", # "Did you see informational materials for adolescents, including video or TV, in the waiting area?"
        "8. Je masaa ya kazi kwa huduma za vijana yanafaa kwako?": "Ndio", # "Working hours for adolescent’s services are convenient for you?"
        "9. Je umesoma mahali popote au kupata tangazo linalosema kuwa “huduma zitatolewa kwa vijana rika wote bila ubaguzi”": "Ndio", # "Have you seen a display that mentions that services will be provided to all adolescents without discrimination?"
        "11. Wakati unahudumiwa (kutibiwa ama kupewa ushauri nasaha) kuna mhudumu yoyote amekuambia kuhusu namna ya kuzuia magonjwa na nini cha kufanya kubaki katika afya njema?": "Ndio", # "During your consultation or counselling session did any service provider talk to you about how to prevent diseases and what to do to stay healthy?"
        "12. Wakati unahudumiwa (kutibiwa ama kupewa ushauri nasaha) kuna mhudumu yoyote amekuhabarisha kuhusu huduma zinazopatikana?": "Ndio", # "During your consultation or counselling session did the service provider inform you about the services available?"
        "17. Wakati unahudumiwa (kutibiwa ama kupewa ushauri nasaha) kuna mhudumu yoyote amekuuliza kuhusu mahusiano ya mapenzi?": "Ndio", # "During your consultation or counselling session did the service provider ask you questions about sexual relationships?"
        "20. Je mtoa huduma alikuhudumia katika hali ya urafiki?": "Ndio", # "Did the service provider treat you in a friendly manner?"
        "21. Je mtoa huduma alionyesha kuheshimu mahitaji yako?": "Ndio", # "Was the service provider respectful of your needs?"
        "22. Je, kulitokea mtu mwingine yeyote kuingia kwenye chumba wakati unahudumiwa?": "Hapana",  # "Did anyone else enter the room during your consultation?"
        "23. Je mtoa huduma alikuhakikisha mwanzo mwa huduma kwamba taarifa haitashirikishwa na mtu yeyote bila ridhaa yako?": "Ndio", # "Did the service provider assure you at the beginning of the consultation that your information will not be shared with anyone without your consent?"
        "24. Je wewe unaamini kwamba taarifa ulizomshirikisha mtoa huduma leo hazitafahamika na mtu mwingine yeyote pasipo ridhaa yako?": "Ndio", # "Do you feel confident that the information you shared with service provider today will not be disclosed to anyone else without your consent?"
        "25. Je kwa maoni yako taarifa za kiafya zinazotolewa na mhudumu pindi anapokuona zilikua wazi na wewe ulizielewa vizuiri?": "Ndio", # "Do you feel that the health information provided during the consultation was clear and that you understood it well?"
        "26. Je mtoa huduma alikuuliza ikiwa ulikubaliana na tiba/huduma/suluhu iliyopendekezwa kabla ya kukupa?": "Ndio", # "Did the provider ask you if you agree with the treatment/ procedure/ solution that was proposed?"
        "27. Je kwa ujumla wake, unajisikia kama umehusishwa katika maamuzi kuhusu huduma unayopewa? Kwa mfano, je ulikua na nafasi ya kueleza maoni yako au mapenzi yako juu ya aina ya huduma unazopewa, maoni yako yalisikilizwa, na kusikika": "Ndio", # "Overall, did you feel that you were involved in the decisions regarding your care? For example, you had a chance to express your opinion or preference for the care provided, and your opinion was listened to, and heard?"
        "32. Kwa leo je, umekosa/kunyimwa huduma yoyote muhimu katika kituo hiki?": "Hapana", # "Today, were you denied necessary services at this health facility?"
    }

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

    qs = (_questions if not endline else _questions_endline)
    _debug_missing_answers = set(qs.keys())
    def _score_row(row):
        score = 0
        for k, v in row.items():
            if qs[k] == v:
                score += 1
                _debug_missing_answers.discard(k)
        average_score = (100 * score) / len(qs)

        return average_score

    data = df[qs.keys()]
    results = _bloom(data.apply(_score_row, axis=1)).apply(lambda x: 1 if x == "High" else 0)

    return results
