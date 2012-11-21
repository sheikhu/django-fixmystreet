from django.contrib.sessions.backends.db import SessionStore
from django_fixmystreet.fixmystreet.models import ReportComment, ReportFile, Report
class SessionManager():
	def createComment(self,title,text,sessionK):
		s = SessionStore(session_key=sessionK)
		print s.keys()
		if not 'comments' in s.keys():
			s['comments'] = []
		s['comments'].append({"title":title,"text":text})
		s.save()
		print s.keys()

	def createFile(self,title,file,sessionK):
		s = SessionStore(session_key=sessionK)
		if not 'files' in s.keys():
			s['files'] = []
		s['files'].append({"title":title,"file":file})
		s.save()

	def saveComments(self,sessionK,reportId):
		
		s = SessionStore(session_key = sessionK)
		print s.keys()
		commentsData = s['comments']
		for comment in commentsData:
			c = ReportComment(title=comment['title'],text=comment['text'], report = Report.objects.get(pk=reportId))
			c.save()
		del s['comments']
		s.save()

	def saveFiles(self,sessionK,reportId):

		s = SessionStore(session_key = sessionK)
		print s.keys()
		filesData = s['files']
		for f in filesData:
			c = ReportFile(title=f['title'],file=f['file'], report = Report.objects.get(pk=reportId))
			c.save()
		del s['files']
		s.save()
