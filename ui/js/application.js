var app = angular.module('businessInsights', []);
app.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
}]);
app.controller('businessInsightsCtrl', function($scope) {
    
	$scope.categories = ['Active Life', 'Adult Entertainment', 'Afghan', 'Arcades', 'Arts & Entertainment', 'Automotive', 'Bagels', 'Bakeries', 'Barbeque', 'Barbers', 'Barre Classes', 'Bars', 'Beauty & Spas', 'Beer', 'Beer Bar', 'Bistros', 'Brasseries', 'Breakfast & Brunch', 'Breweries', 'Bubble Tea', 'Buffets', 'Burgers', 'Butcher', 'Cafes', 'Cajun/Creole', 'Candy Stores', 'Car Wash', 'Casinos', 'Caterers', 'Cheese Shops', 'Cheesesteaks', 'Chicken Shop', 'Chicken Wings', 'Chocolatiers & Shops', 'Cocktail Bars', 'Coffee & Tea', 'Coffee Roasteries', 'Comfort Food', 'Convenience Stores', 'Cosmetics & Beauty Supply', 'Creperies', 'Cupcakes', 'Custom Cakes', 'Dance Clubs', 'Delicatessen', 'Delis', 'Department Stores', 'Desserts', 'Dim Sum', 'Diners', 'Discount Store', 'Dive Bars', 'Do-It-Yourself Food', 'Donuts', 'Drugstores', 'Education', 'Electronics', 'Ethnic Food', 'Event Planning & Services', 'Falafel', 'Farmers Market', 'Fashion', 'Fast Food', 'Fish & Chips', 'Fitness & Instruction', 'Florists', 'Flowers & Gifts', 'Food Court', 'Food Delivery Services', 'Food Stands', 'Food Trucks', 'Fruits & Veggies', 'Gas Stations', 'Gastropubs', 'Gay Bars', 'Gelato', 'Gift Shops', 'Gluten-Free', 'Grocery', 'Hair Removal', 'Hair Salons', 'Hair Stylists', 'Halal', 'Health & Medical', 'Health Markets', 'Herbs & Spices', 'Home & Garden', 'Home Services', 'Hookah Bars', 'Hot Dogs', 'Hot Pot', 'Hotels', 'Hotels & Travel', 'Ice Cream & Frozen Yogurt', 'Imported Food', 'International Grocery', 'Internet Cafes', 'Irish Pub', 'Juice Bars & Smoothies', 'Karaoke', 'Kosher', 'Local Flavor', 'Local Services', 'Lounges', 'Meat Shops', 'Men\'s Hair Salons', 'Mexican', 'Mobile Phones', 'Modern European', 'Music Venues', 'Nightlife', 'Noodles', 'Organic Stores', 'Party & Event Planning', 'Patisserie/Cake Shop', 'Photography Stores & Services', 'Pizza', 'Poke', 'Pool Halls', 'Poutineries', 'Professional Services', 'Pubs', 'Ramen', 'Salad', 'Sandwiches', 'Seafood', 'Seafood Markets', 'Shaved Ice', 'Shopping', 'Soul Food', 'Soup', 'Southern', 'Specialty Food', 'Sports Bars', 'Steakhouses', 'Street Vendors', 'Sushi Bars', 'Tacos', 'Tapas Bars', 'Tapas/Small Plates', 'Tea Rooms', 'Tex-Mex', 'Tobacco Shops', 'Vegan', 'Vegetarian', 'Venues & Event Spaces', 'Vitamins & Supplements', 'Waffles', 'Wine & Spirits', 'Wine Bars', 'Wineries', 'Wraps']
	
	$scope.booleanAttributes = [
		{'id':'BusinessAcceptsCreditCards', 'value':'Accepts Business Cards', selected:0},
		{'id':'BikeParking', 'value':'Bike Parking', selected:0},
		{'id':'Caters', 'value':'Caters', selected:0},
		{'id':'GoodForKids', 'value':'Good for Kids', selected:0},
		{'id':'HasTV', 'value':'Has TV', selected:0},
		{'id':'OutdoorSeating', 'value':'Outdoor Seating', selected:0},
		{'id':'RestaurantsDelivery', 'value':'Delivery Service', selected:0},
		{'id':'RestaurantsGoodForGroups', 'value':'Good for Groups', selected:0},
		{'id':'RestaurantsReservations', 'value':'Reservation Service', selected:0},
		{'id':'RestaurantsTableService', 'value':'Table Service', selected:0},
		{'id':'RestaurantsTakeOut', 'value':'Take Out Service', selected:0},
		{'id':'WheelchairAccessible', 'value':'Wheelchair Accessible', selected:0}
	]
	
	$scope.multiValuedAttributes = [
		{'id':'Alcohol', 'value':'Alochol', 'options':[{'id': 'none', 'value':'None'}, {'id': 'beer_and_wine', 'value':'Beer and Wine'}, {'id': 'full_bar', 'value':'Full Bar'}, {'id': 'na', 'value':'Not Applicable'}], 'selected':'na'},
		{'id':'NoiseLevel', 'value':'Noise', 'options':[{'id': 'very_loud', 'value':'Very Loud'}, {'id': 'loud', 'value':'Loud'}, {'id': 'average', 'value':'Average'}, {'id': 'quiet', 'value':'Quiet'}, {'id': 'na', 'value':'Not Applicable'}], 'selected':'na'},
		{'id':'RestaurantsAttire', 'value':'Attire', 'options':[{'id': 'casual', 'value':'Casual'}, {'id': 'dressy', 'value':'Dressy'}, {'id': 'formal', 'value':'Formal'}, {'id': 'na', 'value':'Not Applicable'}], 'selected':'na'},
		{'id':'RestaurantsPriceRange2', 'value':'Price', 'options':[{'id': 1, 'value':'Low'}, {'id': 2, 'value':'Medium'}, {'id': 3, 'value':'High'}, {'id': 4, 'value':'Very High'}, {'id': 'na', 'value':'Not Applicable'}], 'selected':'na'},
		{'id':'WiFi', 'value':'WiFi', 'options':[{'id': 'no', 'value':'No'}, {'id': 'free', 'value':'Free'}, {'id': 'paid', 'value':'Paid'}, {'id': 'na', 'value':'Not Applicable'}], 'selected':'na'}
	]
	$scope.selectedCategory = undefined
	$scope.errordetails = undefined
	$scope.suggestions = 
	$scope.postUserAttributes = function() {
		$("#error").hide();
		$("#successdiv").hide();
		$("#insightstable").hide();
		var businesslocation = $("#distanceac").val()
		$.get("/elevation?location=" + businesslocation, function( data ) {
			elevation = data
			if($('#category').val().trim() === "") {
				console.error("Category cannot be null!!");
				return;
			}
			
			var post_data = {Attributes: {}, Category: {}};
			post_data.Attributes['elevation'] = parseFloat(elevation)
			for(var i = 0; i < $scope.booleanAttributes.length; i++) {
				post_data.Attributes[$scope.booleanAttributes[i].id] = $scope.booleanAttributes[i].selected
			}
			for(var i = 0; i < $scope.multiValuedAttributes.length; i++) {
				post_data.Attributes[$scope.multiValuedAttributes[i].id] = $scope.multiValuedAttributes[i].selected
			}
			post_data.Category = $scope.selectedCategory
			console.log(post_data)
			$.ajax({
				url:"/predict",
				type: "POST",
				contentType:"application/json",
				dataType:"json",
				data: JSON.stringify(post_data),
				success: function(resultData){
					console.log(resultData);
					$("#successdiv").show()
					$("#successrating").text((resultData.current_rating*10).toFixed(2) + "%")
					var improvement = (resultData.improved_rating*10 - resultData.current_rating*10).toFixed(2);
					var improvement_str = "";
					if(improvement > 0) {
						improvementcolor = "green";
						improvement_str += "+" + improvement + "%";
					}
					else {
						improvementcolor = "red";
						improvement_str += improvement + "%";
					}
					$("#percentimprovement").text(improvement_str);
					$("#percentimprovement").css("color", improvementcolor);
					$("#successratingafter").text((resultData.improved_rating*10).toFixed(2) + "%");
					$("#successratingafter").css("color", improvementcolor);
					var suggestedAttributeValues = resultData.suggested_preferences;
					var difference = {}
					for(attributes in suggestedAttributeValues) {
						difference[attributes] = {}
						difference[attributes].current = post_data.Attributes[attributes]
						difference[attributes].suggested = suggestedAttributeValues[attributes]
					}
					for(var i = 0; i < $scope.booleanAttributes.length; i++) {
						difference[$scope.booleanAttributes[i].id].name = $scope.booleanAttributes[i].value;
						if(difference[$scope.booleanAttributes[i].id].current)
							difference[$scope.booleanAttributes[i].id].current = 'Available'
						else
							difference[$scope.booleanAttributes[i].id].current = 'Not Available'
						if(difference[$scope.booleanAttributes[i].id].suggested)
							difference[$scope.booleanAttributes[i].id].suggested = 'Available'
						else
							difference[$scope.booleanAttributes[i].id].suggested = 'Not Available'
					}
					for(var i = 0; i < $scope.multiValuedAttributes.length; i++) {
						difference[$scope.multiValuedAttributes[i].id].name = $scope.multiValuedAttributes[i].value;
						for(var j = 0; j < $scope.multiValuedAttributes[i].options.length; j++) {
							if($scope.multiValuedAttributes[i].options[j].id == difference[$scope.multiValuedAttributes[i].id].current)
								difference[$scope.multiValuedAttributes[i].id].current = $scope.multiValuedAttributes[i].options[j].value;
							if($scope.multiValuedAttributes[i].options[j].id == difference[$scope.multiValuedAttributes[i].id].suggested)
								difference[$scope.multiValuedAttributes[i].id].suggested = $scope.multiValuedAttributes[i].options[j].value;
							
						}
					}
					$("#suggestiontable tbody tr").remove();
					$("#insightstable").show();
					var suggestion_table = $("#suggestiontable");
					for(suggestion in difference) {
						if(suggestion && difference[suggestion].current != difference[suggestion].suggested) {
							$("#suggestiontable tbody").append("<tr><td style=\"font-style: italic; font-weight: bold\">" + difference[suggestion].name + "</td><td style=\"color: red;\">" + difference[suggestion].current + "</td><td style=\"color: green;\">" + difference[suggestion].suggested + "</td></tr>")
						}
					}
				},
				error: function(response){
					if(response.responseJSON.message.current_rating) {
						$("#successdiv").show()
						$("#successrating").text((response.responseJSON.message.current_rating*10).toFixed(2) + "%")
					}
					$("#error").show();
					$("#errordetails").text(response.responseJSON.message.error);
				}
			})
		}).fail(function(jqXHR,status,err){
			$("#error").show();
			$("#errordetails").text(jqXHR.responseJSON.message.error);
		})
		
	}

});
 function initAutocomplete() {
	// Create the autocomplete object, restricting the search to geographical
	// location types.
	autocomplete = new google.maps.places.Autocomplete(
		/** @type {!HTMLInputElement} */(document.getElementById('distanceac')),
		{types: ['geocode']});

	// When the user selects an address from the dropdown, populate the address
	// fields in the form.
}