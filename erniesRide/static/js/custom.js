var donationMessageText = "Thanks for your pledge! We will be sending you a confirmation email shortly!";

function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}

function stripDollarSign(pledgeString) {
	if (pledgeString.startsWith("$"))
		pledgeString = pledgeString.slice(1);
	return pledgeString;
}

function validateCurrency(num) {
	num = stripDollarSign(num);

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
		pledgeAmount = stripDollarSign(pledgeAmount);
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

	// FORM VALIDATION

	$("#firstName").on("keyup", function () {
		if ($("#firstName").val().length > 0) {
			$("#firstName").parent().addClass("has-success");
			$("#firstName").parent().removeClass("has-error");
		} else {
			$("#firstName").parent().addClass("has-error");
		}
	});

	$("#lastName").on("keyup", function () {
		if ($("#lastName").val().length > 0) {
			$("#lastName").parent().addClass("has-success");
			$("#lastName").parent().removeClass("has-error");
		} else {
			$("#lastName").parent().addClass("has-error");
		}
	});

	$("#city").on("keyup", function () {
		if ($("#city").val().length > 0) {
			$("#city").parent().addClass("has-success");
			$("#city").parent().removeClass("has-error");
		} else {
			$("#city").parent().addClass("has-error");
		}
	});

	$("#state").on("keyup", function () {
		if ($("#state").val().length > 0) {
			$("#state").parent().addClass("has-success");
			$("#state").parent().removeClass("has-error");
		} else {
			$("#state").parent().addClass("has-error");
		}
	});

	$("#inputEmail").on("keyup", function () {
		if (!validateEmail($("#inputEmail").val())) {
			$("#inputEmail").parent().addClass("has-error");
		} else {
			$("#inputEmail").parent().removeClass("has-error");
			$("#inputEmail").parent().addClass("has-success");
		}
	});

	$("#sponsoredRider").change(function () {
		if ($("#sponsoredRider option:selected").text() === "") {
			$("#sponsoredRider").parent().addClass("has-error");
		} else {
			$("#sponsoredRider").parent().removeClass("has-error");
			$("#sponsoredRider").parent().addClass("has-success");
		}	
	});

	$("#donationCenter").change(function () {
		if ($("#donationCenter option:selected").text() === "") {
			$("#donationCenter").parent().addClass("has-error");
		} else {
			$("#donationCenter").parent().removeClass("has-error");
			$("#donationCenter").parent().addClass("has-success");
		}	
	});

	$("#pledgeAmount").on("keyup", function () {
		if (validateCurrency($("#pledgeAmount").val())) {
			$("#pledgeAmount").parent().removeClass("has-error");
			$("#pledgeAmount").parent().addClass("has-success");
		} else {
			$("#pledgeAmount").parent().addClass("has-error");
		}
	});

});

