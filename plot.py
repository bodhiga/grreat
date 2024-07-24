import seaborn as sns
from matplotlib import pyplot as plt

bodhi_blue = (0.0745, 0.220, 0.396)
bodhi_grey = (0.247, 0.29, 0.322)
bodhi_primary_1 = (0.239, 0.38, 0.553)
bodhi_secondary = (0.133, 0.098, 0.42)
bodhi_tertiary = (0.047, 0.396, 0.298)
bodhi_complement = (0.604, 0.396, 0.071)

color_palette = [bodhi_complement, bodhi_blue, bodhi_tertiary, bodhi_primary_1, bodhi_grey, bodhi_secondary]

#sns.color_palette("tab10")
sns.set_palette(color_palette)

def subplot():
    fig, ax = plt.subplots(1, 3,
                           sharey='all',
                           figsize=(10,5),
                           )

    return fig, ax


def category(df, x, y, title=None, xlabel=None, ylabel=None, hue=None, ax=None,targets=None):
    # sns.set_theme(style='whitegrid')
    sns.set_palette(color_palette)
    order_by = None
    if x is not None:
        order_by = df[x].unique().tolist()
        order_by.sort()

    hue_order = None
    if hue is not None:
        hue_order = df[hue].unique().tolist()
        hue_order.sort()

    g = sns.barplot(
        ax=ax,
        data=df,
        x=x, y=y,
        hue=hue,
        order=order_by,
        hue_order=hue_order,
        # errorbar=None,
        errorbar=("ci", 95),
        palette=color_palette, alpha=.9
    )

    if ax:
        ax.set(xlabel=None)
        ax.tick_params(axis='x', pad=2, labelsize=10)
        ax.tick_params(axis='y', pad=2, labelsize=10)
        ax.xaxis.label.set_size(10)
        ax.yaxis.label.set_size(10)
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles=handles, labels=labels, loc='best', fontsize='small')
        else:
            ax.legend().remove()

    if ax and targets:
        sorted_patches = sorted(ax.patches, key=lambda x: x.get_x())
        for idx, (yellow, green) in enumerate(targets):
            a = sorted_patches[idx]

            x_start = a.get_x()
            width = a.get_width()
            ax.plot([x_start, x_start + width], 2*[yellow], '--', c='y')
            ax.plot([x_start, x_start + width], 2*[green], '--', c='g')
    return g
