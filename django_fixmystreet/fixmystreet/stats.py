# pylint: disable=C0326
from datetime import date, timedelta

from django.core.urlresolvers import reverse
from django.db import connection
from django.utils.translation import ugettext_lazy as _

from django_fixmystreet.fixmystreet.models import Report


DEFAULT_SQL_INTERVAL = "30 days"


class ReportCount(object):

    def __init__(self, interval):
        self.interval = interval

    def dict(self):
        return({
            "recent_new":     "COUNT( CASE WHEN age(clock_timestamp(), reports.created) < interval '%s' THEN 1 ELSE NULL END )" % self.interval,
            "recent_fixed":   "COUNT( CASE WHEN age(clock_timestamp(), reports.close_date) < interval '%s' AND reports.is_fixed = TRUE THEN 1 ELSE NULL END )" % self.interval,
            "recent_updated": "COUNT( CASE WHEN age(clock_timestamp(), reports.modified) < interval '%s' AND reports.is_fixed = FALSE AND reports.modified != reports.created THEN 1 ELSE NULL END )" % self.interval,
            "old_fixed":      "COUNT( CASE WHEN age(clock_timestamp(), reports.close_date) > interval '%s' AND reports.is_fixed = TRUE THEN 1 ELSE NULL END )" % self.interval,
            "old_unfixed":    "COUNT( CASE WHEN age(clock_timestamp(), reports.close_date) > interval '%s' AND reports.is_fixed = FALSE THEN 1 ELSE NULL END )" % self.interval
        })


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
        return self.results


class UsersAssignedToCategories(SqlQuery):

    def __init__(self, mainCategoryId, secondaryCategoryId, organisationId):
        SqlQuery.__init__(self)
        self.base_query = """
            SELECT FilterU.first_name, FilterU.last_name
            FROM (
                SELECT auth_user.first_name, auth_user.last_name, auth_user.id
                FROM (
                    SELECT DISTINCT fixmystreet_fmsuser_categories.fmsuser_id
                    FROM (
                        SELECT id
                        FROM fixmystreet_reportcategory
                        WHERE fixmystreet_reportcategory.category_class_id = {main_category_id}
                            AND fixmystreet_reportcategory.secondary_category_class_id = {secondary_category_id}
                    ) AS RCat
                    JOIN fixmystreet_fmsuser_categories ON fixmystreet_fmsuser_categories.reportcategory_id = RCat.id
                ) AS UserCat
                JOIN auth_user ON auth_user.id = UserCat.fmsuser_id
            ) AS FilterU
            JOIN (
                SELECT fixmystreet_fmsuser.user_ptr_id
                FROM fixmystreet_fmsuser
                WHERE fixmystreet_fmsuser.organisation_id = {organisation_id}
            ) AS FMSU ON FMSU.user_ptr_id = FilterU.id
        """.format(main_category_id=mainCategoryId, secondary_category_id=secondaryCategoryId, organisation_id=organisationId)
        self.sql = self.base_query


class UserTypeForOrganisation(SqlQuery):

    def __init__(self, typeId, organisationId):
        SqlQuery.__init__(self)
        self.base_query = """
            SELECT Cat.fmsuser_id, Cat.reportcategory_id
            FROM (SELECT fmsuser_id, reportcategory_id FROM fixmystreet_fmsuser_categories WHERE reportcategory_id = {type_id}) AS Cat
            JOIN (SELECT user_ptr_id FROM fixmystreet_fmsuser WHERE fixmystreet_fmsuser.organisation_id = {organisation_id}) AS U ON U.user_ptr_id = Cat.fmsuser_id
        """.format(type_id=typeId, organisation_id=organisationId)
        self.sql = self.base_query


class TypesWithUsersOfOrganisation(SqlQuery):

    def __init__(self, organisationId):
        SqlQuery.__init__(self)
        self.base_query = """
            SELECT A.reportcategory_id, A.fmsuser_id
            FROM (SELECT * FROM fixmystreet_fmsuser_categories) AS A
            JOIN (SELECT user_ptr_id FROM fixmystreet_fmsuser WHERE organisation_id = {organisation_id}) AS B ON B.user_ptr_id = A.fmsuser_id
        """.format(organisation_id=organisationId)
        self.sql = self.base_query


class ReportCountQuery(SqlQuery):
    """
    Report counts.

    recent_new: Number of incidents in status ``CREATED`` that were created within 30 days.
    recent_fixed: Number of incidents in status ``PROCESSED`` that were closed within 30 days.
    recent_updated: Number of incidents in one of the statuses ``REPORT_STATUS_IN_PROGRESS`` that were modified within 30 days.
    For citizens, restrict to "not private".
    """

    def __init__(self, interval=DEFAULT_SQL_INTERVAL, citizen=False):
        SqlQuery.__init__(self)

        #5 years for pro, 1 month for citizens
        #if isUserAuthenticated() == True:
        #      interval = '60 month'
        #
        #interval = '1 day'

        progress = ','.join([str(s) for s in Report.REPORT_STATUS_IN_PROGRESS])
        citizen_filter = "AND NOT private" if citizen else ""
        self.sql = """
            SELECT
                COUNT( CASE WHEN age(clock_timestamp(), reports.created) < interval '{interval}' AND reports.status = {created} {citizen_filter} THEN 1 ELSE NULL END ) AS recent_new,
                COUNT( CASE WHEN age(clock_timestamp(), reports.close_date) < interval '{interval}' AND reports.status = {closed} {citizen_filter} THEN 1 ELSE NULL END ) AS recent_fixed,
                COUNT( CASE WHEN age(clock_timestamp(), reports.modified) < interval '{interval}' AND reports.status IN ({progress}) {citizen_filter} AND reports.modified != reports.created THEN 1 ELSE NULL END ) AS recent_updated,
                COUNT( CASE WHEN age(clock_timestamp(), reports.close_date) > interval '{interval}' AND reports.status = {closed} {citizen_filter} THEN 1 ELSE NULL END ) AS old_fixed,
                COUNT( CASE WHEN age(clock_timestamp(), reports.created) > interval '{interval}' AND reports.status IN ({progress}) {citizen_filter} THEN 1 ELSE NULL END ) AS old_unfixed
            FROM fixmystreet_report AS reports
        """.format(interval=interval, created=Report.CREATED, closed=Report.PROCESSED, progress=progress, citizen_filter=citizen_filter)

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


class CityTotals(ReportCountQuery):

    def __init__(self, interval, city):
        super(CityTotals, self).__init__(interval)
        self.sql = self.base_query + """
            FROM fixmystreet_report AS reports
                LEFT JOIN fixmystreet_ward AS wards ON reports.ward_id = wards.id
                LEFT JOIN fixmystreet_city AS cities ON cities.id = wards.city_id
            WHERE wards.city_id = %d
        """ % city.id


class CityWardsTotals(ReportCountQuery):

    def __init__(self, city):
        super(CityWardsTotals, self).__init__(DEFAULT_SQL_INTERVAL)
        self.url_prefix = "/wards/"
        self.sql = self.base_query + """, wards.name, wards.id
            FROM fixmystreet_ward AS wards
                LEFT JOIN fixmystreet_report reports ON wards.id = reports.ward_id
                JOIN fixmystreet_city AS cities ON wards.city_id = cities.id
                JOIN fixmystreet_province AS province ON cities.province_id = province.id AND cities.id = {city_id}
            GROUP BY wards.name, wards.id
            ORDER BY wards.name
        """.format(city_id=city.id)

    def id(self):
        return self.get_results()[self.index][6]

    def get_absolute_url(self):
        return reverse('ward_show', args=[self.get_results()[self.index][6]])


class AllCityTotals(ReportCountQuery):

    def __init__(self):
        super(AllCityTotals, self).__init__(DEFAULT_SQL_INTERVAL)
        self.url_prefix = "/cities/"
        self.sql = self.base_query + """, cities.name, cities.id, province.name
            FROM cities
                LEFT JOIN wards ON wards.city_id = cities.id
                JOIN province ON cities.province_id = province.id
                LEFT JOIN reports ON wards.id = reports.ward_id
            GROUP BY cities.name, cities.id, province.name
            ORDER BY province.name, cities.name
        """

    def get_absolute_url(self):
        return self.url_prefix + str(self.get_results()[self.index][6])

    def province(self):
        return self.get_results()[self.index][7]

    def province_changed(self):
        if self.index == 0:
            return True
        return self.get_results()[self.index][7] != self.get_results()[self.index-1][7]


# select count(case when reports.created > '2013-04-30 00:00:00' AND reports.created < NOW() AND reports.status = 1 THEN 1 ELSE null end) as count_new,
#        count(case when reports.created > '2013-04-30 00:00:00' AND reports.created < NOW() AND reports.status in (2, 4, 5, 6, 7) THEN 1 ELSE null end) as count_in_progress,
#        count(case when reports.created > '2013-04-30 00:00:00' AND reports.created < NOW() AND reports.status = 3 THEN 1 ELSE null end) as count_closed,
#        count(case when reports.created > '2013-04-30 00:00:00' AND reports.created < NOW() AND reports.status = 9 THEN 1 ELSE null end) as count_refused,
#        count(case when reports.created > '2013-04-30 00:00:00' AND reports.created < NOW() THEN 1 ELSE null end) as count_all
#             from fixmystreet_report as reports;

class ReportCountBetweenDates(SqlQuery):

    def __init__(self, start_date, end_date):
        super(ReportCountBetweenDates, self).__init__()
        progress = ','.join([str(s) for s in Report.REPORT_STATUS_IN_PROGRESS])
        self.sql = """
            SELECT
                COUNT(CASE WHEN reports.created > '{start_date}' AND reports.created < '{end_date}' AND reports.status = {unpublished} THEN 1 ELSE NULL END) AS count_new,
                COUNT(CASE WHEN reports.created > '{start_date}' AND reports.created < '{end_date}' AND reports.status IN ({progress}) THEN 1 ELSE NULL END) AS count_in_progress,
                COUNT(CASE WHEN reports.created > '{start_date}' AND reports.created < '{end_date}' AND reports.status ={closed} THEN 1 ELSE NULL END) AS count_closed,
                COUNT(CASE WHEN reports.created > '{start_date}' AND reports.created < '{end_date}' THEN 1 ELSE NULL END) AS count_all
            FROM fixmystreet_report AS reports
        """.format(start_date=str(start_date), end_date=str(end_date), progress=progress, closed=Report.PROCESSED, unpublished=Report.CREATED)

    def get_count_new(self):
        return self.get_results()[self.index][0]

    def get_count_in_progress(self):
        return self.get_results()[self.index][1]

    def get_count_closed(self):
        return self.get_results()[self.index][2]

    def get_count_all(self):
        return self.get_results()[self.index][3]


class ReportCountStatsPro(object):

    TRANSLATIONS = {
        "seven_days": _("seven_days"),
        "one_month": _("one_month"),
        "three_months": _("three_months"),
        "one_year": _("one_year"),
        "more_years": _("more_years"),
    }

    def get_stats(self):
        today = date.today()
        return {
            "seven_days":   {"start_date": (today - timedelta(days=7)),       "end_date": (today + timedelta(days=1)),      "order": 0},
            "one_month":    {"start_date": (today - timedelta(days=30)),      "end_date": (today - timedelta(days=8)),      "order": 1},
            "three_months": {"start_date": (today - timedelta(days=3 * 30)),  "end_date": (today - timedelta(days=30)),     "order": 2},
            "one_year":     {"start_date": (today - timedelta(days=365)),     "end_date": (today - timedelta(days=3 * 30)), "order": 3},
            "more_years":   {"start_date": (today - timedelta(days=2 * 365)), "end_date": (today - timedelta(days=365)),    "order": 4},
        }

    def get_result(self):
        stats = self.get_stats()
        result = [''] * len(stats)
        for stat in stats:
            result[stats[stat]["order"]] = {
                "stat_value": ReportCountBetweenDates(stats[stat]["start_date"], stats[stat]["end_date"]),
                "stat_name": self.TRANSLATIONS[stat],
                "stat_key": stat,
            }
        return result
