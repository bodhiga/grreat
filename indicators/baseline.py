import pandas as pd

def indicator_1200b(df, endline):
    df = df[(df["age"] >= 10) & (df["age"] <= 19)]
    # Calculation of indicator 1200b: As suggested by PEP and as agreed by Bodhi in the excel matrix, if changing the denominator makes more sense, can’t we do that and mention in the inception report that this is a change since baseline for improvement of the indicator? While we do want comparability, we shouldn’t go ahead with an indicator that doesn’t make sense. But I would also request you to consider the feasibility of collecting the data for denominator as suggested by PEP.
    # Table 3 Indicatori1200b: The proposed calculation for this indicator is not appropriate. Two thoughts: (1) FP is relevant as a proxy of SRHR service utilization, but how is nutrition measured in this study? Is the assumption that nutrition services are bundled with antenatal care visits? This is a big assumption, especially given the participants. (2) There is potentially a big problem with the denominator -- only those adolescents who are either pregnant (or accompanying a pregnant partner, potentially), or those who are sexually active or planning to be would access ANC and FP services to begin with. If you have the entire population of adolescents as the denominator, this indicator is not going to mean much. Would you not want to know this instead: among those who had a reason to access ANC or FP, what % actually sought the services?
    inclusion_criteria = [
        'QN102', # Have you ever used Family planning (such as condom, pills, injection)? # Q102 # Ndiyo
        'QN103', # Did you use condom in your last sexual encounter (That is; when you last had sex before this interview # Q103 # Ndiyo
        'QN94' # Have you ever had sexual intercourse? # Q94 # Ndiyo
    ]

    selection_criteria = [
        'QN98', # Have you ever been pregnant? # Q98 # Ndiyo
        'QN127', # Have you ever tested for HIV? # Q127
        'QN128', # Have you ever been diagnosed with any of the STI’s? Q128
    ]

    def _filter(row):
        for ic in selection_criteria:
            if row[ic] == "Ndiyo":
                return 1
        return 0

    def _score(row):
        for ic in inclusion_criteria:
            if row[ic] == "Ndiyo":
                return 1
        return 0

    # df[selection_criteria].map({"Yes": 1, "No": 0}).any()
    filtered_df = df[df[selection_criteria].apply(_filter, axis=1) == 1]
    results = filtered_df[inclusion_criteria].apply(_score, axis=1)

    return results


def load(file_path):
    df = pd.read_stata(file_path)

    def _age_to_agegroup(age):
        if age < 10:
            return "0-9"
        elif age < 15:
            return "10-14"
        elif age < 20:
            return "15-19"
        else:
            return ">19"

    df['regions'] = df['QN1']
    df['agegroup'] = df['age'].map(_age_to_agegroup)
    df['sex'] = df['QN14'].map({'Mme': 'Male', 'Mke': 'Female'})

    return df
