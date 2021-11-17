import app_store_connect_client as app_store
import json
import pandas as pd
import sql_queries
import pandas as pd
from date_finder import find_dates
import credentials as creds
import app_finder
import datetime
from functools import reduce
from db_connection import create_connection
import os

table_name = 'itunesAppStoreMetrics'

#Create client for AppStore
client = app_store.Client(username=os.environ['APP_STORE_USERNAME'],
password=os.environ['APP_STORE_PASSWORD'])
client.change_provider(os.environ['APP_STORE_PROVIDER_ID'])
print('API client created')

#Create connection to MySQL DB
connection = create_connection(os.environ['DB_HOST'], os.environ['DB_USER'],
os.environ['DB_PASSWORD'], os.environ['DB_NAME'])
cursor = connection.cursor()

# Create table if required
cursor.execute(sql_queries.queries['create_table'].format(table_name))


#Get list of all availabale apps
def apps():
    apps = client.get_apps()
    apps = apps['results']
    app_list = app_finder.get_apps(apps)
    return app_list


app_list = apps()
updated_apps = []




#Retreive data from AppStore, put it into a Pandas-DataFrame and insert it into DB
#Repeat for each available app
def retreive_insert_data():
    metrics_list = [ app_store.measures.installs,
                     app_store.measures.uninstalls,
                     app_store.measures.sessions,
                     app_store.measures.page_views,
                     app_store.measures.active_devices,
                     app_store.measures.active_last_30days,
                     app_store.measures.units,
                     app_store.measures.crashes,
                     app_store.measures.iap,
                     app_store.measures.impressions,
                     app_store.measures.impressions_unique,
                     app_store.measures.page_view_unique]

    #connecting to DB
    for app in app_list:
        try:
    # Read latest date from DB
            sql = sql_queries.queries['max_date'].format(table_name, app['adamId'])
            cursor.execute(sql)
            max_date = cursor.fetchone()
            max_date = max_date['MAX(date)']
            if max_date == None:
                latest_date = datetime.datetime(2020, 9, 1)
            else:
                latest_date = max_date

        #Retrieving end date and start date for query
            start_date = latest_date.strftime('%Y-%m-%d')
            end_date = find_dates()['yesterday'].strftime('%Y-%m-%d')

        #Reading data for each metric and merging all the metrics into one DF
            if max_date == find_dates()['today']:
                print("No update required for app {}".format(app['name']))
            else:
                data = []
                for metric in metrics_list:
                    config = { 'measures': [metric]}
                    connection_query = app_store.Query(app['adamId']).metrics(config).date_range(start_date, end_date)
                    results = client.execute(connection_query)


                    results_list = results['results']
                    for result in results_list:
                        df = pd.DataFrame(result['data'])
                        data.append(df)

        # Creating data frame with data to insert into DB
                df_merged = reduce(lambda x, y: pd.merge(x, y, on = 'date'), data)
                df_merged['date'] = pd.to_datetime(df.iloc[:,0], format = '%Y-%m-%d').dt.date
                df_merged['app_id'] = app['adamId']
                df_merged['app_name'] = app['name']

                print("Data extracted + DF with data created for app {}".format(app['name']))


            # creating column list for insertion
                cols = ",".join([str(i) for i in df_merged.columns.tolist()])
                vals = ("%s,"* len(df_merged.columns.tolist()))[:-1]
                measures = df_merged.columns.tolist()[1:-2]

            # creating query for insertion
                update_str = ""
                for measure in measures:
                    update_str += "{} = VALUES ({}),".format(measure, measure)
                update_str = update_str[:-1]

                insert_query = sql_queries.queries['insert_rows'].format(table_name, cols, vals)
                insert_query += update_str

        # Insert DataFrame recrds one by one.
                for i,row in df_merged.iterrows():
                    cursor.execute(insert_query, tuple(row))
                    connection.commit()
                print("Data inserted into DB for app {}".format(app['name']))


        #Updating the list with updated apps for later check
                updated_app = {}
                updated_app['name'] = app['name']
                updated_app['adamId'] = app['adamId']
                updated_apps.append(updated_app)

        except Exception as e:
            print('Failed to update app {}. Error message: {}'.format(app['name'], e))

# Checking if all apps were updated
def check():
    set_app_list = set(tuple(sorted(d.items())) for d in app_list)
    set_updated_apps = set(tuple(sorted(d.items())) for d in updated_apps)

    set_difference = set_app_list.symmetric_difference(set_updated_apps)
    list_dicts_difference = []
    for tuple_element in set_difference:
        list_dicts_difference.append(dict((x, y) for x, y in tuple_element))

    if len(list_dicts_difference) == 0:
        print('All apps successfully updated')
    else:
        print('Following apps were not updated:'.format(list_dicts_difference))


apps()
retreive_insert_data()
check()
cursor.close()
connection.close()
