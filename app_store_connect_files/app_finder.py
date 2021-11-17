def get_apps(apps):
    apps_list = []
    for app in apps:
        app_name_id = {}
        if app['isEnabled'] == True:
            app_name_id['name'] = app['name']
            app_name_id['adamId'] = app['adamId']
            apps_list.append(app_name_id)
        else:
            None
    return apps_list
