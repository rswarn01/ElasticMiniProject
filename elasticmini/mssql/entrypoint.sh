sed -i 's|%APP_DB_NAME%|'"${APP_DB_NAME}"'|g' ./create_databse.sql

# start SQL Server, start the script to create the DB and import the data, start the app
./create_databse.sh & /opt/mssql/bin/sqlservr