var ridersToDelete = [];

$(document).ready(function() {
	$("#deleteSubmitButton").submit(function() {
		$(".deleteBox").each(function(index) {
			if ($(this).is(":checked")) {
				ridersToDelete.push($(this).attr("id"));
			}
		});
		$.post('/delete-riders', {
				ids: ridersToDelete
		});
	});

	$("#addRiderButton").submit(function() {
		$.post('/add-rider', {
				riderName: $("#newRiderName").val()
		});
	});
});