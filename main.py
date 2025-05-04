import pandas as pd
import numpy as np
letters_used = []
for i in range(4):
    letters_used.append([l for l in input(f"Enter letters used on side {i+1}:\n").lower() if l.isalpha()])
def validate_letter(letter, i):
    for j in range(len(letters_used)):
        if not i == j:
            if letter in letters_used[j]:
                return True, j
    return False, -1

def valid_word(word):
    try:
        if len(word) < 4:
            return False
        i = -1
        for l in word:
            res, i = validate_letter(l, i)
            if res == False:
                return False
        return True
    except:
        return False

def longest_words(df, num_of_words=5):
    words = []
    for i in range(num_of_words):
        values = df.values.flatten()
        word = max([word for word in values if pd.notna(word)], key=len)
        df = df.replace(word, pd.NA)  # Replace the found word with NaN
        words.append(word)
    return words

def valid_words_in_df():
    # Process the file in chunks
    chunk_size = 10000 
    df = pd.DataFrame(columns=[0])
    for chunk in pd.read_csv('https://people.sc.fsu.edu/~jburkardt/datasets/words/anagram_dictionary.txt', chunksize=chunk_size, header=None):
        df = pd.concat([df, chunk[chunk[0].apply(valid_word)]])

    # Sort by the first letter
    df['first_letter'] = df[0].str[0]  
    df = df.sort_values(by='first_letter').reset_index(drop=True).rename(columns={0: 'word'})
    df['group_index'] = df.groupby('first_letter').cumcount()
    df_pivoted = df.pivot(index="group_index", columns='first_letter', values="word")
    return df_pivoted

def remove_words(df, words):
    # Remove the word from the DataFrame
    for word in words:
        df = df.replace(word, pd.NA)  # Replace the found word with NaN
    return df

def get_first_word(df, num_of_words=5):
    longest_words_list = longest_words(df, num_of_words=num_of_words)
    [print(f"{i}: {word}") for i, word in enumerate(longest_words_list)]
    i = int(input("Which word did letter boxed recognize? (If none were recognized type -1)\nIndex: "))
    if i == -1:
        df = remove_words(df, longest_words_list)
        return get_first_word(df)
    return longest_words_list[i]

def find_best_word(df, col, letters_needed):
    tot_max = 0
    best_word = None
    for word in df[col]:
        if pd.notna(word):
            word_letters = np.array([l for l in word])
            tot = np.size(np.intersect1d(letters_needed, word_letters))
            if tot > tot_max:
                tot_max = tot
                best_word = word
    if input(f"Best word is {best_word} Do you want to keep it? (y/n)\n") == "y":
        return best_word, tot
    else:
        return find_best_word(remove_words(df, [best_word]), col, letters_needed)
##__MAIN__##
# Load the data and find the longest words
df = valid_words_in_df()
letters = np.array(letters_used).flatten()
letters_needed = letters.copy()
words = [get_first_word(df)]
while letters_needed.size > 0:
    words.append(find_best_word(df, words[-1][-1], letters_needed)[0])
    letters_needed = np.setxor1d(letters, np.array([l for word in words for l in word]))
print("Solved!")