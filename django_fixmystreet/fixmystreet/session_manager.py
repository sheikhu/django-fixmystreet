from django.contrib.sessions.backends.db import SessionStore
from django_fixmystreet.fixmystreet.models import ReportComment, ReportFile, Report
class SessionManager():
	def createComment(self,title,text,sessionK):
		s = SessionStore(session_key=sessionK)
		if not 'comments' in s.keys():
			s['comments'] = []
		s['comments'].append({"title":title,"text":text})
		s.save()

	def createFile(self,title,file,sessionK):
		s = SessionStore(session_key=sessionK)
		if not 'files' in s.keys():
			s['files'] = []
		s['files'].append({"title":title,"file":file})
		s.save()

	def saveComments(self,sessionK,reportId):
		import pdb
		s = SessionStore(session_key = sessionK)
		if 'comments' in s.keys():
			commentsData = s['comments']
			for comment in commentsData:
				c = ReportComment(title=comment['title'],text=comment['text'], report = Report.objects.get(pk=reportId))
				c.save()
			del s['comments']
			s.save()

	def saveFiles(self,sessionK,reportId):
		s = SessionStore(session_key = sessionK)
		if 'files' in s.keys():
			filesData = s['files']
			for f in filesData:
				ftype = ReportFile.PDF
				if str(f['file']).endswith("pdf"):
					ftype = ReportFile.PDF
				if str(f['file']).endswith("doc"):
					ftype = ReportFile.WORD
				if str(f['file']).endswith("png") or str(f['file']).endswith("jpg"):
					ftype = ReportFile.IMAGE
				if str(f['file']).endswith("xls"):
					ftype = ReportFile.EXCEL
				c = ReportFile(title=f['title'],file=f['file'], file_type = ftype,report = Report.objects.get(pk=reportId))
				c.save()
			del s['files']
			s.save()
	def clearSession(self,sessionK):
		print 'clearing session'
		s = SessionStore(session_key = sessionK)
		if 'files' in s.keys():
			del s['files']
		if 'comments' in s.keys():
			del s['keys']
		s.save()
