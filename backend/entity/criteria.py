from email.header import decode_header
from datetime import datetime
from utils import formatconvert

class Criteria:
    def __init__(self, **kwargs):
        self.subject = kwargs.get('subject', None)
        self.sender = kwargs.get('from', None)
        self.receiver = kwargs.get('to', None)
        self.words_in_body = kwargs.get('bodyContains', None)
        self.date_from = kwargs.get('dateFrom', None)
        self.date_to = kwargs.get('dateTo', None)
        self.limit = kwargs.get('limit', 'any')

    def print_details(self):
        print("Criteria details:")
        print(f"Subject: {self.subject}")
        print(f"Sender: {self.sender}")
        print(f"Receiver: {self.receiver}")
        print(f"Words in Body: {self.words_in_body}")
        print(f"Date From: {self.date_from}")
        print(f"Date To: {self.date_to}")
        print(f"Limit: {self.limit}")

    def matches(self, email_message, email_body):
        date_format = '%Y-%m-%d'
        print(f"self.subject = {self.subject} and email_message['Subject'] = {email_message['Subject']}")
        subject = self.get_decoded_header(email_message['Subject'])
        sender = self.get_decoded_header(email_message['From'])
        receiver = self.get_decoded_header(email_message['To'])
        email_date_str = self.get_decoded_header(email_message['Date'])
        email_date = formatconvert.convert_email_date(email_date_str)
        print(f"email_date_str {email_date}")
        if email_date == None:
            return False
        if self.subject and self.subject not in subject:
            return False
        if self.sender and self.sender not in sender:
            return False
        if self.receiver and self.receiver not in receiver:
            return False
        if self.words_in_body and any(word not in email_body for word in self.words_in_body.split()):
            return False
        if self.date_from and datetime.strptime(self.date_from, date_format) > datetime.strptime(email_date,date_format) and email_date != '0000-00-00 00:00:00':
            return False
        if self.date_to and datetime.strptime(self.date_to, date_format) < datetime.strptime(email_date,date_format) and email_date != '0000-00-00 00:00:00':
            return False
        return True

    def parse_date(self, date_str, formats):
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        print(f"Error parsing date: {date_str}")
        return None

    def get_decoded_header(self, header):
        if header is None:
            return None

        decoded_header = decode_header(header)
        header_parts = []
        for part, encoding in decoded_header:
            if isinstance(part, bytes):
                try:
                    header_parts.append(part.decode(encoding or 'utf-8'))
                except LookupError:
                    header_parts.append(part.decode('latin-1'))
                except UnicodeDecodeError:
                    header_parts.append(part.decode('latin-1', errors='replace'))
            else:
                header_parts.append(part)

        return ' '.join(header_parts)



