# File operations
This is a documentation for the module of file operations. \
Person responsible for the documentation of that module is Jakub Suliga.

## File storage
Files in the module are stored in a general directory for services in the system under the path:
`/srv/file-ops/data/`. \
The files provided by users are stored in sepearate directories. The general path structure is:
```
user/<userID>/file/<fileId>/<version_no>/<sha8>_<safe_logical_name>
```

## File metadata
Metadata of files will be stored in database in the following tables:
