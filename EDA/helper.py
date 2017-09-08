import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# budget type
def budget_type(budget):
    if budget <= 396000:
        return 'micro'
    elif budget <= 2100000:
        return 'low'
    else:
        return 'normal'

# list of names
def actors_list(movies):
    """Returns a dataframe containing all the actors present in the dataset
    looking at the three actor columns and their respective facebook likes.
    """
    actor1 = movies[['actor_1_name', 'actor_1_facebook_likes']].groupby('actor_1_name').max().reset_index().rename(columns={'actor_1_name': 'actor', 'actor_1_facebook_likes':'facebook_likes'})
    actor2 = movies[['actor_2_name', 'actor_2_facebook_likes']].groupby('actor_2_name').max().reset_index().rename(columns={'actor_2_name': 'actor', 'actor_2_facebook_likes':'facebook_likes'})
    actor3 = movies[['actor_3_name', 'actor_3_facebook_likes']].groupby('actor_3_name').max().reset_index().rename(columns={'actor_3_name': 'actor', 'actor_3_facebook_likes':'facebook_likes'})
    return actor1.append(actor2).append(actor3).groupby('actor').max()

def directors_list(movies):
    """Returns a dataframe containing all the directors present in the dataset and their respective facebook likes.
    """
    directors = movies[['director_name', 'director_facebook_likes']].groupby('director_name').max().reset_index().rename(columns={'director_name': 'director', 'director_facebook_likes':'facebook_likes'})
    return directors.set_index('director')

# analysis by actor
def movies_by_actor(movies, actors):
    """Returns a dataframe containing all the combination of actors and movies
    present in the dataset, the movies gross revenue, budget and ROI and
    the actor's importance in the movie (1st, 2nd or 3rd actor) and facebook likes.
    """
    movies_by_actor = pd.melt(movies[['movie_title', 'actor_1_name', 'actor_2_name', 'actor_3_name', 'gross', 'budget', 'ROI', 'log_ROI']],
                            id_vars=['movie_title', 'gross', 'budget', 'ROI', 'log_ROI'],
                            value_vars=['actor_1_name', 'actor_2_name', 'actor_3_name'],
                            var_name='actor_importance', value_name='actor')
    movies_by_actor.actor_importance = movies_by_actor.actor_importance.map({'actor_1_name':1, 'actor_2_name':2, 'actor_3_name':3})
    movies_by_actor = movies_by_actor.merge(actors, left_on='actor', right_index=True, how='inner')
    return movies_by_actor

def actors_ROI(movies_by_actor):
    """Returns a dataframe containing actors' total gross revenue, budget and ROI
    calculated from all the movies in which they acted.
    It also includes the actor's facebook likes and number of movies.
    It doesn't take into account the actors' importance in the movie.
    """
    actors_ROI = movies_by_actor.groupby('actor').apply(
        lambda x: pd.Series({
                    'ROI': (x.gross.sum() - x.budget.sum()) / (x.budget.sum()) if x.budget.sum() != 0 else np.NaN,
                    'facebook_likes': x.facebook_likes.max(),
                    'total_gross': x.gross.sum(),
                    'total_budget': x.budget.sum(),
                    'number_movies': len(x)
                })
        ).dropna()
    return actors_ROI

# analysis by genre
def movies_by_genre(movies):
    """Returns a dataframe containing all the combination of genres and movies
    present in the dataset, the movies gross revenue, budget and ROI.
    """
    movies_by_genre = pd.melt(movies[['movie_title', 'title_year', 'Biography', 'Adventure', 'Family', 'War', 'Sci-Fi', 'Mystery', 'Romance', 'Crime', 'Action', 'Animation', 'Sport', 'Drama', 'Documentary', 'Music', 'History', 'Fantasy', 'Film-Noir', 'Thriller', 'Horror', 'Short', 'Comedy', 'Western', 'News', 'Musical', 'gross', 'budget', 'ROI', 'log_ROI']],
                        id_vars=['movie_title', 'title_year', 'gross', 'budget', 'ROI', 'log_ROI'],
                        value_vars=['Biography', 'Adventure', 'Family', 'War', 'Sci-Fi', 'Mystery', 'Romance', 'Crime', 'Action', 'Animation', 'Sport', 'Drama', 'Documentary', 'Music', 'History', 'Fantasy', 'Film-Noir', 'Thriller', 'Horror', 'Short', 'Comedy', 'Western', 'News', 'Musical'],
                        var_name='genre', value_name='flag')
    movies_by_genre = movies_by_genre[movies_by_genre.flag==1].drop('flag', axis=1)
    return movies_by_genre

def genres_ROI(movies_by_genre):
    """Returns a dataframe containing genres' total gross revenue, budget and ROI
    calculated from all the movies for the genre applies.
    """
    genres_ROI = movies_by_genre.groupby('genre').apply(
        lambda x: pd.Series({
                    'ROI': (x.gross.sum() - x.budget.sum()) / (x.budget.sum()) if x.budget.sum() != 0 else np.NaN,
                    'total_gross': x.gross.sum(),
                    'total_budget': x.budget.sum(),
                    'number_movies': len(x)
                })
        ).dropna()
    return genres_ROI

def top_movies_by_genre(movies_by_genre, genre, minimum_ROI, n):
    return movies_by_genre[(movies_by_genre.genre==genre) & (movies_by_genre.ROI>=minimum_ROI)].sort_values(by='ROI', ascending=False).head(n)

# analysis by director
def movies_by_director(movies, directors):
    """Returns a dataframe containing all the combination of directors and movies
    present in the dataset, the movies gross revenue, budget and ROI and
    the director's facebook likes.
    """
    movies_by_director = movies[['movie_title', 'director_name', 'gross', 'budget', 'ROI', 'log_ROI']]
    movies_by_director = movies_by_director.merge(directors, left_on='director_name', right_index=True, how='inner')
    return movies_by_director

def directors_ROI(movies_by_director):
    """Returns a dataframe containing directors' total gross revenue, budget and ROI
    calculated from all the movies they directed.
    It also includes the director's facebook likes and number of movies.
    """
    directors_ROI = movies_by_director.groupby('director_name').apply(
        lambda x: pd.Series({
                    'ROI': (x.gross.sum() - x.budget.sum()) / (x.budget.sum()) if x.budget.sum() != 0 else np.NaN,
                    'facebook_likes': x.facebook_likes.max(),
                    'total_gross': x.gross.sum(),
                    'total_budget': x.budget.sum(),
                    'number_movies': len(x)
                })
        ).dropna()
    return directors_ROI

# analysis by year and genre
def genre_year(movies_by_genre, genre_list):
    genre_year = movies_by_genre[movies_by_genre.genre.isin(genre_list)].groupby(['genre', 'title_year']).apply(
    lambda x: pd.Series({
                'ROI': (x.gross.sum() - x.budget.sum()) / (x.budget.sum()) if x.budget.sum() != 0 else np.NaN,
                'total_gross': x.gross.sum(),
                'total_budget': x.budget.sum(),
                'number_movies': len(x)
            })).reset_index()
    return genre_year

def genre_year_plotting(movies_by_genre, genre_list, year_from=1980):
    df = pd.pivot_table(genre_year(movies_by_genre, genre_list), values=['number_movies', 'ROI'], index='title_year', columns='genre', aggfunc='sum')
    secondary_y = []
    for el in genre_list:
        secondary_y.append(('ROI', el))
    df[df.index >= year_from].plot(figsize=(16, 8), legend=True, secondary_y=secondary_y)
