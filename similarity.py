def similarity_percentage(word1, word2):
    # Calcul de la distance de Levenshtein
    distance = levenshtein_distance(word1, word2)

    # Calcul du pourcentage de similitude
    max_length = max(len(word1), len(word2))
    similarity = max_length - distance

    return similarity


def levenshtein_distance(word1, word2):
    # Initialisation de la matrice
    matrix = [[0] * (len(word2) + 1) for _ in range(len(word1) + 1)]

    # Remplissage de la première ligne et de la première colonne
    for i in range(len(word1) + 1):
        matrix[i][0] = i
    for j in range(len(word2) + 1):
        matrix[0][j] = j

    # Calcul de la distance de Levenshtein
    for i in range(1, len(word1) + 1):
        for j in range(1, len(word2) + 1):
            if word1[i - 1] == word2[j - 1]:
                cost = 0
            else:
                cost = 1
            matrix[i][j] = min(matrix[i - 1][j] + 1,  # Suppression
                               matrix[i][j - 1] + 1,  # Insertion
                               matrix[i - 1][j - 1] + cost)  # Substitution

    return matrix[len(word1)][len(word2)]


# Exemple d'utilisation
word1 = "STRUCTURE DE DONNÉES"
word2 = "STRUCTURE DES DONNÉES"
percentage = similarity_percentage(word1, word2)
print(f"Pourcentage de similitude entre '{word1}' et '{word2}': {percentage}")
