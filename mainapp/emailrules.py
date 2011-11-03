from django.utils.translation import ugettext as _


class EmailRuleBehaviour(object):
    def __init__(self,email_rule,report):
        self.email_rule = email_rule
        self.report = report

    def add_email(self,email):
        if self.email_rule.is_cc and email not in self.report.cc_emails and email not in self.report.excluded: 
            self.report.cc_emails.append(email)
        elif not self.email_rule.is_cc and email not in self.report.to_emails and email not in self.report.excluded:
            self.report.to_emails.append(email)
    
    def remove_email(self,email):
        if email in self.report.cc_emails:
            self.report.cc_emails.remove(email)
        if email in self.report.to_emails:
            self.report.to_emails.remove(email)
        
        if email not in self.report.excluded:
            self.report.excluded.append(email)

class ToCouncillor(EmailRuleBehaviour):
    def resolve_email(self):
        self.add_email(self.email_rule.councillor.email)

class MatchingCategoryClass(EmailRuleBehaviour):
    def resolve_email(self):
        if self.report.category.category_class == self.email_rule.category_class:
            self.add_email(self.email_rule.councillor.email)

    
class NotMatchingCategoryClass(EmailRuleBehaviour):
    def resolve_email(self):
        if self.report.category.category_class == self.email_rule.category_class:
            self.remove_email(self.email_rule.councillor.email)
        else:
            self.add_email(self.email_rule.councillor.email)



