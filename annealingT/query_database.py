import cx_Oracle
import datetime
import ast
import hashlib
import subprocess
import multiprocessing

def fetch(query, user = "cms_pix_runinfo", caching = False, cache_file_name = "queries.cache"):

    query_hashed = hashlib.md5(query).hexdigest()
    
    result = ""
    if caching:
        with open(cache_file_name, 'a+') as f:
            save_next_line = False
            for count, line in enumerate(f, start=1):
                if (count+1) % 3 == 0:
                    if query_hashed + "\n" == line:
                        save_next_line = True
                        continue
                if save_next_line:
                    result = eval(line)
                    break

    if result == "":
        if user == "cms_pix_runinfo":
            connection = cx_Oracle.connect('cms_pix_runinfo/run2009info@cms_omds_adg')
        elif user == "cms_trk_r":
            connection = cx_Oracle.connect('cms_trk_r/1A3C5E7G:FIN@cms_omds_adg')
        elif user == "cms_pixel_monitoring":
            connection = cx_Oracle.connect('cms_pixel_monitoring/CMS2018Pixel@cms_omds_adg')

        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

        if caching:
            with open(cache_file_name, 'a+') as f:
                query = query.replace('\n', ' ')
                f.write(query + '\n' + query_hashed + '\n' + str(result) + '\n')
            
    return result


# define some common db queries:

def get_timestamps(run_number):
    rows = fetch("select distinct DIPTIME from CMS_BEAM_COND.CMS_BRIL_LUMINOSITY where RUN=%s order by DIPTIME" % run_number)
    return [item[0] for item in rows]

def get_start_stop_timestamps(first_run, last_run):
    rows = fetch("select * from (select DIPTIME from CMS_BEAM_COND.CMS_BRIL_LUMINOSITY where RUN=%s order by DIPTIME) where ROWNUM=1 UNION select * from (select DIPTIME from CMS_BEAM_COND.CMS_BRIL_LUMINOSITY where RUN=%s order by DIPTIME desc) where ROWNUM=1" % (first_run, last_run))
    return [item[0] for item in rows]

def get_runs_from_fill(fill_number):
    rows = fetch("select distinct RUN from CMS_BEAM_COND.CMS_BRIL_LUMINOSITY where FILL=%s order by RUN" % fill_number)
    return [item[0] for item in rows]

def get_runs_from_timerange(time_start, time_stop):
    rows = fetch("select distinct RUN from CMS_BEAM_COND.CMS_BRIL_LUMINOSITY where DIPTIME BETWEEN TO_TIMESTAMP('%s', 'RRRR-MM-DD HH24:MI:SS.FF') AND TO_TIMESTAMP('%s', 'RRRR-MM-DD HH24:MI:SS.FF') order by RUN" % (time_start, time_stop))
    return [item[0] for item in rows]
 
