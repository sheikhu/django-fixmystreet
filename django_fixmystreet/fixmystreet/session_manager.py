from django.contrib.sessions.backends.db import SessionStore
from django_fixmystreet.fixmystreet.models import ReportComment, ReportFile, Report


class SessionManager:
	@classmethod
	def createComment(cls, title, text, session):
		if not 'comments' in session:
			session['comments'] = []
		session['comments'].append({"title":title,"text":text})


	@classmethod
	def createFile(cls, title, file, session):
		if not 'files' in session:
			session['files'] = []
		session['files'].append({"title":title,"file":file})

	@classmethod
	def saveComments(cls, session, report):
		if 'comments' in session:
			commentsData = session['comments']
			for comment in commentsData:
				c = ReportComment(text=comment['text'], report=report)
				c.save()
			del session['comments']

	@classmethod
	def saveFiles(cls, session, report):
		if 'files' in session:
			for f in session['files']:
				ftype = ReportFile.PDF
				if str(f['file']).endswith("pdf"):
					ftype = ReportFile.PDF
				if str(f['file']).endswith("doc"):
					ftype = ReportFile.WORD
				if str(f['file']).endswith("png") or str(f['file']).endswith("jpg"):
					ftype = ReportFile.IMAGE
				if str(f['file']).endswith("xls"):
					ftype = ReportFile.EXCEL
				c = ReportFile(title=f['title'], file=f['file'], file_type=ftype, report=report)
				c.save()
			del session['files']

	@classmethod
	def clearSession(cls, session):
		if 'files' in session:
			del session['files']
		if 'comments' in session:
			del session['comments']
