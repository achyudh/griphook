import json
import os
from collections import defaultdict

import javalang
from sklearn.model_selection import train_test_split
from unidiff import PatchSet

# List of repositories that will make up the dataset
repositories = ['apache/beam', 'apache/flink', 'apache/hadoop', 'apache/hbase', 'apache/hive', 'apache/kafka', 'apache/kylin']

label_encoding = {
    'Bug': '001',
    'Improvement': '010',
    'Sub-task': '100'
}

# Filename extension for code files
code_ext = '.java'


def is_ascii(string):
    return all(ord(c) < 128 for c in string)


def is_code_change(diff, code_ext):
    """
    Returns true if the diff contains changes from at least one code file
    :param diff: pull request diff
    :param code_ext: filename extension for code files
    :return:
    """
    patch = PatchSet(diff)
    for file in patch.added_files + patch.modified_files + patch.removed_files:
        if os.path.splitext(file.path)[1] == code_ext:
            return True
    return False


def get_tokens(code_changes):
    """
    Returns tokens from Java code snippets.
    NOTE: This requires well formed Java code as input and doesn't work on diffs
    :param code_changes: Java code encoded as a string
    :return: tokens extracted from the input code
    """
    file_tokens = list()

    try:
        file_tokens = [''.join(x.value.split()) for x in javalang.tokenizer.tokenize('\n'.join(code_changes))
                       if len(x.value.strip()) < 64 and is_ascii(x.value)]

    except:
        for line in code_changes:
            try:
                line_tokens = [''.join(x.value.split()) for x in javalang.tokenizer.tokenize(line)
                               if len(x.value.strip()) < 64 and is_ascii(x.value)]
                if line_tokens and line_tokens[0] != '*':
                    file_tokens.extend(line_tokens)
            except:
                pass

    if file_tokens:
        return ' '.join(file_tokens)

    return None


def split_dataset(dataset):
    """

    :param data_x:
    :param data_y:
    :return:
    """
    dataset_labels = [x[-1] for x in dataset]
    train_split, test_split = train_test_split(dataset, stratify=dataset_labels, test_size=0.20, random_state=42)

    train_labels = [x[-1] for x in train_split]
    train_split, dev_split = train_test_split(train_split, stratify=train_labels, test_size=0.25, random_state=42)

    print("Train, dev and test split sizes:", len(train_split), len(dev_split), len(test_split))
    return train_split, dev_split, test_split


# List containing labelled pull requests
labelled_commits = list()

label_counts = defaultdict(int)
for repo_name in repositories:
    with open(os.path.join(os.pardir, 'data', 'commits', repo_name, 'commit_metadata.json'), 'r') as metadata_file:
        metadata_dict = json.load(metadata_file)
    with open(os.path.join(os.pardir, 'data', 'commits', repo_name, 'commit_labels.json'), 'r') as label_file:
        label_dict = json.load(label_file)
    with open(os.path.join(os.pardir, 'data', 'commits', repo_name, 'commit_diffs.json'), 'r') as diff_file:
        diff_dict = json.load(diff_file)

    num_processed = 0
    for commit in metadata_dict:
        diff = diff_dict[commit['sha']]
        if is_code_change(diff, code_ext):
            commit_label = label_encoding.get(label_dict.get(commit['sha'], None), None)
            if commit_label:
                labelled_commits.append((commit, repo_name, diff, commit_label))
                label_counts[commit_label] += 1

        num_processed += 1
        if num_processed % 1000 == 0:
            print('Processed %d of %d commits in %s' %
                  (num_processed, len(metadata_dict), repo_name))

print("Number of labelled pull requests:", len(labelled_commits))
print("Dataset distribution:", label_counts)

# List containing all the dataset samples
dataset = list()

for commit, repo_name, diff, label in labelled_commits:
    diff_changes = list()
    patch = PatchSet(diff)

    for file in patch.added_files + patch.modified_files + patch.removed_files:
        if os.path.splitext(file.path)[1] == code_ext:
            file_changes = list()

            for hunk in file:
                for line in hunk:
                    file_changes.append(line.value)

            file_tokens = get_tokens(file_changes)
            if file_tokens:
                diff_changes.append(file_tokens)

    if diff_changes:
        dataset.append((repo_name,
                        commit['sha'],
                        json.dumps(diff_changes),
                        label))

train_split, dev_split, test_split = split_dataset(dataset)

with open(os.path.join(os.pardir, 'data', 'commits', 'apache', 'train.tsv'), 'w') as tsv_file:
    tsv_file.write('\n'.join('\t'.join(str(y) for y in x) for x in train_split))
with open(os.path.join(os.pardir, 'data', 'commits', 'apache', 'dev.tsv'), 'w') as tsv_file:
    tsv_file.write('\n'.join('\t'.join(str(y) for y in x) for x in dev_split))
with open(os.path.join(os.pardir, 'data', 'commits', 'apache', 'test.tsv'), 'w') as tsv_file:
    tsv_file.write('\n'.join('\t'.join(str(y) for y in x) for x in test_split))
