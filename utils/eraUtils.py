
def get_date_from_era(era):
    era_to_date = {
        "2011": "Mar 2011 - Dec 2011",
        "2012": "Apr 2012 - Dec 2012",
        "2013": "Jan 2013 - Feb 2013",
        "2015": "June 2015 - Nov 2015",
        "2016": "Apr 2016 - Dec 2016",
        "2017": "May 2017 - Dec 2017",
        "2018": "Apr 2018 - Dec 2018",
        "run1": "Mar 2011 - Feb 2013",
        "run2": "June 2015 - Dec 2018",
        "run1_and_run2": "Mar 2011 - Dec 2018",
    }
    return era_to_date[era]


def get_phase_from_fill(fill):
    if not isinstance(fill, int):
        fill = int(fill)

    if fill >= 1005 and fill <= 5576:
        return 0
    elif fill >= 5659:
        return 1


def get_fills_for_era(era):

    fills_2012 = list(range(3114, 3819))
    fills_2015 = list(range(3819, 4851))
    fills_2016 = list(range(4851, 5457))
    fills_2017 = list(range(5698, 6467))
    fills_2018 = list(range(6467, 7495))
    fills_run1 = fills_2012
    # Quick and dirty hack, phase 0 does not work
    # fills_run2 = fills_2015 + fills_2016 + fills_2017 + fills_2018
    fills_run2 = fills_2017 + fills_2018
    fills_run1_and_run2 = fills_2015 + fills_2016 + fills_2017 + fills_2018

    return eval("fills_" + era)