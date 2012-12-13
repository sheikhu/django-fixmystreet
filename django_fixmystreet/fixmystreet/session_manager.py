from django.contrib.sessions.backends.db import SessionStore
from django_fixmystreet.fixmystreet.models import ReportComment, ReportFile, Report
from django_fixmystreet.fixmystreet.utils import save_file_to_server
import os

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
				file_path = ""
				if str(f['file']).endswith("pdf"):
					ftype = ReportFile.PDF
					file_path = save_file_to_server(f['file'],ReportFile.attachment_type[ftype-1][1],"pdf", report.id)
				if str(f['file']).endswith("doc"):
					ftype = ReportFile.WORD
					file_path = save_file_to_server(f['file'],ReportFile.attachment_type[ftype-1][1],"doc", report.id)
				if str(f['file']).endswith("png") or str(f['file']).endswith("jpg"):
					ftype = ReportFile.IMAGE
					file_path = save_file_to_server(f['file'],ReportFile.attachment_type[ftype-1][1],"jpg", report.id)
				if str(f['file']).endswith("xls"):
					ftype = ReportFile.EXCEL
					file_path = save_file_to_server(f['file'],ReportFile.attachment_type[ftype-1][1],"xls", report.id)
				
				c = ReportFile(title=f['title'], file=file_path, file_type=ftype, report=report)
				c.save()
			del session['files']

	@classmethod
	def clearSession(cls, session):
		if 'files' in session:
			for f in session['files']:
				path = f['file']
				if os.path.exists(path):
					os.remove(path)
			del session['files']
		if 'comments' in session:
			del session['comments']

