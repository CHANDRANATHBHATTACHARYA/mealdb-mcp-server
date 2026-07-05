import os
import requests
from mcp.server.fastmcp import FastMCP

mcp=FastMCP(
    "MealDb MCP Server",
    dependencies=["requests"],
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8000)),
)
BASE_URL = "https://www.themealdb.com/api/json/v1/1"

@mcp.tool()
def search_meal_by_name(meal_name: str) -> dict:
    """
    Search for meals by their name.
    """

    try:
        response = requests.get(
            f"{BASE_URL}/search.php",
            params={
                "s": meal_name
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        meals = data.get("meals")

        if meals is None:
            return {
                "success": False,
                "message": f"No meal found with the name '{meal_name}'."
            }

        processed_meals = []

        for meal in meals:

            ingredients = []

            for i in range(1, 21):

                ingredient = meal.get(f"strIngredient{i}")
                measure = meal.get(f"strMeasure{i}")

                if ingredient and ingredient.strip():

                    ingredients.append({
                        "ingredient": ingredient,
                        "measure": measure.strip() if measure else ""
                    })

            processed_meals.append({
                "Meal ID": meal.get("idMeal"),
                "Meal Name": meal.get("strMeal"),
                "Category": meal.get("strCategory"),
                "Cuisine": meal.get("strArea"),
                "Instructions": meal.get("strInstructions"),
                "Ingredients": ingredients,
                "YouTube": meal.get("strYoutube"),
                "Thumbnail": meal.get("strMealThumb")
            })

        return {
            "success": True,
            "count": len(processed_meals),
            "meals": processed_meals
        }

    except requests.exceptions.RequestException as e:

        return {
            "success": False,
            "message": "Unable to connect to TheMealDB API.",
            "error": str(e)
        }
    

def format_meal(meal: dict) -> dict:
    """
    Converts a raw MealDB response into a clean, structured dictionary.
    """

    ingredients = []

    for i in range(1, 21):

        ingredient = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")

        if ingredient and ingredient.strip():

            ingredients.append({
                "ingredient": ingredient,
                "measure": measure.strip() if measure else ""
            })

    return {
        "Meal ID": meal.get("idMeal"),
        "Meal Name": meal.get("strMeal"),
        "Category": meal.get("strCategory"),
        "Cuisine": meal.get("strArea"),
        "Instructions": meal.get("strInstructions"),
        "Ingredients": ingredients,
        "YouTube": meal.get("strYoutube"),
        "Thumbnail": meal.get("strMealThumb")
    }


def format_meal_summary(meal: dict) -> dict:
    """
    Converts a filtered MealDB response into a simplified meal summary.
    """

    return {
        "Meal ID": meal.get("idMeal"),
        "Meal Name": meal.get("strMeal"),
        "Thumbnail": meal.get("strMealThumb")
    }

@mcp.tool()
def lookup_meal_by_id(meal_id: str) -> dict:
    """
    Lookup a meal using its MealDB ID.
    """

    try:

        response = requests.get(
            f"{BASE_URL}/lookup.php",
            params={
                "i": meal_id
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        meals = data.get("meals")

        if meals is None:

            return {
                "success": False,
                "message": f"No meal found with ID '{meal_id}'."
            }

        return {
            "success": True,
            "meal": format_meal(meals[0])
        }

    except requests.exceptions.RequestException as e:

        return {
            "success": False,
            "message": "Unable to connect to TheMealDB API.",
            "error": str(e)
        }


@mcp.tool()
def random_meal() -> dict:
    """
    Returns a random meal from TheMealDB.
    """

    try:

        response = requests.get(
            f"{BASE_URL}/random.php",
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        meals = data.get("meals")

        if meals is None:

            return {
                "success": False,
                "message": "Unable to fetch a random meal."
            }

        return {
            "success": True,
            "meal": format_meal(meals[0])
        }

    except requests.exceptions.RequestException as e:

        return {
            "success": False,
            "message": "Unable to connect to TheMealDB API.",
            "error": str(e)
        }

@mcp.tool()
def filter_by_category(category: str) -> dict:
    """
    Returns all meals belonging to a given category.
    """

    try:

        response = requests.get(
            f"{BASE_URL}/filter.php",
            params={
                "c": category
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        meals = data.get("meals")

        if meals is None:

            return {
                "success": False,
                "message": f"No meals found in category '{category}'."
            }

        processed_meals = []

        for meal in meals:

            processed_meals.append({
                "Meal ID": meal.get("idMeal"),
                "Meal Name": meal.get("strMeal"),
                "Thumbnail": meal.get("strMealThumb")
            })

        return {
            "success": True,
            "category": category,
            "count": len(processed_meals),
            "meals": processed_meals
        }

    except requests.exceptions.RequestException as e:

        return {
            "success": False,
            "message": "Unable to connect to TheMealDB API.",
            "error": str(e)
        }

@mcp.tool()
def filter_by_area(area: str) -> dict:
    """
    Returns all meals belonging to a given cuisine/area.
    """

    try:

        response = requests.get(
            f"{BASE_URL}/filter.php",
            params={
                "a": area
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        meals = data.get("meals")

        if meals is None:

            return {
                "success": False,
                "message": f"No meals found for area '{area}'."
            }

        processed_meals = [
            format_meal_summary(meal)
            for meal in meals
        ]

        return {
            "success": True,
            "area": area,
            "count": len(processed_meals),
            "meals": processed_meals
        }

    except requests.exceptions.RequestException as e:

        return {
            "success": False,
            "message": "Unable to connect to TheMealDB API.",
            "error": str(e)
        }
    

@mcp.resource("meal://categories")
def get_categories() -> dict:
    """
    Returns all available meal categories.
    """

    try:

        response = requests.get(
            f"{BASE_URL}/categories.php",
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        categories = data.get("categories", [])

        processed_categories = []

        for category in categories:

            processed_categories.append({
                "Category": category.get("strCategory"),
                "Description": category.get("strCategoryDescription"),
                "Thumbnail": category.get("strCategoryThumb")
            })

        return {
            "count": len(processed_categories),
            "categories": processed_categories
        }

    except requests.exceptions.RequestException as e:

        return {
            "error": str(e)
        }
    

@mcp.resource("meal://areas")
def get_areas() -> dict:
    """
    Returns all available meal areas/cuisines.
    """

    try:

        response = requests.get(
            f"{BASE_URL}/list.php",
            params={
                "a": "list"
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        meals = data.get("meals", [])

        areas = [
            meal.get("strArea")
            for meal in meals
        ]

        return {
            "count": len(areas),
            "areas": areas
        }

    except requests.exceptions.RequestException as e:

        return {
            "error": str(e)
        }
    
@mcp.prompt()
def cooking_guide(meal_name: str) -> str:
    """
    Generates a detailed prompt for preparing a particular meal.
    """

    return f"""
You are an experienced chef, culinary instructor, and food expert.

The user wants to prepare the dish: "{meal_name}".

Generate a complete cooking guide using the following structure:

1. Introduction
   - Briefly describe the dish.
   - Mention its country or cuisine of origin.

2. Ingredients
   - List all required ingredients with approximate quantities.

3. Required Kitchen Equipment
   - Mention the utensils and equipment needed.

4. Preparation
   - Describe all preparation steps before cooking.

5. Cooking Process
   - Explain the cooking process step by step.
   - Mention approximate cooking times.
   - Mention temperatures whenever applicable.

6. Tips
   - Mention common mistakes to avoid.
   - Suggest useful cooking tips.

7. Serving Suggestions
   - Recommend side dishes or beverages.
   - Suggest garnishing ideas.

8. Storage
   - Explain how to store leftovers.
   - Mention how long they remain fresh.

Write the response in clear, beginner-friendly language.
Use headings and bullet points wherever appropriate.
"""

if __name__ == "__main__":
    mcp.run(transport="streamable-http")