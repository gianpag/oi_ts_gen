import sys
import getopt
import time
import json
import requests
import oi_history_gen_lib as oi


url = oi.getOI_REST_url()

headers = oi.requestHeaders()
print 'headers: ', headers
oi_user = oi.getOI_User()
oi_pass = oi.getOI_Password()

r1 = requests.Session()


def main(argv):
    dp_time = ''
    datapoint = 0
    try:
        opts, args = getopt.getopt(argv, "ht:d:", ["time=", "datapoint="])
    except getopt.GetoptError:
        print 'oi_send_datapoint.py -t now -d 10'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'oi_send_datapoint.py -t now -d 10'
            sys.exit()
        elif opt in ("-t", "--time"):
            dp_time = arg
        elif opt in ("-d", "--datapoint"):
            datapoint = arg

    if dp_time == '' or dp_time == 'now':
        dp_timestamp = int(time.time())
    json_payload = oi.generate_OI_json_payload(dp_timestamp, datapoint)
    print 'Input file is "', dp_timestamp
    print 'Output file is "', datapoint

    res = r1.post(
        url,
        headers=headers,
        auth=(oi_user, oi_pass),
        data='['+json.dumps(json_payload)+']'
    )

    print 'Datapoint POST completed with return code: ', res.status_code


if __name__ == "__main__":
    main(sys.argv[1:])
