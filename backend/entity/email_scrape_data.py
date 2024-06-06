class EmailScrapeData:
    def __init__(self, subject, sender, date, body):
        self.subject = subject
        self.sender = sender
        self.date = date
        self.body = body

    def __repr__(self):
        return f"EmailScrapeData(subject='{self.subject}', sender='{self.sender}', date='{self.date}', body='{self.body[:30]}...')"

    def to_dict(self):
        return {
            "subject": self.subject,
            "sender": self.sender,
            "date": self.date,
            "body": self.body
        }