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
	$scope.postUserAttributes = function() {
		if($('#category').val().trim() === "") {
			console.error("Category cannot be null!!");
			return;
		}
		
		var post_data = {Attributes: {}, Category: {}};
		for(var i = 0; i < $scope.booleanAttributes.length; i++) {
			post_data.Attributes[$scope.booleanAttributes[i].id] = $scope.booleanAttributes[i].selected
		}
		for(var i = 0; i < $scope.multiValuedAttributes.length; i++) {
			post_data.Attributes[$scope.multiValuedAttributes[i].id] = $scope.multiValuedAttributes[i].selected
		}
		post_data.Category = $scope.selectedCategory
		
		$.ajax({
			url:"/predict",
			type: "POST",
			contentType:"application/json",
			dataType:"json",
			data: JSON.stringify(post_data)
		}).done(function(response) {
			$("#successdiv").show()
			$("#successrating").text((response*10).toFixed(2) + "%")
			$("#percentimprovement").text("+0.0%")
		})
	}

});