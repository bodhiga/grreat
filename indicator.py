import pandas as pd
import itertools as itertools
import seaborn as sns

import indicators.adolescents as adolescents
import indicators.health as health
import indicators.satisfaction as satisfaction
import indicators.influencers as influencers
import indicators.baseline as baseline

import analysis as analysis
import table as table
import plot as plot

def get_targets(adf, eadf, hdf, ehdf, cidf, ecidf, csdf, ecsdf,bdf):
    return {
        "1000c": {
            "func": adolescents.indicator_1000,
            "dataframe": adf.loc[(adf["sex"] == "Female") & (adf['agegroup'].isin(['10-14', '15-19']))], # GIRLS ONLY! BUG looks like the baseline was calculated with both boys and girls?
            "endline_dataframe": eadf.loc[(eadf["sex"] == "Female") & (eadf['agegroup'].isin(['10-14', '15-19']))], # TODO Replace this with the endline dataframe
            "percent": False,
            "targets": {
                (): [0.582, 0.582 * 1.1],
                ("agegroup",): {
                    "10-14": [0.542, 0.542 * 1.1],
                    "15-19": [0.625, 0.625 * 1.1],
                },
                ("regions",): {
                    # NOTE "10% increase from baseline"
                    # is interpreted at 'percentage point' increase
                    # as there are a number of targets at zero, which means
                    # that percentage increase doesn't make sense.
                    "Mbeya": [0.621, 0.621 * 1.1],
                    "Songwe": [0.576, 0.576 * 1.1],
                    "Zanzibar": [0.536, 0.536 * 1.1],
                }
            }
        },
        "1100a": {
            "dataframe": hdf.drop_duplicates(subset="Q_3"),
            "endline_dataframe": ehdf,
            "func": health.indicator_1100a,
            "percent": True,
            "targets": {
                ("regions",): {
                    "Mbeya": [0.0, 0.0 + 0.1], # NOTE percentage _point_ increase
                    "Songwe": [0.0, 0.0 + 0.1],
                    "Zanzibar": [0.286, 0.286 * 1.1],
                },
            }
        },
        "1100b": {
            "dataframe": csdf,
            "endline_dataframe": ecsdf,
            "func": satisfaction.indicator_1100b,
            "percent": True,
            "targets": {
                ("regions",): {
                    "Mbeya": [0.35, 0.35 * 1.1],
                    "Songwe": [0.129, 0.129 * 1.1],
                    "Zanzibar": [0.488, 0.488 * 1.1],
                },
                ("agegroup",): {
                    "10-14": [0,0],
                    "15-19": [0,0],
                },
                ("sex",): {
                    "Male": [0,0],
                    "Female": [0,0],
                },
            }
        },
        "1113": {
            "dataframe": adf,
            "endline_dataframe": eadf,
            "func": adolescents.indicator_1113,
            "percent": True,
            "targets": {
                (): [0.0, 0.0],
                ("regions",): {
                    "Mbeya": [0.0, 0.0],
                    "Songwe": [0.0, 0.0],
                    "Zanzibar": [0.0, 0.0],
                },
            }
        },
        "1200a": {
            "dataframe": cidf,
            "endline_dataframe": ecidf,
            "func": influencers.indicator_1200a,
            "percent": True,
            "targets": {
                ("gender_support",): {
                    "Boys": [0.798, 0.798 * 1.1],
                    "Girls": [0.847, 0.847 * 1.1],
                },
                ("regions", "gender_support"): {
                    "Mbeya": {
                        "Boys": [0.833, 0.833 * 1.1],
                        "Girls": [0.929, min(0.929 * 1.1, 1)],
                    },
                    "Songwe": {
                        "Boys": [0.722, 0.722 * 1.1],
                        "Girls": [0.895, 0.895 * 1.1],
                    },
                    "Zanzibar": {
                        "Boys": [0.804, 0.804 * 1.1],
                        "Girls": [0.793, 0.793 * 1.1],
                    }
                }
            }
        },
        "1200b": {
            "dataframe": adf[adf["agegroup"] != "0-9"],
            "endline_dataframe": eadf[eadf["agegroup"] != "0-9"],
            "func": adolescents.indicator_1200b,
            "percent": True,
            "targets": {
                ("regions",): {
                    "Mbeya": [0.156, 0.156 * 1.1],
                    "Songwe": [0.08642, 0.08642 * 1.1],
                    "Zanzibar": [0.013333333, 0.013333333 * 1.1],
                },
                ("sex",): {
                    "Male": [0.132978723 , 0.132978723 * 1.1],
                    "Female": [0.086614173 , 0.086614173 * 1.1],
                },
                ("agegroup",): {
                    "10-14": [0.031055901 , 0.031055901 * 1.1],
                    "15-19": [0.149466192 , 0.149466192 * 1.1],
                },
                ("sex","agegroup",): {
                    "Male": {
                        "10-14": [0.057142857 , 0.057142857 * 1.1],
                        "15-19": [0.177966102 , 0.177966102 * 1.1],
                    },
                    "Female": {
                        "10-14": [0.010989011 , 0.010989011 * 1.1],
                        "15-19": [0.128834356 , 0.128834356 * 1.1],
                    }
                },
            }
        },
        # "1200b_baseline": {
        #     "dataframe": bdf[bdf["agegroup"] != "0-9"],
        #     "endline_dataframe": bdf[bdf["agegroup"] != "0-9"], # TODO Replace with endline dataframe
        #     "func": baseline.indicator_1200b,
        #     "percent": True,
        #     "targets": {
        #         ("regions",): {
        #             "Mbeya": [0, 0],
        #             "Songwe": [0, 0],
        #             "Zanzibar": [0, 0],
        #         },
        #         ("sex",): {
        #             "Male": [0, 0],
        #             "Female": [0, 0],
        #         },
        #         ("agegroup",): {
        #             "10-14": [0, 0],
        #             "15-19": [0, 0],
        #         },
        #         ("sex","agegroup",): {
        #             "Male": {
        #                 "10-14": [0, 0],
        #                 "15-19": [0, 0],
        #             },
        #             "Female": {
        #                 "10-14": [0, 0],
        #                 "15-19": [0, 0],
        #             }
        #         },
        #     }
        # },
        "1210": {
            "func": adolescents.indicator_1210,
            "dataframe": adf,
            "endline_dataframe": eadf,
            "percent": True,
            "targets": {
                (): [0.764, 0.764 * 1.1],
                ("sex",): {
                    "Female": [0.754, 0.754 * 1.1],
                    "Male": [0.779, 0.779 * 1.1]
                },
                ("regions", "sex"): {
                    "Mbeya": {
                        "Female": [0.756, 0.756 * 1.1], # NOTE flipped male/female order to match baseline report
                        "Male": [0.847, 0.847 * 1.1],
                    },
                    "Songwe": {
                        "Female": [0.754, 0.754 * 1.1],
                        "Male": [0.745, 0.745 * 1.1],
                    },
                    "Zanzibar": {
                        "Female": [0.75, 0.75 * 1.1],
                        "Male": [0.731, 0.731 * 1.1],
                    }
                }
            }
        },
        "1220a": {
            # NOTE the numbers are very small here,
            # I don't think neither we, nor the survey has the statistical power
            # to draw any conclusions from this data
            "func": adolescents.indicator_1220a,
            "dataframe": adf,
            "endline_dataframe": eadf,
            "percent": True,
            "targets": {
                ("regions",): {
                    "Mbeya": [0.014, 0.014 * 1.1],
                    "Songwe": [0.008, 0.008 * 1.1],
                    "Zanzibar": [0.006, 0.006 * 1.1],
                },
                ("regions", "sex"): {
                    "Mbeya": {
                        "Male": [0.005, 0.005 * 1.1],
                        "Female": [0.02, 0.02 * 1.1],
                    },
                    "Songwe": {
                        "Male": [0.005, 0.005 * 1.1],
                        "Female": [0.01, 0.01 * 1.1],
                    },
                    "Zanzibar": {
                        "Male": [0.0, 0.005 * 1.1],
                        "Female": [0.009, 0.009 * 1.1],
                    }
                }
            }
        },
        "1220a_hiv": {
            "func": adolescents.indicator_1220hiv,
            "dataframe": adf,
            "endline_dataframe": eadf,
            "percent": True,
            "targets": {
                ("regions",): {
                    "Mbeya": [0, 0],
                    "Songwe": [0, 0],
                    "Zanzibar": [0, 0],
                },
                ("regions", "sex"): {
                    "Mbeya": {
                        "Male": [0, 0],
                        "Female": [0, 0],
                    },
                    "Songwe": {
                        "Male": [0, 0],
                        "Female": [0, 0],
                    },
                    "Zanzibar": {
                        "Male": [0, 0],
                        "Female": [0, 0],
                    },
                },
            },
        },
        "1220a_fp": {
            "func": adolescents.indicator_1220fp,
            "dataframe": adf,
            "endline_dataframe": eadf,
            "percent": True,
            "targets": {
                ("regions",): {
                    "Mbeya": [0, 0],
                    "Songwe": [0, 0],
                    "Zanzibar": [0, 0],
                },
                ("regions", "sex"): {
                    "Mbeya": {
                        "Male": [0, 0],
                        "Female": [0, 0],
                    },
                    "Songwe": {
                        "Male": [0, 0],
                        "Female": [0, 0],
                    },
                    "Zanzibar": {
                        "Male": [0, 0],
                        "Female": [0, 0],
                    },
                },
            },
        },

        "1220a_nutri": {
            "func": adolescents.indicator_1220nutri,
            "dataframe": adf,
            "endline_dataframe": eadf,
            "percent": True,
            "targets": {
                ("regions",): {
                    "Mbeya": [0, 0],
                    "Songwe": [0, 0],
                    "Zanzibar": [0, 0],
                },
                ("regions", "sex"): {
                    "Mbeya": {
                        "Male": [0, 0],
                        "Female": [0, 0],
                    },
                    "Songwe": {
                        "Male": [0, 0],
                        "Female": [0, 0],
                    },
                    "Zanzibar": {
                        "Male": [0, 0],
                        "Female": [0, 0],
                    },
                },
            },
        },
        "1220ab": {
            # NOTE the numbers are very small here,
            # I don't think neither we, nor the survey has the statistical power
            # to draw any conclusions from this data
            "func": adolescents.indicator_1220ab,
            "dataframe": adf,
            "endline_dataframe": eadf,
            "percent": True,
            "targets": {
                (): [0.147, 0.147 * 1.1],
                ("regions",): {
                    "Mbeya": [0.146, 0.146 * 1.1],
                    "Songwe": [0.171, 0.171 * 1.1],
                    "Zanzibar": [0.112, 0.112 * 1.1],
                },
                ("sex",): {
                    "Male": [0.116, 0.116 * 1.1],
                    "Female": [0.167, 0.167 * 1.1],
                },
            }
        },
        "1300b": {
            "func": adolescents.indicator_1300b,
            "dataframe": adf,
            "endline_dataframe": eadf,
            "percent": True,
            "targets": {
                ("regions",): {
                    "Mbeya": [0.051, 0.051 * 1.1],
                    "Songwe": [0.034, 0.034 * 1.1],
                    "Zanzibar": [0.0, 0.1], # NOTE set in line with Songwe
                },
                ("sex",): {
                    "Male": [0, 0],
                    "Female": [0, 0],
                },
            }
        },
}

def _target_gen(indict, acc = None):
    acc = acc[:] if acc else []
    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                for d in _target_gen(value, acc + [key]):
                    yield d
            else:
                yield acc + [key, value]
    else:
        yield acc + [indict]

def process(adf,eadf,hdf,ehdf,cidf,ecidf,csdf,ecsdf,bdf):
    _targets = get_targets(adf,eadf,hdf,ehdf,cidf,ecidf,csdf,ecsdf,bdf)


    for name, indicator in _targets.items():
        f = None

        try:
            f = indicator["func"]
        except KeyError:
            print('No func for {name}'.format(name=name))
            f = lambda x: x
            continue

        targets = None
        try:
            targets = indicator["targets"]
        except KeyError:
            print('No target for {}'.format(name))
            continue

        for cols in targets.keys():
            assert type(cols) == tuple

            df = indicator["dataframe"]
            edf = indicator["endline_dataframe"]

            values = indicator["targets"][cols]
            sequences = _target_gen(values)

            for seq in sequences:
                filtered_df = df
                filtered_edf = edf
                for idx, x in enumerate(seq[:-1]):
                    col = cols[idx]
                    filtered_df = filtered_df.loc[filtered_df[col] == x]
                    filtered_edf = filtered_edf.loc[filtered_edf[col] == x]

                [baseline, pmf_target] = seq[-1]
                midline_target = (baseline + pmf_target) / 2

                alternative = 'less'
                if baseline <= pmf_target:
                    alternative = 'greater'
                # Run the analysis here


                print('Running analysis on {indicator}: {cols} - {seq}'.format(indicator=name, cols=cols, seq=seq[:-1]))
                print('Baseline {bl}, midline target: {m} and PMF target: {pmf}'.format(bl=baseline, pmf=pmf_target, m=midline_target))

                result = f(filtered_df, endline=False)
                eresult = f(filtered_edf, endline=True)
                pmf_test_results = analysis.ttest(eresult, pmf_target, alternative=alternative)
                midline_test_results = analysis.ttest(result, midline_target, alternative=alternative)
                mean = result.mean()
                emean = eresult.mean()

                print('Mean midline: {mu}, p-value (Midline target): {mp}\nMean endline: {mue}, p-value (PMF): {p}'.format(mu=mean, mue=emean, p=pmf_test_results.pvalue, mp=midline_test_results.pvalue))
                print()
            pass

            result = f(df, endline=False)
            eresult = f(edf, endline=True)
            result2 = pd.concat([result, df[list(cols)]], axis=1)
            eresult2 = pd.concat([eresult, edf[list(cols)]], axis=1)
            result2["indicator"] = result2[0]
            eresult2["indicator"] = eresult2[0]

            if indicator["percent"]:
                result2["indicator"] = result2["indicator"].apply(lambda x: x * 100)
                eresult2["indicator"] = eresult2["indicator"].apply(lambda x: x * 100)

            x = cols[0] if len(cols) > 0 else None
            hue = None
            if len(cols) >= 2:
                hue = cols[1]

            g, _axes = plot.subplot()
            _axes[0].set_title("Baseline")
            _axes[1].set_title("Midline")
            _axes[2].set_title("Endline")

            baseline_data = []
            all_targets = []
            target_list = list(_target_gen(values))
            target_list.sort(key=lambda x: " ".join(x[:-1]))

            for seq in target_list:
                baseline_data.append(seq[0:-1] + [seq[-1][0]])
                all_targets.append([(seq[-1][0] + seq[-1][1])/2,seq[-1][1]])

            baseline_df = pd.DataFrame(baseline_data,
                                           columns=list(cols) + ["indicator"])
            if indicator["percent"]:
                baseline_df["indicator"] = baseline_df["indicator"].apply(lambda x: x * 100)
                all_targets = [[t1 * 100, t2 * 100] for [t1, t2] in all_targets]

            def _add_labels(ax, mul=1, suffix=''):
                ax.set(ylabel="")
                #ax = fig.facet_axis(0, 0)
                for container in ax.containers:
                    if suffix == '%':
                        labels = [f'{(v.get_height() * mul):.1f}' + suffix for v in container]
                        ax.bar_label(container, labels=labels, label_type='edge', padding=-8, color ='white', fontsize=6.5, fontweight='bold')
                        ax.set_ylim(0, 100)
                    else:
                        labels = [f'{(v.get_height() * mul):.2f}' + suffix for v in container]
                        ax.bar_label(container, labels=labels, label_type='edge', padding=-9, color ='white', fontsize=7.3, fontweight='bold')

            baseline = plot.category(baseline_df, x, "indicator",
                              title='Indicator {}'.format(name),
                                     hue=hue, ax=_axes[0],
                                     targets=all_targets)
            mul = (1 if indicator["percent"] else 1)
            suffix =  ('%' if indicator["percent"] else '')
            _add_labels(_axes[0], mul=mul, suffix=suffix)

            midline = plot.category(result2, x, "indicator",
                              title='Indicator {}'.format(name),
                                    hue=hue,
                                    ax=_axes[1],
                                    targets=all_targets)

            _add_labels(_axes[1], mul=mul, suffix=suffix)

            endline = plot.category(eresult2, x, "indicator",
                                    title='Inidicator {}'.format(name),
                                    hue=hue, ax=_axes[2],
                                    targets=all_targets,
                                    )
            _add_labels(_axes[2], mul=mul, suffix=suffix)

            figure_name = '_'.join(['indicator_{}'.format(name)] + list(cols))
            figure_path = './output/figures/{}.png'.format(figure_name)
            g.savefig(figure_path,dpi=500)

            if(len(cols) >= 2):
                ctdf = table.crosstab(eresult2, "indicator", cols[0], cols[1:])
                table.crosstab_to_xlsx(ctdf, "./output/data/{}.xlsx".format(figure_name))
        print()


def dashboard(adf, eadf, hdf, cidf, ecidf, csdf, ecsdf, bdf, ehdf): # TODO
        _targets = get_targets(adf=adf,
                               eadf=eadf,
                               hdf=hdf,
                               ehdf=ehdf,
                               cidf=cidf,
                               ecidf=ecidf,
                               csdf=csdf,
                               ecsdf=ecsdf,
                               bdf=bdf
                               )
        _expected_results = {
            "1000": ["1000c"],
            "1100": ["1100a", "1100b"],
            "1113": ["1113"],
            "1200": ["1200a", "1200b"],
            "1300": ["1300b"],
            "1210": ["1210"],
            "1220": ["1220a"],
        }

        _expected_results_description = {
            "1000": "Adolescent girls in Mbeya and Songwe regions of Tanzania Mainland and in Zanzibar are able to realize their sexual and reproductive health rights (SRHR) and nutrition rights.",
        }

        def _disaggs(f, df, edf, disaggregations):
            results = []
            for cols in disaggregations.keys():
                values = disaggregations[cols]
                sequences = _target_gen(values)

                for seq in sequences:
                    name = ", ".join(cols)

                    [baseline, pmf_target] = seq[-1]
                    midline_target = (baseline + pmf_target) / 2

                    alternative = 'less'
                    if baseline <= pmf_target:
                        alternative = 'greater'

                    filtered_df = df
                    filtered_edf = edf
                    for idx, x in enumerate(seq[:-1]):
                        col = cols[idx]
                        filtered_df = filtered_df.loc[filtered_df[col] == x]
                        filtered_edf = filtered_edf.loc[filtered_edf[col] == x]

                    disagg_by_values = ", ".join(seq[:-1])
                    result = f(filtered_df, endline=False)
                    eresult = f(filtered_edf, endline=True)
                    pmf_test_results = analysis.ttest(eresult, pmf_target, alternative=alternative)
                    midline_test_results = analysis.ttest(result, midline_target, alternative=alternative)
                    midline_mean = result.mean()
                    mean = eresult.mean()

                    results.append({
                        "name": name,
                        "disagg_by_values": disagg_by_values,
                        "value": mean,
                        "midline_value": midline_mean,
                        "pmf_target": pmf_target,
                        "midline_target": midline_target,
                        "baseline_value": baseline,
                        "pmf_p": pmf_test_results.pvalue,
                        "midline_p": midline_test_results.pvalue,
                    })
            return results

        def _indicators(indicators):
            results = []
            for indicator in indicators:
                targets = _targets[indicator]["targets"]
                f = _targets[indicator]["func"]
                df = _targets[indicator]["dataframe"]
                edf = _targets[indicator]["endline_dataframe"]
                results.append({
                    "name": indicator,
                    "disaggregations": _disaggs(f, df, edf, targets),
                })

            return results
        dashboard = []
        for [outcome, indicators] in _expected_results.items():
            dashboard.append({
                "expected_results": outcome,
                "indicators": _indicators(indicators)
            })

        d2 = pd.json_normalize(dashboard, record_path=['indicators', 'disaggregations'], meta=['expected_results', ['indicators', 'name']])
        d2[[
            "expected_results",
            "indicators.name",
            'name',
            'disagg_by_values',
            "midline_target",
            "pmf_target",
            "baseline_value",
            "value",
            "midline_value",
            "pmf_p",
            "midline_p",
        ]].to_excel('./output/dashboard.xlsx')

        # TODO
        # adolescents.indicator_1300b_tables(adf)

def gei_breakdown(df, edf):
    dimensions = {
        "Self-perception and personal changes": {
            'key': 'self_perception',
            'baseline': {
                "regions": {
                    "Mbeya": [0.095, 0.885, 0.02],
                    "Songwe": [0.069, 0.886, 0.066],
                    "Zanzibar": [0.032, 0.912, 0.056],
                },
                'agegroup': {
                    '10-14': [0.033, 0.889, 0.078],
                    '15-19': [0.107, 0.88, 0.013],
                },
                'overall': [0.069, 0.885, 0.047],
            }
        },
        'Personal freedom': {
            'key': 'personal_freedom',
            'baseline': {
                'regions': {
                    'Mbeya': [0.031, 0.739, 0.231],
                    'Songwe': [0.039, 0.649, 0.312],
                    'Zanzibar': [0.009, 0.63, 0.341],
                },
                'agegroup': {
                    '10-14': [0.026, 0.6, 0.374],
                    '15-19': [0.031, 0.769, 0.21],
                },
                'overall': [0.028, 0.677, 0.295],
            }
        },
        'Access to and Control Over Resources': {
            'key': 'access_to_and_control_over_resources',
            'baseline': {
                'regions': {
                    'Mbeya': [0.007, 0.97, 0.024],
                    'Songwe': [0.033, 0.941, 0.026],
                    'Zanzibar': [0.051, 0.907, 0.042],
                },
                'agegroup': {
                    '10-14': [0.035, 0.929, 0.035],
                    '15-19': [0.021, 0.957, 0.023],
                },
                'overall': [0.028, 0.942, 0.029],
            }
        },
        'Decision and influence': {
            'key': 'decision_and_influence',
            'baseline': {
                'regions': {
                    'Mbeya': [0.332, 0.576, 0.069],
                    'Songwe': [0.295, 0.577, 0.11],
                    'Zanzibar': [0.139, 0.62, 0.192],
                },
                'agegroup': {
                    '10-14': [0.254, 0.551, 0.162],
                    '15-19': [0.281, 0.629, 0.068],
                },
                'overall': [0.267, 0.588, 0.117],
            },
        },
        'Care and unpaid works': {
            'key': 'care_and_unpaid_works',
            'baseline': {
                'regions': {
                    'Mbeya': [0.342, 0.359, 0.298],
                    'Songwe': [0.18, 0.305, 0.515],
                    'Zanzibar': [0.255, 0.306, 0.44],
                },
                'agegroup': {
                    '10-14': [0.207, 0.311, 0.482],
                    '15-19': [0.315, 0.34, 0.345],
                },
                'overall': [0.259, 0.325, 0.417],
            },
        },
        'Knowledge on nutrition': {
            'key': 'knowledge_and_nutrition',
            'baseline': {
                'regions': {
                    'Mbeya': [0.076, 0.817, 0.107],
                    'Songwe': [0.053, 0.885, 0.063],
                    'Zanzibar': [0.076, 0.788, 0.137],
                },
                'agegroup': {
                    '10-14': [0.059, 0.8, 0.127],
                    '15-19': [0.074, 0.849, 0.067],
                },
                'overall': [0.066, 0.824, 0.11],
            }
        },
        'Support from social network': {
            'key': 'support_from_social_network',
            'baseline': {
                'regions': {
                    'Mbeya': [0.407, 0.0, 0.593],
                    'Songwe': [0.639, 0.0, 0.361],
                    'Zanzibar': [0.278, 0.0, 0.722],
                },
                'agegroup': {
                    '10-14': [0.355, 0.0, 0.645],
                    '15-19': [0.573, 0.0, 0.427],
                },
                'overall': [0.46, 0.0, 0.54],
            }
        },
        'Control over the body': {
            'key': 'control_over_body',
            'baseline': {
                'regions': {
                    'Mbeya': [0.258, 0.678, 0.064],
                    'Songwe': [0.125, 0.712, 0.164],
                    'Zanzibar': [0.046, 0.759, 0.194],
                },
                'agegroup': {
                    '10-14': [0.087, 0.694, 0.219],
                    '15-19': [0.223, 0.732, 0.046],
                },
                'overall': [0.152, 0.712, 0.136],
            }
        },
        'Leadership': {
            'key': 'leadership',
            'baseline': {
                'regions': {
                    'Mbeya': [0.132, 0.695, 0.15],
                    'Songwe': [0.161, 0.639, 0.173],
                    'Zanzibar': [0.171, 0.407, 0.349],
                },
                'agegroup': {
                    '10-14': [0.165, 0.553, 0.282],
                    '15-19': [0.141, 0.647, 0.212],
                },
                'overall': [0.153, 0.598, 0.249],
            },
        },
        'Economic empowerment': {
            'key': 'economic_empowerment',
            'baseline': {
                'regions': {
                    'Mbeya': [0.668, 0.0, 0.332],
                    'Songwe': [0.472, 0.0, 0.528],
                    'Zanzibar': [0.482, 0.0, 0.519],
                },
                'agegroup': {
                    '10-14': [0.485, 0.0, 0.515],
                    '15-19': [0.611, 0.0, 0.389],
                },
                'overall': [0.545, 0.0, 0.455],
            }
        },
        'Girl Empowerment Index': {
            'key': 'aggregate',
            'baseline': {
                'regions': {
                    'Mbeya': [0.017, 0.963, 0.02],
                    'Songwe': [0.0, 0.934, 0.066],
                    'Zanzibar': [0.0, 0.852, 0.148],
                },
                'agegroup': {
                    '10-14': [0.0, 0.88, 0.12],
                    '15-19': [0.013, 0.969, 0.018],
                },
                'overall': [0.006, 0.923, 0.071],
            }
        }
    }

    def _bloom(df):
        """Apply Bloom's Taxonomy to the dataframe"""

        def _categorise(value):
            if value < 60:
                return "Most disempowered"
            elif value < 80:
                return "Disempowered"
            else:
                return "Empowered"

        return df.apply(_categorise)

    output = pd.DataFrame()
    eoutput = pd.DataFrame()
    results = adolescents.indicator_1000_v2(df, endline=False)
    eresults = adolescents.indicator_1000_v2(edf, endline=True)

    for d, v in dimensions.items():
        key = v['key']
        for disagg, values in v['baseline'].items():
            for value in values:
                output[key] = _bloom(results[key])
                eoutput[key] = _bloom(eresults[key])

    output = output.assign(study='midline')
    eoutput = eoutput.assign(study='endline')
    output = pd.concat([output, eoutput]) # TODO
    output['regions'] = df['regions']
    output['agegroup'] = df['agegroup']

    output2 = []
    for d, v in dimensions.items():
        key = v['key']
        ct = pd.crosstab(
            pd.Categorical(output[key], categories=['Empowered', 'Disempowered', 'Most disempowered']),
            [output["regions"]], normalize='columns', dropna=False, margins=True, margins_name="All (regions)")
        for region, baseline_values in v['baseline']['regions'].items():
            ct[region + ' (baseline)'] = baseline_values
        ct2 = pd.crosstab(
            pd.Categorical(output[key], categories=['Empowered', 'Disempowered', 'Most disempowered']),
            [output["agegroup"]], normalize='columns', dropna=False, margins=True, margins_name="All (agegroups)")
        for ag, baseline_values in v['baseline']['agegroup'].items():
            ct2[ag + ' (baseline)'] = baseline_values
        header = pd.DataFrame()
        header["name"] = [key]
        output2.append(header)
        output2.append(pd.concat([ct, ct2], axis=1))

        x = 'regions'
        y = key
        plotdata = (output.groupby(by=[x, 'study'])[y].value_counts(normalize=True) .mul(100) .rename('percent') .reset_index())
        plotdata['study'] = pd.Categorical(plotdata['study'], categories=['baseline', 'midline', 'endline'], ordered=True)
        plotdata[key] = pd.Categorical(plotdata[key], categories=['Empowered', 'Disempowered', 'Most disempowered'], ordered=True)

        overall_breakdown = output.groupby(by=['study'])[y].value_counts(normalize=True).rename('percent').reset_index()

        overall_breakdown.to_excel('./output/gei_breakdown_overall.xlsx')

        overall = v['baseline']['overall']

        overall_breakdown = overall_breakdown.append({'study': 'baseline', key: 'Empowered', 'percent': overall[0] }, ignore_index=True)
        overall_breakdown = overall_breakdown.append({'study': 'baseline', key: 'Disempowered', 'percent': overall[1]}, ignore_index=True)
        overall_breakdown = overall_breakdown.append({'study': 'baseline', key: 'Most disempowered', 'percent': overall[2]}, ignore_index=True)

        sns_plot = sns.catplot(overall_breakdown,x=key,y='percent', hue='study', errorbar=None, kind='bar', hue_order=['baseline', 'midline', 'endline'], order=['Empowered', 'Disempowered', 'Most disempowered'], alpha=.9)
        ax = sns_plot.facet_axis(0, 0)
        for container in ax.containers:
            labels = [f'{(v.get_height() * 100):.1f}%' for v in container]
            ax.bar_label(container, labels=labels, label_type='edge', fontsize=8.5)
            ax.set_ylim(0, 1)

        sns_plot.set(xlabel=d)

        fig =sns_plot.figure

        figure_name="./output/figures/gei_breakdown_all_{key}.png".format(region=region, key=key)
        fig.savefig(figure_name,dpi=500)

        for disagg in ['regions', 'agegroup']:
            for region, bl in v['baseline'][disagg].items():
                plotdata = plotdata.append({disagg: region, 'study': 'baseline', key: 'Empowered', 'percent': bl[0] * 100}, ignore_index=True)
                plotdata = plotdata.append({disagg: region, 'study': 'baseline', key: 'Disempowered', 'percent': bl[1] * 100}, ignore_index=True)
                plotdata = plotdata.append({disagg: region, 'study': 'baseline', key: 'Most disempowered', 'percent': bl[2] * 100}, ignore_index=True)

                plotdata = plotdata.append({disagg: region, 'study': 'overall', key: 'Empowered', 'percent': overall[0] * 100}, ignore_index=True)
                plotdata = plotdata.append({disagg: region, 'study': 'overall', key: 'Disempowered', 'percent': overall[1] * 100}, ignore_index=True)
                plotdata = plotdata.append({disagg: region, 'study': 'overall', key: 'Most disempowered', 'percent': overall[2] * 100}, ignore_index=True)

            for region, bl in v['baseline'][disagg].items():
                filtered_data = plotdata[plotdata[disagg] == region]
                sns_plot = sns.catplot(plotdata[plotdata[disagg] == region],x=key,y='percent', hue='study', errorbar=None, kind='bar', hue_order=['baseline', 'midline', 'endline'], order=['Empowered', 'Disempowered', 'Most disempowered'], alpha=.9)
                sns_plot.set(xlabel=d)

                fig =sns_plot.figure

                figure_name="./output/figures/gei_breakdown_{region}_{key}.png".format(region=region, key=key)
                fig.savefig(figure_name,dpi=500)
                filtered_data.to_excel('./output/gei_breakdown_{region}_{key}.xlsx'.format(region=region, key=key))

    gei_breakdown_result = pd.concat(output2)
    gei_breakdown_result.to_excel('./output/gei_breakdown.xlsx')

def demographics(df):
    result = df['Q_6'].value_counts()
    print("Total demographic count is: {}".format(result.sum()))
    return result
