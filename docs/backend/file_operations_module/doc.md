# File operations
This is a documentation for the module of file operations. \
Person responsible for the documentation of that module is Jakub Suliga.

## File storage
Files in the module are stored in a general directory for services in the system under the path:
`/srv/file-ops/data/`. \
To allow the program to save in that directory there is a need to:
- fistly create it
- add specific permission to the user running the server
```
sudo mkdir -p /srv/file-ops/data
sudo chown -R student:student /srv/file-ops
sudo chmod 750 /srv/file-ops /srv/file-ops/data
```
The files provided by users are stored in sepearate directories. The general path structure is:
```
user/<userID>/file/<fileId>/<safe_logical_name>
```

## File metadata
Metadata of files will be stored in database in the following table and with following realtionships:
![image](files_table.png)