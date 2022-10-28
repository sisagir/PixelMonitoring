import hashlib
import cx_Oracle
from inspect import cleandoc as multi_line_str

from utils.pythonUtils import run_bash_command


def get_oms_database_password(file_name="oms_pwd.txt"):
    directory = run_bash_command("echo $PIXEL_MONITORING_DIR") + "/credentials"
    with open(directory + "/" + file_name) as f:
        return f.readline().strip()


def get_oms_database_user_password_and_name():
    user_name = "cms_trk_r"
    password = get_oms_database_password()
    database_name = "cms_omds_adg"
    return user_name, password, database_name


def fetch(query, caching=False, cache_file_name="queries.cache"):

    user_name, password, database_name = get_oms_database_user_password_and_name()
    query_hashed = hashlib.md5(query.encode('utf-8')).hexdigest()
    
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
        connection = cx_Oracle.connect('%s/%s@%s' % (user_name, password, database_name))

        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

        if caching:
            with open(cache_file_name, 'a+') as f:
                query = query.replace('\n', ' ')
                f.write(query + '\n' + query_hashed + '\n' + str(result) + '\n')
            print("Wrote cache")
            
    return result


def get_timestamps(run_number):
    query = multi_line_str("""
        SELECT DISTINCT diptime
        FROM cms_beam_cond.cms_bril_luminosity
        WHERE run={run_number}
        ORDER BY diptime""".format(
            run_number=run_number,
        )
    )
    rows = fetch(query)
    return [item[0] for item in rows]


