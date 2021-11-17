# dbproj
Database Class 2021 project 1 Part 3

Account UNI: sk4865

URL: http://35.237.6.11:8111/

DESCRIPTION:
We implemented three main parts, which are searching for the best deal, adding new deal
and deleting a specified deal.
1. Searching: customers can search for best deals that can be offered for them
	Without any specification, the website will ouput all the deals from percentage
		coupons, absolute value coupons, and credit card cashback offer.
	With percentage coupon and absolute value specified, the webpage will only show
		the specified type of coupons.
	With creditcard specified, it will show whether the cashback would be avaliable
		for the product.
2. Adding: when the user enters merchant mode with specified URL, they can add new deal
	The deal should be added in the range of already listed products, merchants,
		third party, and manufacturers.
3. Deleting: when the user wants to delete the existing deal, it can be done in merchant
	mode as well. If the coupon id is entered, it will get deleted from the data base.

Interesting Operations:

 - For the user interface in index.html, we implement the search function for coupons given input product (mandatory), coupon type (optional) and credit card (optional) information. This is interesting because this query almost covers all the tables in the database. We join the coupon results from merchants, manufacturers, and third parties and we need to resolve schema differences among these different tables.
 - For the merchant interface in another.html, we implement adding/deleting coupons for products. For the third party, we have a drop down menu for choosing the third party app. We need to handle the inputs which are strings and parse them into the correct data type to add to our database. The page also presents the updated list of coupons immediately as we add or delete.
