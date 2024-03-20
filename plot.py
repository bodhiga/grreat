import seaborn as sns
from matplotlib import pyplot as plt


sns.color_palette("tab10")

def subplot():
    fig, ax = plt.subplots(1, 2,
                           sharey='all',
                           figsize=(10,5),
                           )

    return fig, ax


def category(df, x, y, title=None, xlabel=None, ylabel=None, hue=None, ax=None,targets=None):
    # sns.set_theme(style='whitegrid')
    sns.color_palette("tab10")
    order_by = None
    if x is not None:
        # import pdb; pdb.set_trace()
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
        palette="dark", alpha=.6
    )

    if ax:
        ax.set(xlabel=None)

    if ax and targets:
        sorted_patches = sorted(ax.patches, key=lambda x: x.get_x())
        for idx, (yellow, green) in enumerate(targets):
            a = sorted_patches[idx]

            x_start = a.get_x()
            width = a.get_width()
            ax.plot([x_start, x_start + width], 2*[yellow], '--', c='y')
            ax.plot([x_start, x_start + width], 2*[green], '--', c='g')
    return g
