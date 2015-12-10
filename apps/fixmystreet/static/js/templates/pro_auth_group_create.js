var users_field          = document.querySelector('select[name="users"]');
var users_list           = $('#memberships');


 $(function(){
     if(IS_MANAGER && !IS_LEADER) {
         $.each($("#id_group_type").find("option"), function (idx, value) {
             if (value.value != "agent") {
                 $(value).remove();
             }
         });
     }
 });


// Init event
users_list.delegate('.delete', 'click', function removeMembership(evt) {
    // AJAX request to remove membership
    evt.preventDefault();

    var user = $(this).closest('tr');
    var membership_id = user.prop('id');

    user.addClass('loading');
    $.get( "/pro/groups/membership/remove/" + membership_id + "/", function(data) {
        user.removeClass('loading');
        if (data == 'OK') {
            user.remove();
            refreshDisabledUser();
        }
    });
});

// Init event
users_list.delegate('.contact', 'change', function setContactMembership(evt) {
    // AJAX request to set membership as default contact

    var user = $(this).closest('tr');
    var membership_id = user.prop('id');

    user.addClass('loading');
    $.get( "/pro/groups/membership/contact/" + membership_id + "/", function(data) {
        user.removeClass('loading');
        if (data == 'OK') {
            users_list.find('.contact').prop('checked', false);
            users_list.find('.delete').prop('disabled', false);
            user.find('.contact').prop('checked', true);
            user.find('.delete').prop('disabled', true);
        }
    });
});

users_field.addEventListener('change', function addMembership() {
    var $this = $(this);
    var user_id = $this.val();

    if (!user_id) {
        return;
    }

    $this.addClass('loading');
    // AJAX request to add membership
    $.getJSON("/pro/groups/membership/add/" + GROUP_ID + "/" + user_id + "/")
        .success(function(data) {

            $this.removeClass('loading');
            $this.val(null);
            if (data.status == 'OK') {
                var userOption = $this.find('option[value=' + user_id + ']');

                var membership_id = data.membership_id;

                var new_user = $('#memberships .hidden').clone();
                new_user.removeClass('hidden');
                new_user.prop("id", membership_id).data('user', user_id);
                new_user.find('.name').html(userOption.text());

                if (!users_list.find('tr').not('.hidden').length) {
                    new_user.find('.contact').prop('checked', true);
                    new_user.find('.delete').prop('disabled', true);
                }
                users_list.append(new_user);
                refreshDisabledUser();
            }
        }).error(function (error) {
            $this.removeClass('loading');
            $this.val(null);
            console.error(error);
        });
});

function refreshDisabledUser() {
    options = $(users_field).find('option');
    options.prop('disabled', false);

    $('#memberships tr').each(function (index, row) {
        var user_id = $(row).data('user');
        var userOption = options.filter('[value=' + user_id + ']');
        userOption.prop('disabled', true);
    });
}
refreshDisabledUser();