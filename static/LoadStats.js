// LoadStats.js

$(document).ready(function() {
    // Define a function to handle form submission
    $('#stats-form').submit(function(event) {

        event.preventDefault();


        $('#loading').removeAttr('hidden');
        $('#stats-view-container').hide();

        var formData = $(this).serialize();

        $.ajax({
            type: 'POST',
            timeout: 600000,
            url: '/',
            data: formData,
            success: function(data) {
                console.log(data);
                $('#loading').attr('hidden', true);
                $('#stats-view-container').show();
                $('#stats-view-container').html(data);
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);

                $('#loading').attr('hidden', true);
                $('#stats-view-container').html('<p>Error fetching player statistics. Please try again later.</p>').show();
            }
        });
    });
});
