# Resources: user_account, own_user_account, file, own_file
# Actions: read, update, delete, create

PERMISSIONS_MAP = {
    # Admin has all control
    "admin": {
        "user_account": ["read", "update", "delete"],
        "file": ["read", "update", "delete", "create"],
    },
    # Regular user is restricted to their own resources
    "user": {
        # Can read other user accounts, but cannot modify/delete them
        "user_account": ["read"],
        # Can only modify their own account
        "own_user_account": ["update"],
        # Can create files
        "file": ["create"],
        # Can read/download/delete their own files
        "own_file": ["read", "update", "delete"],
    },
}