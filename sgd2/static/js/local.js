function search(search_str) {
	var url = "/gene/" + pmid;
	$.post(url, function(data) {
		input = "Error:"
		if(data.substring(0, input.length) === input) {
			document.getElementById(pmid + "_validation_error").innerHTML = data
			document.getElementById(pmid + "_validation_error").style.display = 'block';
		}
		else {
			$("#" + pmid).empty().append("<div class='alert alert-success'><h4>Success!</h4>" + data + "</div>");
		}
	});

}