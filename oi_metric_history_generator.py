import json
import datetime
import time
import requests
import oi_history_gen_lib as oi


url = oi.getOI_REST_url()

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
DATE_FORMAT_GMT = '%a, %d %b %Y %H:%M:%S GMT'
# CONTENT_TYPE = 'application/json'


headers = oi.requestHeaders()
print 'headers: ', headers
oi_user = oi.getOI_User()
oi_pass = oi.getOI_Password()

metrics_batch = oi.generate_OI_History_seasonal_timeseries()
print 'number of data batches: ', len(metrics_batch)

r1 = requests.Session()

for batch in metrics_batch:

    '''
    Sending the first element of the list with a dedicated POST
    to cause metric registration in case it's not yet registered.
    '''

    res = r1.post(
        url,
        headers=headers,
        auth=(oi_user, oi_pass),
        json=batch[0]
    )

    time.sleep(5)

    res = r1.post(
        url,
        headers=headers,
        auth=(oi_user, oi_pass),
        json=batch[1:]
    )

    r1_status_code = res.status_code

    print "status code " + str(r1_status_code)
    print 'Sending JSON payload for ', len(batch), 'metrics'

    if oi.Dump_Metrics_To_Files:
        filename = 'history_ts_json_payload_' + str(
            datetime.datetime.now()) + '.json'
        with open(filename.replace(" ", "_"), 'w') as outfile:
            json.dump(batch, outfile)

    time.sleep(30)
