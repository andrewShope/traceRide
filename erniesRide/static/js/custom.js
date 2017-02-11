var donationMessageText = "Thanks for your pledge! We will email you shortly to confirm.";

function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}

function validateCurrency(num) {
	if (num > 0)
		return true
	else
		return false
}

$(document).ready(function(){
	$("#submitButton").bind("click", function() {
		emailAddress = $("#inputEmail").val();
		pledgeAmount = $("#pledgeAmount").val();
		if (validateEmail(emailAddress) && validateCurrency(pledgeAmount)) {
			$.post('/pledge', {
				pledgeAmount: $("#pledgeAmount").val(),
				emailAddress: $("#inputEmail").val()
			}, function(data) {
				if (data.result === 'success') {
					$("#donationSection").fadeOut(2000, function() {
						$("#donationMessage").append("<p>" + "Thank you for your pledge of \
							$" + data.pledgeAmount + " per mile. We will send you an email \
						to confirm." + "</p>");
						$("#donationMessage").css("display", "block");
					});
					$("#pledgeSum").text(data.total)

				}
				else
					alert("Something was wrong");
			});
		}
		else {
			
		}
	});

	$("#pledgeAmount").keyup(function() {
		var valueString = $("#pledgeAmount").val()
		if (valueString.charAt(0) === "$") {
			valueString = valueString.slice(1, valueString.length);
		}
		var value = Number(valueString)*320;
		var message = " x 320 miles = ";
		value = value.toFixed(2);
		if (isNaN(value))
			$("mileText").text(message + "$0.00" + "Maximum Possible Pledge");
		else
			$("#mileText").text(message + "$" + String(value) + " Maximum Possible Pledge");
	});
});
