// Pagination : a bit tricky
var previousPage = document.getElementById('previousPage');
var nextPage     = document.getElementById('nextPage');

var currentPage = 1;
var maxItemsPerPage  = 6;

function paginateResults() {

    var reportsMergeable = document.getElementsByClassName('reportsMergeable');
    var reportsVisible = [];

    // Get visible reports only
    for (var i=0, mergeableLength=reportsMergeable.length; i < mergeableLength; i++) {

        if (!reportsMergeable[i].hidden) {
            reportsVisible.push(reportsMergeable[i]);
        }

    }

    // Show only reports in current page
    var minIndex = (currentPage - 1) * maxItemsPerPage;
    var maxIndex = currentPage * maxItemsPerPage;

    for (var j=0, visibleLength=reportsVisible.length; j < visibleLength; j++) {

        if ( (j >= minIndex) && (j < maxIndex) ) {
            reportsVisible[j].classList.remove('hidden');
        } else {
            reportsVisible[j].classList.add('hidden');
        }

    }

    // Show/Hide previous button
    if (currentPage == 1) {
        previousPage.classList.add('hidden');
    } else {
        previousPage.classList.remove('hidden');
    }

    // Show/Hide next button
    if (maxIndex >= visibleLength) {
        nextPage.classList.add('hidden');
    } else {
        nextPage.classList.remove('hidden');
    }

}

previousPage.addEventListener('click', function() {
    currentPage--;
    paginateResults();
});
nextPage.addEventListener('click', function() {
    currentPage++;
    paginateResults();
});

function loadModal(reportId, reportDate, reportCategory, reportAddress, marker) {
    // note : postMethod and currentReport are initialized in merge.html

    var selectedReport      = {};
    selectedReport.date     = reportDate;
    selectedReport.marker   = STATIC_URL + marker;
    selectedReport.id       = reportId;
    selectedReport.category = reportCategory;
    selectedReport.address  = reportAddress;

    var olderReport;
    var newerReport;

    // Set one_incident to current (currentReport is initialized in merge.html)
    if (currentReport.date < selectedReport.date) {
        olderReport = currentReport;
        newerReport = selectedReport;

        document.getElementById('olderToMerge').classList.add("one_incident");
        document.getElementById('newerToMerge').classList.remove("one_incident");
    } else {
        olderReport = selectedReport;
        newerReport = currentReport;

        document.getElementById('newerToMerge').classList.add("one_incident");
        document.getElementById('olderToMerge').classList.remove("one_incident");
    }

    document.getElementById('oldertoMergeMarker').setAttribute('src', olderReport.marker);
    document.getElementById('oldertoMergeNumber').innerHTML   = olderReport.id;
    document.getElementById('oldertoMergeCategory').innerHTML = olderReport.category;
    document.getElementById('oldertoMergeAddress').innerHTML  = olderReport.address;

    document.getElementById('newertoMergeMarker').setAttribute('src', newerReport.marker);
    document.getElementById('newertoMergeNumber').innerHTML   = newerReport.id;
    document.getElementById('newertoMergeCategory').innerHTML = newerReport.category;
    document.getElementById('newertoMergeAddress').innerHTML  = newerReport.address;

    document.getElementById('reportToMergeInput').value = reportId;

    var formMerge = document.getElementById('formMerge');
    formMerge.action = postMethod + "?mergeId=" + reportId; //postMethod is initialized in merge.html

    $('#modalMerge').modal();
}
$(document).ready(function() {
  $('.carousel').each(
    function(id, obj){
      if($(this).find('p').length < 2){
        $(this).find('.carousel-control').remove();
      }
    }
  );
});
