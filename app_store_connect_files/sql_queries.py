queries = {}


queries['create_table'] = """CREATE TABLE IF NOT EXISTS {}
(date DATE NOT NULL,
installs INT,
uninstalls INT,
sessions INT,
pageViewCount INT,
activeDevices INT,
rollingActiveDevices INT,
units INT,
crashes INT,
iap INT,
impressionsTotal INT,
impressionsTotalUnique INT,
pageViewUnique INT,
app_id VARCHAR(20),
app_name VARCHAR(20),
PRIMARY KEY (date,app_id) )"""


queries['insert_rows'] = """INSERT IGNORE INTO {} ({}) VALUES ({})
ON DUPLICATE KEY UPDATE """

queries['max_date'] = "SELECT MAX(date) FROM {} WHERE app_id = {}"
