function postUserAttributes() {
	var post_request_data = {
		
		card: $('#card').is(':checked'),
		bikeparking: $('#bikeparking').is(':checked'),
		caters: $('#caters').is(':checked'),
		kids: $('#kids').is(':checked'),
		tv: $('#tv').is(':checked'),
		outdoor: $('#outdoor').is(':checked'),
		delivery: $('#delivery').is(':checked'),
		groups: $('#groups').is(':checked'),
		reservations: $('#reservations').is(':checked'),
		table: $('#table').is(':checked'),
		takeout: $('#takeout').is(':checked'),
		wheelchair: $('#wheelchair').is(':checked'),
		
		alcohol: $('#alcohol').val(),
		noise: $('#noise').val(),
		attire: $('#attire').val(),
		price: $('#price').val(),
		wifi: $('#wifi').val()
	}
	console.log(post_request_data)
	$.ajax({
		url:"/predict",
		type: "POST",
		contentType:"application/json",
		dataType:"json",
		data: JSON.stringify(post_request_data)
	});
}