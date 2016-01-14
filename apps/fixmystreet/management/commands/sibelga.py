from django.core.management.base import BaseCommand, CommandError
from apps.fixmystreet.models import Report

class Command(BaseCommand):
    help = 'Update sibelga incidents (one time script)'

    def handle(self, *args, **options):
        incidents = [884,17513,18606,18574,18679,18900,19076,19200,8412,8413,19363,19364,19368,19597,19746,8532,19789,19932,19960,20199,20200,20189,20217,20231,20197,20366,20470,18884,20735,18706,18648,19394,20308,20707,20706,20705,18675,18758,18754,18827,20766,20929,17693,17694,17683,17731,18553,18592,18594,18595,18597,17723,18708,18966,19014,19201,19209,19213,19228,19012,19402,19750,19616,19635,19657,19763,19762,19632,20172,20241,20328,18559,20364,20643,20700,20718,20762,20999,21001,14149,17755,17757,17908,18858,18910,18946,19041,19244,19256,19631,19545,19630,19751,19749,19849,20145,20376,20452,20450,20561,20600,19244,20276,15010,19016,19436,20258,20415,20451,20556,20665,18636,18712,18856,18875,18953,18931,19502,19610,20890,19696,19808,19917,20025,20040,20056,20045,20033,20310,20378,20358,20466,20655,20704,20761,20755,20837,20838,20878,20879,20887,20885,20883,20884,20771,20772,19202,16609,18659,19362,19359,19877,20143,20220,20288,20291,20298,20299,20297,20296,20294,20293,20292,20905,20926,20930,20992,20982,18609,19464,20239,19614,19613,8859,20765,18842,19279,19815,20307,8713,17962,16382,18629,18974,19048,19568,19497,19667,19666,18732,18498,18497,20205,20261,20396,20262,11250,19497,20772,8462,20880,18892,19033,19914,19145,19308,19438,19485,19527,19526,19601,19600,19599,19911,19910,19913,20037,20440,20596,20597,20598,20804,19186,19930,19832,20290,18724,18926,19141,19184,19135,19510,19418,19420,19134,19133,19132,19131,19127,19125,19118,19122,19760,19141,18699,18854,19019,18699,19991,20035,20315,20809,20810,20809,20808,20830]
        # Incidents pour le test du script en dev
        # 36218 => Incident non sibelga
        # 32620 => Sans suite (REFUSED)
        # 32621 => CLOSED
        # 32623 => MERGED
        # 32619 => Sibelga eclairage (non cloture)
        # 32624 => Impetrant sibelga (non cloture)
        # 32626 => Impetrant sibelga (signale solved)
        # incidents = [32618,32619,32620,32621,32623,32624,32626]
        self.stdout.write('"ID";"STATUS"')
        for i in incidents:
            try:
                report = Report.objects.get(pk=i)
                if report.is_refused():
                    self.stdout.write('"{}";"CURRENT STATUS REFUSED"'.format(i))
                    continue
                elif report.status in Report.REPORT_STATUS_CLOSED or report.status in Report.REPORT_STATUS_OFF:
                    self.stdout.write('"{}";"CURRENT STATUS UNCHANGEABLE"'.format(i))
                    continue
                elif report.is_merged():
                    self.stdout.write('"{}";"CURRENT STATUS MERGED"'.format(i))
                    continue

                if report.responsible_entity.id == 143 or report.responsible_department.id == 171:
                    #Sibelga to close
                    report.close()
                    self.stdout.write('"{}";"CLOSED"'.format(i))
                elif report.contractor and report.contractor.id == 60:
                    #Sibelga to solve
                    if report.is_solved() or not report.is_markable_as_solved():
                        self.stdout.write('"{}";"CURRENT STATUS SOLVED OR NOT SOLVABLE"'.format(i))
                    else:
                        report.solve()
                        self.stdout.write('"{}";"SOLVED"'.format(i))
                else:
                    self.stdout.write('"{}";"NOT SIBELGA"'.format(i))

            except Report.DoesNotExist:
                self.stdout.write('"{}";"NOT FOUND"'.format(i))
