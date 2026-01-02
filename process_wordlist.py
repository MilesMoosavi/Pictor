import os

# Paths
propernouns_file = 'pictor/wordlists/drawit_wordlist_propernouns.txt'
wordlist_file = 'pictor/wordlists/drawit_wordlist.txt'

# Read propernouns and create lowercase to capitalized mapping
propernouns = {}
with open(propernouns_file, 'r', encoding='utf-8') as f:
    for line in f:
        word = line.strip()
        if word:
            propernouns[word.lower()] = word

# Read wordlist, replace lowercase with capitalized if exists, collect all lines
lines = []
with open(wordlist_file, 'r', encoding='utf-8') as f:
    for line in f:
        word = line.strip()
        if word:
            lower = word.lower()
            if lower in propernouns:
                lines.append(propernouns[lower])
            else:
                lines.append(word)

# Sort the lines
lines.sort()

# Deduplicate
unique_lines = sorted(set(lines))

# Write back to wordlist_file
with open(wordlist_file, 'w', encoding='utf-8') as f:
    for line in unique_lines:
        f.write(line + '\n')
with open(wordlist_file, 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(line + '\n')