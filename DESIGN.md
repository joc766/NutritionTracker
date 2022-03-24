YALEFITNESS DESIGN:

First, I will describe how I used SQL databases in order to organize my website and store important data.

The "Daily" table contains each user's daily needs for calories, carbs, protein, and fats as well as an id for each user. The permcals and the calories fields
are used to differentiate between the users constant daily caloric needs and their caloric needs each day taking into account excercise. This table is used when
inputting information into the graphs on the homepage. The homepage displays the "calories" column so that the user can see their allowance for that day. The
div below the "Set Goals" page shows the user's constant daily recommended amounts for each category.

The "Nutrition" table hold the user's height, weight, goalweight, gender, activity level, age, and id. This information is originally used to calculate daily
caloric and macronutrient needs for each user. It is also used when calculating how many calories are burned by each user when they do a specific excercise.
These excercises have different amounts of calories burned per hour for different weight ranges (I found this data in a Harvard study which is
referenced in the source code).

The "favorites" table tracks how many times a given food is input by a user. It contains all the nutrtional information about each food and the number of times
the user has input this food. I used this table to make the Quick Add section of the homepage.

The "food" table contains all the food and nutritional information for all the food the user eats in a given day. As seen in the homepage function, this table
is cleared every day at midnight. This information is used in displaying the charts with the user's daily intake.

The "lastaccessed" table is used when resetting the "foods" table. It updates the last date each user visited the site, and if the date is different than the
information in the database, it clears the "foods" table. I probably could've just put this in the "users" table

The "users" table contains the username, password hash, and id of each user. It comes from the Finance website.

I calculated the nutritional needs of each user using the Harris Benedict Equation which can be found in many places. It first calculates the basal metabolic
rate (bmr) of each user and then accounts for activity levels. Then, I used recommendations from livestrong.com and healthline.com to come up with formulas
for each user's needs for each nutrient based on whether or not they want to gain or lose a little or significant amount of weight.

I calculated the excercise needs using information from a Harvard study on the number of calories burned per hour in many common excercises.

The charts on the homepage were made using Google's templates for charts with a few modifications on my part like that of the title, the colors of the bars, and
obviously the data. The data is dynamically updated using jinja and python. This is the link https://developers.google.com/chart.

The majority of my webpage uses similar input structures and select forms in order to gain information from the user. Another touch that I added to my page
is the "Welcome" sign at the top of the page which uses the :after property in CSS in order to create a second and staggered text to create an interesting effect.