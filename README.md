# cookbook
## Table of contents
* [Introduction](#Introduction)
* [Setup](#setup)


## Introduction
Manage a database for recipes with text-based user input.

Shows menus to get user input like this:

```
  1) Show recipe names.
  2) Search recipes by ingredient.
  3) Show ingredients.
  4) Show whole recipe.
  5) Add new recipe.
  6) Modify recipe.
  7) Delete recipe.
  q) Quit this menu.

Action: 
```

Displays completed recipes like this:
```
Recipe: Garlic Bread
Prep Time: 5 mins
Cook Time: 3 mins

Ingredients:

| Index |               Ingredient               |  Amount  |   Unit   |             Prep             | Optional |
==================================================================================================================
|     1 |              garlic salt               |    2     |   tsp    |                              |    n     |
|     2 |                 bread                  |    6     |  slices  |                              |    n     |
|     3 |                 butter                 |    1     |   Tbsp   |                              |    n     |

Instructions: Preheat broiler. Butter bread. Sprinkle on garlic salt. Place bread on cookie sheet on top rack for 
    3 minutes or until bread starts to become crispy. tasty!
```

Future work:

* Search by multiple ingredients so user can input what ingredients they have on hand and get a list of recipes they can make.
* Add recipe by pasting in link to online recipe url, which the program then parses to auto-create the recipe.
* Create Django project with the same functionality, but available in web browser with functional UI.

## Setup:
Written with python 3.8.2  
To run the project, clone it to a local library and navigate to that library in the Terminal  
On Windows:  

```
python -m venv env
env/Scripts/Activate
pip install -r requirements.txt
main.py
```