# from sqlalchemy.orm import Session
# from datetime import datetime
# from ..models.log_book import LogBook
# from ..db import get_session

# #Logging function
# def log_action(user_id: int, action: str, file_id: int=None, details: dict=None):
#     db: Session = get_session()

#     try:
#         log_entry = LogBook(user_id = user_id,
#                             action = action,
#                             file_id = file_id,
#                             details = details,
#                             timestamp = datetime.now(datetime.timezone.utc))
#         db.add(log_entry)
#         db.commit()
#         db.refresh(log_entry)
#         print("Logged action: {action} of user: {user_id}")
#     except Exception as e:
#         db.rollback()
#         print("Error: {e}")
