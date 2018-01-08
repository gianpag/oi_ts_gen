import json
import datetime
import time
import requests
import oi_history_gen_lib as oi


url = oi.getOI_REST_url()

# DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
# DATE_FORMAT_GMT = '%a, %d %b %Y %H:%M:%S GMT'
# CONTENT_TYPE = 'application/json'


headers = oi.requestHeaders()
print 'headers: ', headers
oi_user = oi.getOI_User()
oi_pass = oi.getOI_Password()

metrics_batch = oi.generate_OI_History_seasonal_timeseries()
print 'number of data batches: ', len(metrics_batch)

r1 = requests.Session()

mi = 0
for batch in metrics_batch:

    if mi == 0:
        '''
        Sending the first element of the list with a dedicated POST
        to cause metric registration in case it's not yet registered.
        '''

        res = r1.post(
            url,
            headers=headers,
            auth=(oi_user, oi_pass),
            data='['+json.dumps(batch[0])+']'
        )

        print 'Initial metric sent for registration\n\n',
        '['+json.dumps(batch[0])+']'

        print 'batch[0] POST status: ', res.status_code

        print 'Sleeping for 60 seconds to let the midserver digest ', 'the first bite\n\n'
        time.sleep(60)

        res = r1.post(
            url,
            headers=headers,
            auth=(oi_user, oi_pass),
            data=json.dumps(batch[1:])
        )
        time.sleep(60)
    else:
        res = r1.post(
            url,
            headers=headers,
            auth=(oi_user, oi_pass),
            data=json.dumps(batch)
        )

    r1_status_code = res.status_code

    print "status code " + str(r1_status_code)
    print 'Sent JSON payload for ', len(batch), 'metrics'
    print 'Sleeping for 60 seconds to let the midserver digest ', len(batch), 'metrics'

    if oi.Dump_Metrics_To_Files:
        filename = 'history_ts_json_payload' + str(mi) + '_' + str(
            datetime.datetime.now()) + '.json'
        filename.replace(" ", "_")
        filename.replace(":", "-")
        with open(filename, 'w') as outfile:
            json.dump(batch, outfile)
    mi += 1
    time.sleep(60)
