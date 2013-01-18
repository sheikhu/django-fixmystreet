
from django.db import connection

from django_fixmystreet.fixmystreet.models import Report
from datetime import date as dt
from datetime import timedelta

class ReportCount(object):
    def __init__(self, interval):
        self.interval = interval

    def dict(self):
        return({ "recent_new": "count( case when age(clock_timestamp(), reports.created) < interval '%s' THEN 1 ELSE null end )" % self.interval,
          "recent_fixed": "count( case when age(clock_timestamp(), reports.close_date) < interval '%s' AND reports.is_fixed = True THEN 1 ELSE null end )" % self.interval,
          "recent_updated": "count( case when age(clock_timestamp(), reports.modified) < interval '%s' AND reports.is_fixed = False and reports.modified != reports.created THEN 1 ELSE null end )" % self.interval,
          "old_fixed": "count( case when age(clock_timestamp(), reports.close_date) > interval '%s' AND reports.is_fixed = True THEN 1 ELSE null end )" % self.interval,
          "old_unfixed": "count( case when age(clock_timestamp(), reports.close_date) > interval '%s' AND reports.is_fixed = False THEN 1 ELSE null end )" % self.interval } )


class SqlQuery(object):
    """
    This is a workaround: django doesn't support our optimized
    direct SQL queries very well.
    """

    def __init__(self):
        self.cursor = None
        self.index = 0
        self.results = None

    def next(self):
        self.index = self.index + 1

    def get_results(self):
        if not self.cursor:
            self.cursor = connection.cursor()
            self.cursor.execute(self.sql)
            self.results = self.cursor.fetchall()
        return( self.results )

class UsersAssignedToCategories(SqlQuery):
    def __init__(self,mainCategoryId,secondaryCategoryId,organisationId):
        SqlQuery.__init__(self)
        self.base_query = """ select FilterU.first_name, FilterU.last_name from(\
        select auth_user.first_name, auth_user.last_name, auth_user.id from(\
                select distinct fixmystreet_fmsuser_categories.fmsuser_id from(\
                        select id from fixmystreet_reportcategory where fixmystreet_reportcategory.category_class_id=%d and fixmystreet_reportcategory.secondary_category_class_id=%d) as RCat \
                join fixmystreet_fmsuser_categories on fixmystreet_fmsuser_categories.reportcategory_id = RCat.id ) as UserCat \
        join auth_user\
        on auth_user.id = UserCat.fmsuser_id \
    ) as FilterU \
join\
    (\
        select fixmystreet_fmsuser.user_ptr_id \
        from fixmystreet_fmsuser \
        where fixmystreet_fmsuser.organisation_id = %d \
    ) as FMSU \
on FMSU.user_ptr_id = FilterU.id """ % (mainCategoryId,secondaryCategoryId,organisationId)
        self.sql = self.base_query


class UserTypeForOrganisation(SqlQuery):
    def __init__(self,typeId,organisationId):
        SqlQuery.__init__(self)
        self.base_query="""select Cat.fmsuser_id,Cat.reportcategory_id \
from (select fmsuser_id,reportcategory_id from fixmystreet_fmsuser_categories where reportcategory_id=%d) as Cat \
join (select user_ptr_id from fixmystreet_fmsuser where fixmystreet_fmsuser.organisation_id=%d) as U \
on U.user_ptr_id = Cat.fmsuser_id """ % (typeId,organisationId)
        self.sql=self.base_query


class TypesWithUsersOfOrganisation(SqlQuery):
    def __init__(self,organisationId):
        SqlQuery.__init__(self)
        self.base_query=""" select A.reportcategory_id, A.fmsuser_id \
from (select * from fixmystreet_fmsuser_categories) as A \
join (select user_ptr_id from fixmystreet_fmsuser where organisation_id=%d) as B \
on B.user_ptr_id = A.fmsuser_id""" % (organisationId)
        self.sql=self.base_query

class ReportCountQuery(SqlQuery):

    def name(self):
        return self.get_results()[self.index][5]

    def recent_new(self):
        return self.get_results()[self.index][0]

    def recent_fixed(self):
        return self.get_results()[self.index][1]

    def recent_updated(self):
        return self.get_results()[self.index][2]

    def old_fixed(self):
        return self.get_results()[self.index][3]

    def old_unfixed(self):
        return self.get_results()[self.index][4]

    def __init__(self, interval = '1 month'):
        SqlQuery.__init__(self)

        #5 years for pro, 1 month for citizens
        #if isUserAuthenticated() == True:
        #      interval = '60 month'
        #
        #interval = '1 day'

        self.sql = """select count( case when age(clock_timestamp(), reports.created) < interval '{interval}' THEN 1 ELSE null end ) as recent_new,
count( case when age(clock_timestamp(), reports.close_date) < interval '{interval}' AND reports.status = {closed} THEN 1 ELSE null end ) as recent_fixed,
count( case when age(clock_timestamp(), reports.modified) < interval '{interval}' AND reports.status in ({progress}) and reports.modified != reports.created THEN 1 ELSE null end ) as recent_updated,
count( case when age(clock_timestamp(), reports.close_date) > interval '{interval}' AND reports.status = {closed} THEN 1 ELSE null end ) as old_fixed,
count( case when age(clock_timestamp(), reports.created) > interval '{interval}' AND reports.status in ({progress}) THEN 1 ELSE null end ) as old_unfixed
from fixmystreet_report as reports;
""".format(interval=interval, progress=','.join([str(s) for s in Report.REPORT_STATUS_IN_PROGRESS]), closed=Report.PROCESSED)


class CityTotals(ReportCountQuery):

    def __init__(self, interval, city):
        ReportCountQuery.__init__(self, interval)
        self.sql = self.base_query
        self.sql += """ from fixmystreet_report as reports left join fixmystreet_ward as wards on reports.ward_id = wards.id left join fixmystreet_city as cities on cities.id = wards.city_id
        """
        self.sql += ' where wards.city_id = %d ' % city.id

class CityWardsTotals(ReportCountQuery):

    def __init__(self, city):
        ReportCountQuery.__init__(self,"1 month")
        self.sql = self.base_query
        self.url_prefix = "/wards/"
        self.sql +=  ", wards.name, wards.id from fixmystreet_ward as wards "
        self.sql += """left join fixmystreet_report reports on wards.id = reports.ward_id join fixmystreet_city as cities on wards.city_id = cities.id join fixmystreet_province as province on cities.province_id = province.id
        """
        self.sql += "and cities.id = " + str(city.id)
        self.sql += " group by  wards.name, wards.id order by wards.name"

    def id(self):
        return(self.get_results()[self.index][6])

    def get_absolute_url(self):
        return reverse('ward_show', args=[self.get_results()[self.index][6]])

class AllCityTotals(ReportCountQuery):

    def __init__(self):
        ReportCountQuery.__init__(self,"1 month")
        self.sql = self.base_query
        self.url_prefix = "/cities/"
        self.sql +=  ", cities.name, cities.id, province.name from cities "
        self.sql += """left join wards on wards.city_id = cities.id join province on cities.province_id = province.id left join reports on wards.id = reports.ward_id
        """
        self.sql += "group by cities.name, cities.id, province.name order by province.name, cities.name"

    def get_absolute_url(self):
        return( self.url_prefix + str(self.get_results()[self.index][6]))

    def province(self):
        return(self.get_results()[self.index][7])

    def province_changed(self):
        if (self.index ==0 ):
            return( True )
        return( self.get_results()[self.index][7] != self.get_results()[self.index-1][7] )


class ReportCountBetweenDates(SqlQuery):
    def __init__(self, start_date,end_date):
        SqlQuery.__init__(self)
        self.sql = """ select 
        count(case when (reports.created between '{start_date}' AND '{end_date}') AND reports.status = {unpublished} THEN 1 ELSE null end) as count_new,
        count(case when reports.created > '{start_date}' AND reports.created < '{end_date}' AND reports.status in ({progress}) THEN 1 ELSE null end) as count_in_progress,
        count(case when reports.created > '{start_date}' AND reports.created < '{end_date}' AND reports.status ={closed} THEN 1 ELSE null end) as count_closed,
        count(case when reports.created > '{start_date}' AND reports.created < '{end_date}' THEN 1 ELSE null end) as count_all 
        from fixmystreet_report as reports;
        """.format(start_date=str(start_date),end_date=str(end_date), progress=','.join([str(s) for s in Report.REPORT_STATUS_IN_PROGRESS]), closed=Report.PROCESSED, unpublished = Report.CREATED)

    def get_count_new(self):
        return self.get_results()[self.index][0]

    def get_count_in_progress(self):
        return self.get_results()[self.index][1]
    
    def get_count_closed(self):
        return self.get_results()[self.index][2]
    
    def get_count_all(self):
        return self.get_results()[self.index][3]

class ReportCountStatsPro(object):

    def get_stats(self):
        today = dt.today()
        return {
            "seven_days":{"start_date":(today-timedelta(days=7)),"end_date":(today+timedelta(days=1)),"order":0},
            "one_month":{"start_date":(today-timedelta(days=30)),"end_date":(today-timedelta(days=8)),"order":1},
            "three_months":{"start_date":(today-timedelta(days=3*30)),"end_date":(today-timedelta(days=30)),"order":2},
            "one_year":{"start_date":(today-timedelta(days=365)),"end_date":(today-timedelta(days=3*30)),"order":3},
            "more_years":{"start_date":(today-timedelta(days=2*365)),"end_date":(today-timedelta(days=365)),"order":4}
        }
    def get_result(self):
        stats= self.get_stats()
        result = ['']*len(stats)
        for stat in stats:
            result[stats[stat]["order"]] = {"stat_value":ReportCountBetweenDates(stats[stat]["start_date"],stats[stat]["end_date"]),"stat_name":stat}
        return result


