import imaplib
import imaplib
import email
from email import message_from_bytes
from email.header import decode_header
import json
from entity.email_scrape_data import EmailScrapeData
from utils import dbutils, formatconvert
import threading
import schedule
import time
from entity.criteria import Criteria


def scrape(email,password,criteria,mailbox='INBOX'):
    try:
        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(email, password)
    except imaplib.IMAP4.error as e:
        print(f"Login failed: {e}")
        return []
    print("Auth Successful")

    try:
        imap.select(mailbox)
        status, messages = imap.search(None, 'ALL')
        if status != 'OK':
            print("Failed to retrieve messages.")
            return []

        emails_data = []
        message_ids = messages[0].split()
        # If criteria.limit == 'any' use all message IDs, if not up to limit
        if criteria.limit != 'any':
            try:
                limit = int(criteria.limit)  # Convert limit to int
                message_ids = message_ids[:limit]
            except ValueError:
                print("Invalid limit specified. Defaulting to all messages.")

        for message_id in message_ids:
            status, message_data = imap.fetch(message_id, '(RFC822)')
            if status != 'OK':
                continue

            for part in message_data:
                if isinstance(part, tuple):
                    email_message = message_from_bytes(part[1])
                    subject = decode_header(email_message['Subject'])[0][0]
                    subject = subject.decode() if isinstance(subject, bytes) else subject
                    from_ = decode_header(email_message['From'])[0][0]
                    from_ = from_.decode() if isinstance(from_, bytes) else from_
                    date = email_message['Date']
                    body = "Could not retrieve the body"

                    if email_message.is_multipart():
                        for payload in email_message.get_payload():
                            if payload.get_content_type() == 'text/plain':
                                body = payload.get_payload(decode=True).decode('utf-8')
                                break
                    else:
                        body = email_message.get_payload(decode=True).decode('utf-8')

                    if criteria.matches(email_message, body):
                        emailScrapeDataInstance = EmailScrapeData(subject, from_, date, body)
                        print(f"valid : {emailScrapeDataInstance}")
                        emails_data.append(emailScrapeDataInstance.to_dict())
                    # emailScrapeDataInstance = EmailScrapeData(subject, from_, date, body)
                    # print(emailScrapeDataInstance.to_dict())
                    # emails_data.append(emailScrapeDataInstance)
        imap.logout()
        # emails_data_dicts = [email.to_dict() for email in emails_data]
        # emails_data_json = json.dumps(emails_data_dicts, indent=4)

        emails_data_json = json.dumps(emails_data,indent=4)
        print(f"emails_data_json : {emails_data_json}")
        return emails_data_json
    except Exception as e:
        print(f"An error occurred: {e}")
        imap.logout()
        return []

def monitor():
    print('[MONITOR] : started...')
    schedule.every().day.at("16:55").do(dbutils.monitor_user_filters)
    while True:
        schedule.run_pending()
        time.sleep(60)



def save_emails_to_db(emails, user_email):
    emails_json = json.loads(emails)
    if not dbutils.does_user_data_table_exist():
        dbutils.create_user_data_table()
    dbutils.delete_all_user_data(user_email)
    for email in emails_json:
        print(f"emailtosave : {email}")
        email['date'] = formatconvert.convert_date_format(email['date'])
        dbutils.insert_user_data(email,user_email)


def process_filter(row):
    print(f'test : row {row}')
    criteria = Criteria(
        subject=row.get('subject'),
        sender=row.get('from'),
        receiver=row.get('to'),
        words_in_body=row.get('bodyContains'),
        date_from=row.get('dateFrom'),
        date_to=row.get('dateTo'),
        limit=row.get('limit', 'any')
    )
    valid_emails = scrape(row['user'], row['password'], criteria)
    valid_emails = json.loads(valid_emails)
    print("________________________")
    print(f"valid emails : {valid_emails}")
    for email_data in valid_emails:  # Iterate over the email data from scrape
        print(f"moniored email : {email_data}")
        print(f"monitored email date : {email_data.get('date')}")
        print(f"conv : {formatconvert.convert_date_format(email_data.get('date'))}")
        db_valid_date = formatconvert.convert_date_format(email_data.get('date'))
        dbutils.insert_filter_scrape_data(email_data.get('subject'),email_data.get('sender'),db_valid_date,email_data.get('body'),row['id'])


