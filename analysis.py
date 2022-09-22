from scipy import stats

def ttest(df, popmean, alternative='less'):
    result = stats.ttest_1samp(df,
                    popmean,
                    axis=0,
                    nan_policy='omit',
                    alternative=alternative,
                    )
    return result

def breakdown(df, columns):
    for col in columns:
        c = col if isinstance(col, list) else [col]
        result = df[c].value_counts()
        total = result.sum()
        print(result)
        print(total)
        print()

def holm_bonferroni(target_alpha, hypotheses):

    # https://www.statisticshowto.com/holm-bonferroni-method/
    #
    n = len(hypotheses)

    # Step 1: Order the p-values from smallest to greatest:
    sorted_hypotheses = sort(hypotheses)

    # Step 2: Work the Holm-Bonferroni formula for the first rank:
    # HB = Target α / (n – rank + 1)
    # HB = .05 / 4 – 1 + 1 = .05 / 4 = .0125.
    #
    #Step 3: Compare the first-ranked (smallest) p-value from Step 1 to the alpha level calculated in Step 2:
    # Smallest p-value, in Step 1 (H4 = 0.005) < Alpha level in Step 2 (.0125).
    # If the p-value is smaller, reject the null hypothesis for this individual test.

    # The p-value of .005 is less than .0125, so the null hypothesis for H4 is rejected.

    # The testing stops when you reach the first non-rejected hypothesis. All subsequent hypotheses are non-significant (i.e. not rejected).
