import datetime
import time
import pandas as pd
import random
import ConfigParser


OI_Config = ConfigParser.ConfigParser()
OI_Config.read("oi_history_generator_config.ini")

#  MID_ADDRESS = 'ec2-52-91-241-245.compute-1.amazonaws.com'
global MID_WEB_USER
MID_WEB_USER = OI_Config.get('MID_SERVER', 'MID_WEB_USER')
global MID_WEB_PASS
MID_WEB_PASS = OI_Config.get('MID_SERVER', 'MID_WEB_PASS')
global NUMBER_OF_SAMPLES_PER_REQUEST
NUMBER_OF_SAMPLES_PER_REQUEST = OI_Config.getint(
 'MID_SERVER', 'NUMBER_OF_SAMPLES_PER_REQUEST'
)

global Dump_Metrics_To_Files
Dump_Metrics_To_Files = OI_Config.getboolean(
    'METRIC_DEFINITION', 'DUMP_REQUESTS_TO_JSON_FILE')

global METRIC_TYPE
METRIC_TYPE = OI_Config.get('METRIC_DEFINITION', 'METRIC_TYPE')
global METRIC_RESOURCE
METRIC_RESOURCE = OI_Config.get('METRIC_DEFINITION', 'METRIC_RESOURCE')
global METRIC_NODE
METRIC_NODE = OI_Config.get('METRIC_DEFINITION', 'METRIC_NODE')
global METRIC_SOURCE
METRIC_SOURCE = OI_Config.get('METRIC_DEFINITION', 'METRIC_SOURCE')
global metric_frequency_minutes
metric_frequency_minutes = OI_Config.getint(
 'METRIC_DEFINITION', 'METRIC_FREQUENCY_MINUTES'
 )
global days_of_past_data
days_of_past_data = OI_Config.getint('METRIC_DEFINITION',
                                     'DAYS_OF_PAST_DATA')
global multiply_factor
multiply_factor = OI_Config.getfloat('METRIC_DEFINITION',
                                     'METRIC_VALUE_MULTIPLY_FACTOR')
global include_anomaly
include_anomaly = OI_Config.getboolean(
    'METRIC_DEFINITION', 'INCLUDE_ANOMALY')


def getOI_User():
    """Return Mid Web Extension User."""
    mws = MID_WEB_USER
    return mws


def getOI_Password():
    """Return Mid Web Extension Password."""
    mwp = MID_WEB_PASS
    return mwp


def getOI_SamplesPerRequest():
    """Return Mid Web Extension Password."""
    samp_x_req = NUMBER_OF_SAMPLES_PER_REQUEST
    return samp_x_req


def getOI_REST_url():
    """
    Document function here.

    It returns the Operational Metrics Mid Server Web Extension.
    This is the url used to send JSON payloads with metrics.
    """
    MID_ADDRESS = OI_Config.get('MID_SERVER', 'MID_HOSTNAME')
    MID_PORT = OI_Config.get('MID_SERVER', 'MID_PORT')
    USE_HTTPS = OI_Config.getboolean('MID_SERVER', 'USE_HTTPS')
    if USE_HTTPS:
        url_proto = 'https'
    else:
        url_proto = 'http'

    url = url_proto + '://' + MID_ADDRESS + ':' + MID_PORT + \
        '/api/mid/sa/metrics'

    return url


DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
DATE_FORMAT_GMT = '%a, %d %b %Y %H:%M:%S GMT'
# CONTENT_TYPE = 'application/json'


def requestHeaders():
    """
    Document function here.

    This is required for Secure connections
    to the Mid Server Web extension.

    """
    auth = ''
    auth += 'POST\n'
    auth += 'application/json\n'
    auth += datetime.datetime.utcnow().strftime(DATE_FORMAT)[:-3] + 'Z\n'
    auth += '/api/mid/sa/metrics'

    return {
        'Date': datetime.datetime.utcnow().strftime(DATE_FORMAT)[:-3] + 'Z',
        'Content-Type': 'application/json'
    }


def generate_OI_History_seasonal_timeseries():
    """Time Series generation section."""
    ts_startdate = datetime.datetime.now() - datetime.timedelta(
        days=days_of_past_data)
    #  minutes_of_past_data = days_of_past_data*1440/metric_frequency_minutes

    #  generate a date range to use for the time series generation

    daterage_list = pd.date_range(start=ts_startdate,
                                  end=datetime.datetime.now(), freq=str(
                                   metric_frequency_minutes)+'min')

    print len(daterage_list), daterage_list[-1]

    i = 0
    ts_metric_values_list = []

    for tstamp in daterage_list:
        if tstamp.hour in range(0, 3):
            rnd_low_end = 500 * multiply_factor
            rnd_up_end = 1000 * multiply_factor
        elif tstamp.hour in range(3, 6):
            rnd_low_end = 900 * multiply_factor
            rnd_up_end = 1500 * multiply_factor
        elif tstamp.hour in range(6, 9):
            rnd_low_end = 1200 * multiply_factor
            rnd_up_end = 1800 * multiply_factor
        elif tstamp.hour in range(9, 13):
            rnd_low_end = 1500 * multiply_factor
            rnd_up_end = 2500 * multiply_factor
        elif tstamp.hour in range(13, 17):
            rnd_low_end = 1200 * multiply_factor
            rnd_up_end = 1800 * multiply_factor
        elif tstamp.hour in range(17, 21):
            rnd_low_end = 1500 * multiply_factor
            rnd_up_end = 2500 * multiply_factor
        elif tstamp.hour in range(21, 25):
            rnd_low_end = 900 * multiply_factor
            rnd_up_end = 1500 * multiply_factor

        metric_value = random.randrange(rnd_low_end, rnd_up_end)

        ts_metric_values_list.append(
            {
              "metric_type": METRIC_TYPE,
              "resource": METRIC_RESOURCE,
              "node": METRIC_NODE,
              "value": metric_value,
              "timestamp": int(time.mktime(
                  daterage_list[i].timetuple()))*1000,
              "ci_identifier": {
                "node": METRIC_NODE
              },
              "source": METRIC_SOURCE
            }
        )

        i += 1

    if include_anomaly and len(ts_metric_values_list) > 10:
        ts_metric_values_list[-5]['value'] *= 8
        ts_metric_values_list[-4]['value'] *= 7

    chunk_lenght = NUMBER_OF_SAMPLES_PER_REQUEST
    batched_metrics = [
        ts_metric_values_list[j:j + chunk_lenght] for j in xrange(
            0, len(ts_metric_values_list), chunk_lenght)]

    return batched_metrics


def generate_OI_json_payload(dp_time, datapoint):
    """Json payload generation section."""
    ts_metric_values_list = []

    ts_metric_values_list.append(
        {
          "metric_type": METRIC_TYPE,
          "resource": METRIC_RESOURCE,
          "node": METRIC_NODE,
          "value": datapoint,
          "timestamp": int(dp_time)*1000,
          "ci_identifier": {
            "node": METRIC_NODE
          },
          "source": METRIC_SOURCE
        }
    )

    return ts_metric_values_list
