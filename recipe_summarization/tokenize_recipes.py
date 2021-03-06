"""Tokenize recipes."""
import _pickle as pickle
from os import path
from nltk.tokenize import word_tokenize
from nltk import download
from tqdm import tqdm
import pandas as pd
import recipe_summarization.config as config
import recipe_summarization.prep_data as prep_data
from recipe_summarization.parse_ingredients import parse_ingredient_list


def tokenize_sentence(sentence):
    """Tokenize a sentence."""
    try:
        return ' '.join(list(filter(
            lambda x: x.lower() != "advertisement",
            word_tokenize(sentence))))
    except LookupError:
        print('Downloading NLTK data')
        download()
        return ' '.join(list(filter(
            lambda x: x.lower() != "advertisement",
            word_tokenize(sentence))))


def recipe_is_complete(r):
    """Return True if recipe is complete and False otherwise.

    Completeness is defined as the recipe containing a title and instructions.
    """
    if ('title' not in r) or ('instructions' not in r):
        return False
    if (r['title'] is None) or (r['instructions'] is None):
        return False
    return True


def tokenize_recipes(recipes):
    """Tokenise all recipes."""
    tokenized = []
    for r in tqdm(recipes.values()):
        if recipe_is_complete(r):
            ingredients = '; '.join(parse_ingredient_list(r['ingredients'])) + '; '
            tokenized.append((
                tokenize_sentence(r['title']),
                tokenize_sentence(ingredients) + tokenize_sentence(r['instructions'])))
    return tuple(map(list, zip(*tokenized)))


def pickle_recipes(recipes):
    """Pickle all recipe tokens to disk."""
    with open(path.join(config.path_data, 'tokens.pkl'), 'wb') as f:
        pickle.dump(recipes, f, 2)


def load_recipes():
    """Read pickled recipe tokens from disk."""
    with open(path.join(config.path_data, 'tokens.pkl'), 'rb') as f:
        recipes = pickle.load(f)
    return recipes


def get_tokenized(recipes):
    tokenized = []

    for r in tqdm(recipes.values()):
        if recipe_is_complete(r):
            ingredients = '; '.join(parse_ingredient_list(r['ingredients'])) + '; '
            tokenized.append((
                tokenize_sentence(r['title']),
                tokenize_sentence(ingredients) + tokenize_sentence(r['instructions'])))

    return tokenized


# Download punkt NLTK package (use d for download, punkt as identifier and q for quit.)

"""### Dataframe and Feature Creation"""


# Build dataframe (we will not use the recipe images or id's)
def make_dataframe(tokenized):
    colnames = ['title', 'ingredients', 'instructions']
    df = pd.DataFrame(columns=colnames)

    titles = []

    for recipe in tokenized:
        titles.append(recipe[0])

    df['title'] = titles

    ingredients_and_instructions = []

    for recipe in tokenized:
        ingredients_and_instructions.append(recipe[1])

    ingredients_and_instructions_lists = []

    for recipe in ingredients_and_instructions:
        list_of_strings = recipe.split(';')
        ingredients_and_instructions_lists.append(list_of_strings)

    instructions = []
    ingredients = []

    for recipe in ingredients_and_instructions_lists:
        instructions.append(recipe[-1])
        ingredients.append(recipe[0:-1])

    df['instructions'] = instructions
    df['ingredients'] = ingredients
    df['separator'] = '</>separator</>'

    return df
