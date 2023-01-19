from utils.constants import CELSIUS_TO_KELVIN


def set_font_size_and_offset(graph):
    """Set consistent font, size and offet for graphs.

    Args:
        graph (ROOT.TH1)
    """

    graph.GetXaxis().SetLabelSize(0.045)
    graph.GetYaxis().SetLabelSize(0.045)
    graph.GetXaxis().SetTitleSize(0.05)
    graph.GetYaxis().SetTitleSize(0.05)
    graph.GetXaxis().SetTitleOffset(1.2)
    graph.GetYaxis().SetTitleOffset(1.35)


def make_y_axis_title(
        text,
        unit="#muA",
        target_temperature=None,
        normalize_to_volume=False,
        normalize_to_number_of_rocs=False,
    ):

    if normalize_to_number_of_rocs:
        unit += " / ROC"

    if normalize_to_volume:
        unit += " / cm^{3}"
    
    if target_temperature is not None:
        correction =  "(corr. to %d #circC)" % (target_temperature - CELSIUS_TO_KELVIN)
    else:
        correction = ""

    title = "%s [%s] %s" % (text, unit, correction)
    if title.endswith(" "): title = title[:-1]

    return title

