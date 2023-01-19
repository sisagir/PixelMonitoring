def get_fluence(readout_group, pp_cross_section, fluence_field, lumi):
    """Get fluence for a readout group.

    If lumi is instantaneous (fb-1.s-1), then will get instantaneous fluence
    (n_eq.cm-2.s-1)

    Args:
        readout_group (utils.modules.ReadoutGroup)
        pp_cross_section (float)
        fluence_field (ROOT.TH2D)
        lumi (float)
    
    Returns:
        float
    """

    return readout_group.getAverageFluence(fluence_field, lumi, pp_cross_section)

