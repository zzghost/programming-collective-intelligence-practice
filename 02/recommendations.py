#-*- encoding:utf-8 -*-
# A dictionary of movie critics and their ratings of a small
# set of movies
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 
 'You, Me and Dupree': 3.5}, 
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0, 
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0}, 
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}
from math import sqrt


#Euclidean metric
def sim_distance(prefs, person1, person2):
    si = {}
    
    for x in prefs[person1]:
        if x in prefs[person2]:
            si[x] = 1

    if len(si) == 0:
        return 0

    sum_of_squares = sum([pow(prefs[person1][x]-prefs[person2][x], 2) for x in prefs[person1] if x in prefs[person2]])

    return 1/(sqrt(sum_of_squares) + 1)

#print sim_distance(critics, 'Lisa Rose', 'Jack Matthews')


#Pearson metric
def sim_pearson(prefs, person1, person2):
    si = {}

    for x in prefs[person1]:
        if x in prefs[person2]:
            si[x] = 1

    n = len(si)
    
    if n == 0:
        return 0

    sumX = sum([prefs[person1][x] for x in si])
    sumY = sum([prefs[person2][x] for x in si])

    sumX2 = sum([pow(prefs[person1][x], 2) for x in si])
    sumY2 = sum([pow(prefs[person2][x], 2) for x in si])

    sumXY = sum([prefs[person1][x]*prefs[person2][x] for x in si])

    num = sumXY - sumX * sumY / n
    den = sqrt((sumX2 - pow(sumX, 2) / n) * (sumY2 - pow(sumY, 2) / n))
    
    if den == 0:
        return 0
    
    return num / den

#print sim_pearson(critics, 'Lisa Rose', 'Gene Seymour')

#get top n person with similar appetite
def top_matches(prefs, person, n=5, similarity=sim_pearson):
    scores = [ (similarity(prefs, person, other), other) for other in prefs if other != person ]

    scores.sort()
    scores.reverse()
    return scores[:n]

#print top_matches(critics, 'Toby', n=3)

#recommend movies
def get_recommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}

    for other in prefs:
        if person == other:
            continue

        sim = similarity(prefs, person, other)

        if sim <= 0:
            continue
        
        for item in prefs[other]:
            
            if item not in prefs[person] or prefs[person][item] == 0:
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim

                simSums.setdefault(item, 0)
                simSums[item] += sim

    rankings = [(total / simSums[item], item) for item, total in totals.items()]

    rankings.sort()
    rankings.reverse()
    return rankings

#print get_recommendations(critics, 'Toby')


def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            result[item][person] = prefs[person][item]
    return result


# 计算物品间的相似程度
def calculateSimilarItems(prefs, n=10):
    result = {}
    itemPrefs = transformPrefs(prefs)

    c = 0

    for item in itemPrefs:
        c += 1
        if c % 100 == 0:
            print "%d / %d" % (c, len(itemPrefs))

        scores = top_matches(itemPrefs, item, n, sim_distance)
        result[item] = scores

    return result

# 基于物品间的相似程度，为每一位用户推荐物品
def getRecommendationItem(prefs, itemMatch, user):
    userRating = prefs[user]
    scores = {}
    totalSim = {}

    for (item, rating) in userRating.items():
        for (similarity, item2) in itemMatch[item]:
            if item2 in userRating:
                continue

            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating

            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    rankings = [(score / totalSim[item], item) for item,score in scores.items()]

    rankings.sort()
    rankings.reverse()
    return rankings


def loadMovieLens(path='./ml-20m'):
    movies = {}
    for line in open(path + '/movies.csv'):
        (id, title) = line.split(',')[:2]
        movies[id] = title

    prefs = {}
    for line in open(path + '/ratings.csv'):
        (user, movieid,rating,ts) = line.split(',')
        prefs.setdefault(user, {})
        prefs[user][movies[movieid]] = float(rating)

    return prefs
