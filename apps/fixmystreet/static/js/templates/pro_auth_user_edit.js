$(function() {
    var $manager = $(':checkbox[name=manager]');
    var $leader = $(':checkbox[name=leader]');
    var $contractor = $(':checkbox[name=contractor]');
    var $agent = $(':checkbox[name=agent]');

    $leader.prop('disabled', true); // leader not editable

    $leader.change(function () {
        var leader = $leader.prop('checked');
        var manager = $manager.prop('checked');

        $contractor.prop('disabled', leader);
        $agent.prop('disabled', leader || manager);
    }).change();

    $manager.change(function () {
        var leader = $leader.prop('checked');
        var manager = $manager.prop('checked');

        $agent.prop('disabled', leader || manager);
    }).change();


    // $contractor.change(function () {
    //     var agent = $agent.prop('checked');
    //     var contractor = $contractor.prop('checked');

    //     // $leader.prop('disabled', agent || contractor); // leader not editable
    // }).change();

    $agent.change(function () {
        var agent = $agent.prop('checked');
        var contractor = $contractor.prop('checked');

        // $leader.prop('disabled', agent || contractor); // leader not editable
        $manager.prop('disabled', agent);
    }).change();
});