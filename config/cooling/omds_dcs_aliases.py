def omds_to_dcs_alias(omds_alias):
    """Correct DCS alias corresponding to OMDS alias.

    Args:
        omds_alias (str)

    Returns:
        str
    """

    # alias in database (OMDS): alias in DCS (correct)
    omds_to_dcs_alias_map = {
        # These aliases were not correct
        "4I_L1D2MN": "4R_L1D2MN",
        "4M_L1D2MN": "4I_L1D2MN",
        "4R_L1D2MN": "4M_L1D2MN",
        "3I_L2D1MN": "1I_L4D2MN",
        "3M_L2D1MN": "1M_L4D2MN",
        "3R_L2D1MN": "1R_L4D2MN",
        "4I_L2D2PN": "6R_L4D3PN",
        "4M_L2D2PN": "6M_L4D3PN",
        "4R_L2D2PN": "6I_L4D3PN",
        "2I_L3D1MN": "2R_L3D1MN",
        "2R_L3D1MN": "2I_L3D1MN",
        "5I_L3D3MN": "5R_L3D3MN",
        "5R_L3D3MN": "5I_L3D3MN",
        "1I_L4D2MN": "3I_L2D1MN",
        "1M_L4D2MN": "3M_L2D1MN",
        "1R_L4D2MN": "3R_L2D1MN",
        "6M_L4D3PN": "4M_L2D2PN",
        "6R_L4D3PN": "4R_L2D2PN",
        "6I_L4D4MN": "6R_L4D4MN",
        "6R_L4D4MN": "6I_L4D4MN",
        "3M_L1D1MF": "3I_L1D1MF",
        "3I_L1D1MF": "3M_L1D1MF",
        "3I_L2D1PF": "1I_L4D2PF",
        "3M_L2D1PF": "1M_L4D2PF",
        "3R_L2D1PF": "1R_L4D2PF",
        "2I_L3D1PF": "2M_L3D1PF",
        "2M_L3D1PF": "2I_L3D1PF",
        "2R_L3D2MF": "2I_L3D2MF",
        "2I_L3D2MF": "2R_L3D2MF",
        "1I_L4D2PF": "3I_L2D1PF",
        "1M_L4D2PF": "3M_L2D1PF",
        "1R_L4D2PF": "3R_L2D1PF",
        "6M_L4D3MF": "4M_L2D2MF",
        "6R_L4D3MF": "4R_L2D2MF",
        "4I_L2D2MF": "6I_L4D3MF",
        "4M_L2D2MF": "6M_L4D3MF",
        "4R_L2D2MF": "6R_L4D3MF",
        "6I_L4D4PF": "6R_L4D4PF",
        "6R_L4D4PF": "6I_L4D4PF",
        # These aliases were correct
        "5I_L3D4PN": "5I_L3D4PN",
        "1R_L4D1PN": "1R_L4D1PN",
        "5M_L3D4PN": "5M_L3D4PN",
        "1I_L4D1MF": "1I_L4D1MF",
        "6M_L4D4MN": "6M_L4D4MN",
        "1M_L4D1PN": "1M_L4D1PN",
        "1R_L4D1MF": "1R_L4D1MF",
        "5R_L3D4MF": "5R_L3D4MF",
        "2R_L3D1PF": "2R_L3D1PF",
        "1M_L4D1MF": "1M_L4D1MF",
        "5M_L3D4MF": "5M_L3D4MF",
        "1I_L4D1PN": "1I_L4D1PN",
        "3I_L1D1PN": "3I_L1D1PN",
        "4R_L1D2PF": "4R_L1D2PF",
        "3R_L1D1MF": "3R_L1D1MF",
        "6M_L4D4PF": "6M_L4D4PF",
        "4I_L1D2PF": "4I_L1D2PF",
        "2M_L3D2PN": "2M_L3D2PN",
        "2R_L3D2PN": "2R_L3D2PN",
        "5R_L3D3PF": "5R_L3D3PF",
        "5R_L3D4PN": "5R_L3D4PN",
        "5I_L3D3PF": "5I_L3D3PF",
        "5M_L3D3MN": "5M_L3D3MN",
        "5I_L3D4MF": "5I_L3D4MF",
        "2M_L3D2MF": "2M_L3D2MF",
        "3R_L1D1PN": "3R_L1D1PN",
        "5M_L3D3PF": "5M_L3D3PF",
        "2I_L3D2PN": "2I_L3D2PN",
    }

    if omds_alias not in omds_to_dcs_alias_map.keys():
        print(f"Error: {omds_alias} not not OMDS to DCS alias map!")
        return None

    return omds_to_dcs_alias_map[omds_alias]
