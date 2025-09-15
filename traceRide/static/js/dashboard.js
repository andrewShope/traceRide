var deletionList = [];

$(document).ready(function() {
	$("#deleteSubmitButton").submit(function() {
		$(".deleteBox").each(function(index) {
			if ($(this).is(":checked")) {
				deletionList.push($(this).attr("id"));
			}
		});
		$.post('/delete', {
				ids: deletionList
		});
	});
});