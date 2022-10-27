import cx_Oracle


def fetch(query, user = "cms_pix_runinfo", caching = True):

    try:

        if user == "cms_pix_runinfo":
            connection = cx_Oracle.connect('cms_pix_runinfo/run2009info@cms_omds_adg')
        elif user == "cms_pixel_monitoring":
            connection = cx_Oracle.connect('cms_pixel_monitoring/2019PIXELcms@cms_omds_adg')
        else:
            connection = cx_Oracle.connect('cms_trk_r/1A3C5E7G:FIN@cms_omds_adg')

        cursor = connection.cursor()
        cursor.execute(str(query))
        result = cursor.fetchall()  
        connection.close()
  
        return result

    except Exception as e:

        raise Exception("Error while querying the OMDS database :-(<p> <b>Details:</b> <br>%s " % str(e))


# define some common db queries:

def get_timestamps(run_number):
    rows = fetch("select distinct DIPTIME from CMS_BEAM_COND.CMS_BRIL_LUMINOSITY where RUN=%s order by DIPTIME" % run_number)
    return [item[0] for item in rows]

def get_start_stop_timestamps(first_run, last_run):
    rows = fetch("select RUN, min(DIPTIME), max(DIPTIME) from CMS_BEAM_COND.CMS_BRIL_LUMINOSITY where RUN>=%s and RUN<=%s group by RUN" % (first_run, last_run))
    return [item[0] for item in rows]

def get_runs_from_fill(fill_number):
    rows = fetch("select distinct RUN from CMS_BEAM_COND.CMS_BRIL_LUMINOSITY where FILL=%s order by RUN" % fill_number)
    return [item[0] for item in rows]

def get_runs_from_timerange(time_start, time_stop):
    rows = fetch("select distinct RUN from CMS_BEAM_COND.CMS_BRIL_LUMINOSITY where DIPTIME>=TO_TIMESTAMP('%s', 'RRRR-MM-DD HH24:MI:SS.FF') AND DIPTIME<=TO_TIMESTAMP('%s', 'RRRR-MM-DD HH24:MI:SS.FF') order by RUN" % (time_start, time_stop))
    return [item[0] for item in rows]
 
