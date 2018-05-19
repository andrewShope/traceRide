var donationMessageText = "Thanks for your pledge! We will email you shortly to confirm.";

function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}

function validateCurrency(num) {
	if (num > 0)
		return true;
	else
		return false;
}

function validateFields(city, state, firstName, lastName, emailAddress, pledgeAmount, riderName, donationCenter) {
	var flag = true;
	if (city === "")
		flag = false;
	if (state === "")
		flag = false;
	if (firstName === "") 
		flag = false;
	if (lastName === "")
		flag = false;
	if (validateEmail(emailAddress) === false)
		flag = false;
	if (validateCurrency(pledgeAmount) === false)
		flag = false;
	if (riderName === "")
		flag = false;
	if (donationCenter === "")
		flag = false;

	return flag;
}

$(document).ready(function(){
	$("#submitButton").bind("click", function() {
		city = $("#city").val();
		state = $("#state").val();
		firstName = $("#firstName").val();
		lastName = $("#lastName").val();
		emailAddress = $("#inputEmail").val();
		pledgeAmount = $("#pledgeAmount").val();
		riderName = $("#sponsoredRider option:selected").text();
		donationCenter = $("#donationCenter option:selected").text();
		if (validateFields(city, state, firstName, lastName, emailAddress, pledgeAmount, riderName, donationCenter)) {
			$.post('/pledge', {
				firstName: firstName,
				lastName: lastName,
				city: city,
				state: state,
				pledgeAmount: pledgeAmount,
				emailAddress: emailAddress,
				riderName: riderName,
				donationCenter: donationCenter
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
					alert("There was an error processing your request.");
			});
		}
		else {
			alert("Please check your information and try again.")
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

	$("#sponsoredRider").change(function () {
		if (window.riderPledges[$("#sponsoredRider option:selected").text()] == undefined) {
			$("#riderSum").text("0.00");
		} else {
		$("#riderSum").text(window.riderPledges[$("#sponsoredRider option:selected").text()].toFixed(2));
		}	
	});

	$("#donationCenter").change(function () {
		if (window.centerPledges[$("#donationCenter option:selected").text()] == undefined) {
			$("#centerSum").text("0.00");
		} else {
		$("#centerSum").text(window.centerPledges[$("#donationCenter option:selected").text()].toFixed(2));
		}	
	});
});
