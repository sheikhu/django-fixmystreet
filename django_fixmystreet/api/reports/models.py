# -*- coding: utf-8 -*-
import datetime


class ReportAssignmentAccept(object):

    def __init__(self, reference_id, created_at=None, comment=None):
        self.reference_id = reference_id
        self.comment = comment
        self.created_at = created_at or datetime.datetime.now()


class ReportAssignmentReject(object):

    def __init__(self, comment, created_at=None):
        self.comment = comment
        self.created_at = created_at or datetime.datetime.now()


class ReportAssignmentClose(object):

    def __init__(self, reference_id, created_at=None, comment=None):
        self.reference_id = reference_id
        self.comment = comment
        self.created_at = created_at or datetime.datetime.now()
