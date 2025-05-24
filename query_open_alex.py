import string
from re import search
import requests
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import re
import time
import itertools
from collections import Counter


def read_input_file(filename: str):
    """
    Reads an input text file and returns it as a list.

    :param filename: path to the input file
    :return: file contents as a list
    """
    print(filename)
    file = open(filename, "r")
    input_data = file.read()
    input_list = input_data.split("\n")
    file.close()
    return input_list


def clean_input_list(input_list: list):
    """
    Cleans common errors in input list to get DOIs in format "https://doi.org/10.XXX/XXX" or "doi:10.XXXX/XXX",
    removing duplicates.

    :param input_list: list of DOIs
    :return: cleaned list of DOIs
    """
    cleaned_input_list = []
    for item in input_list:
        if item == '':
            continue
        elif re.search(r'^10\.', item):
            search_item = f"https://doi.org/{item}"
        elif re.search(r'^DOI:', item):
            # OpenAlex can handle searching DOIs listed as "doi:10.XXXX/XXXX", but not with upper case "DOI:"
            new_item = re.sub(r'DOI:', 'doi:', item, 1)
            search_item = new_item
        elif re.search(r'^doi.org', item):
            new_item = re.sub(r'doi.org/', '', item, 1)
            search_item = f"https://doi.org/{new_item}"
        else:
            search_item = item
        cleaned_input_list.append(search_item.strip())
        cleaned_input_list = list(set(cleaned_input_list))
    return cleaned_input_list


def query_open_alex(cleaned_input_list: list):
    """
    Queries OpenAlex for attributes of items with specific DOIs. See OpenAlex Work Object documentation for more
    details: https://docs.openalex.org/api-entities/works/work-object.

    :param cleaned_input_list: input list of DOIs in format "https://doi.org/10.XXX/XXX" or "doi:10.XXXX/XXX"
    :return: list of dictionaries with attributes for Work objects from returned queries in OpenAlex.
    """
    identifier_list = cleaned_input_list
    identifier_with_error_list = []

    authorships_dictionary = {}
    concepts_dictionary = {}
    keywords_dictionary = {}
    topics_dictionary = {}
    type_dictionary = {}
    publication_year_dictionary = {}
    primary_location_dictionary = {}

    for identifier in identifier_list:
        try:
            response = requests.get(f"https://api.openalex.org/works/{identifier}")
            result = response.json()
            authorships_dictionary[identifier] = result["authorships"]
            concepts_dictionary[identifier] = result["concepts"]
            keywords_dictionary[identifier] = result["keywords"]
            topics_dictionary[identifier] = result["topics"]
            type_dictionary[identifier] = result["type"]
            publication_year_dictionary[identifier] = result["publication_year"]
            primary_location_dictionary[identifier] = result["primary_location"]
            time.sleep(0.1)  # OpenAlex has a limit of max 10 requests per second.
        except Exception:
            identifier_with_error_list.append(identifier)
            continue

    # print(f"DOIs with errors: {len(identifier_with_error_list)}")
    # print(f"List of identifiers with errors: {identifier_with_error_list}")

    return (authorships_dictionary,
            concepts_dictionary,
            keywords_dictionary,
            topics_dictionary,
            type_dictionary,
            publication_year_dictionary,
            primary_location_dictionary,
            identifier_with_error_list)


def create_alphabet_tick_labels():
    alphabet = string.ascii_letters
    alphabet_tick_labels_list = []
    for i in range(len(alphabet)):
        alphabet_tick_labels_list.append(alphabet[i])
    for j in range(len(alphabet)):
        for k in range(len(alphabet)):
            alphabet_tick_labels_list.append(alphabet[j] + alphabet[k])
    return alphabet_tick_labels_list


def print_for_testing(authorships_dictionary,
                      concepts_dictionary,
                      keywords_dictionary,
                      topics_dictionary,
                      type_dictionary,
                      publication_year_dictionary,
                      primary_location_dictionary,
                      identifier_with_error_list):
    """
    Prints query output when needed for testing.

    :param authorships_dictionary: dictionary of authorships for DOIs from OpenAlex
    :param concepts_dictionary: dictionary of concepts for DOIs from OpenAlex
    :param keywords_dictionary: dictionary of keywords for DOIs from OpenAlex
    :param topics_dictionary: dictionary of topics for DOIs from OpenAlex
    :param type_dictionary: dictionary of item type for DOIs from OpenAlex
    :param publication_year_dictionary: dictionary of publication year for DOIs from OpenAlex
    :param primary_location_dictionary: dictionary of primary location for DOIs from OpenAlex
    :param identifier_with_error_list: dictionary of identifier with errors when querying OpenAlex
    :return: print
    """
    print(authorships_dictionary)
    print(concepts_dictionary)
    print(keywords_dictionary)
    print(topics_dictionary)
    print(type_dictionary)
    print(publication_year_dictionary)
    print(primary_location_dictionary)
    print(identifier_with_error_list)


def create_type_frequency_plot(type_dictionary: dict, primary_location_dictionary: dict):
    """
    Creates frequency plot for item types.

    :param type_dictionary: dictionary of item type for DOIs from OpenAlex
    :param primary_location_dictionary: dictionary of primary location for DOIs from OpenAlex. Used to separate
    conference proceedings from journal articles.
    :return: plot of item type frequency, pie chart of item type frequency, sorted frequency dictionary, and
    list of items with type None.
    """
    type_list = []
    type_none_list = []
    for doi_key, response_value in type_dictionary.items():
        if response_value is None:
            type_none_list.append(doi_key)
        elif response_value == 'article' and primary_location_dictionary[doi_key]['source'] is not None:
            if primary_location_dictionary[doi_key]['source']['type'] == 'journal':
                article_type = 'journal\narticle'
                type_list.append(article_type)
            elif primary_location_dictionary[doi_key]['source']['type'] == 'conference':
                article_type = 'conference\nproceeding'
                type_list.append(article_type)
        else:
            type_list.append(response_value)

    type_frequency = Counter(type_list)
    sorted_type_frequency = dict(sorted(type_frequency.items(), key=lambda x: (x[1], x[0]), reverse=True))

    fig_width = max(6.0, len(sorted_type_frequency) * 0.5)
    fig_height = fig_width

    fig1, ax1 = plt.subplots(figsize=(fig_width, fig_height), layout="constrained")
    ax1.bar(sorted_type_frequency.keys(), sorted_type_frequency.values())
    ax1.set_title("Frequency of Item Type(s)")
    plt.figtext(0.01,
                0.01,
                f'Excludes {len(type_none_list)} items with None value out of {len(type_dictionary)} total items',
                horizontalalignment='left',
                size='x-small')
    ax1.set_xlabel("Item Type")
    ax1.set_ylabel("Frequency")
    ax1.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    # ax1.tick_params(axis='x', labelrotation=45)
    ax1.bar_label(ax1.containers[0], label_type='edge', padding=0.5)
    # plt.show()

    label_list = []
    alphabet_list = []
    alphabet = create_alphabet_tick_labels()
    count = 0
    for key in sorted_type_frequency.keys():
        if key == 'journal\narticle':
            label = f"{alphabet[count]} journal article"
        elif key == 'conference\nproceeding':
            label = f"{alphabet[count]} conference proceeding"
        else:
            label = f"{alphabet[count]} {key}"
        label_list.append(label)
        alphabet_list.append(alphabet[count])
        count += 1

    fig2, ax2 = plt.subplots(figsize=(fig_width, fig_height), layout="constrained")
    ax2.set_title("Frequency of Item Type(s)")
    plt.figtext(0.01,
                0.01,
                f'Excludes {len(type_none_list)} items with None value out of {len(type_dictionary)} total items',
                horizontalalignment='left',
                size='x-small')
    ax2.pie(sorted_type_frequency.values(), labels=alphabet_list, autopct='%1.1f%%')
    plt.legend(labels=label_list, loc='upper right')
    # plt.show()

    return fig1, fig2, sorted_type_frequency, type_none_list


def create_year_frequency_plot(publication_year_dictionary: dict):
    """
    Creates frequency plot for publication years.
    :param publication_year_dictionary: dictionary of publication year for DOIs from OpenAlex
    :return: publication year frequency plot and sorted frequency dictionary
    """
    year_list = []
    year_none_list = []
    for doi_key, response_value in publication_year_dictionary.items():
        if response_value is None:
            year_none_list.append(doi_key)
        else:
            year_list.append(response_value)

    year_frequency = Counter(year_list)
    sorted_year_frequency = dict(sorted(year_frequency.items(), key=lambda x: (x[1], x[0]), reverse=True))

    fig_width = max(6.0, len(sorted_year_frequency) * 0.5)
    fig_height = fig_width * 0.6

    fig3, ax3 = plt.subplots(figsize=(fig_width, fig_height), layout="constrained")
    ax3.bar(sorted_year_frequency.keys(), sorted_year_frequency.values())
    ax3.set_title(f"Frequency of Publication Year")
    plt.figtext(0.01,
                0.01,
                f'Excludes {len(year_none_list)} items with None value '
                f'out of {len(publication_year_dictionary)} total items',
                horizontalalignment='left',
                size='x-small')
    ax3.set_xlabel("Publication Year")
    ax3.set_ylabel("Frequency")
    ax3.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax3.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax3.bar_label(ax3.containers[0], label_type='edge', padding=0.5)
    # plt.show()

    return fig3, sorted_year_frequency


def create_primary_location_frequency_plot(primary_location_dictionary: dict):
    """
    Creates frequency plot for primary locations (venues).

    :param primary_location_dictionary: dictionary of primary locations for DOIs from OpenAlex
    :return: plot of location frequency, sorted frequency dictionary, and list of items with primary location None.
    """
    primary_location_list = []
    primary_location_none_list = []
    for doi_key, response_value in primary_location_dictionary.items():
        if response_value["source"] is None:
            primary_location_none_list.append(doi_key)
        else:
            source = response_value["source"]["display_name"]
            primary_location_list.append(source)

    primary_location_frequency = Counter(primary_location_list)
    sorted_primary_location_frequency = dict(sorted(primary_location_frequency.items(),
                                                    key=lambda x: (x[1], x[0].lower())))

    fig_height = max(6.0, len(sorted_primary_location_frequency) * 0.462)
    fig_width = max(9.0, fig_height * 0.7)

    label_list = []
    alphabet_list = []
    alphabet = create_alphabet_tick_labels()
    count = len(sorted_primary_location_frequency) - 1
    for key in sorted_primary_location_frequency.keys():
        truncated_key = key[:67] + "..." if len(key) > 67 else key
        label = f"{alphabet[count]} {truncated_key}"
        label_list.append(label)
        alphabet_list.append(alphabet[count])
        count = count - 1

    fig6, ax6 = plt.subplots(figsize=(fig_width, fig_height), layout="constrained")
    ax6.barh(sorted_primary_location_frequency.keys(),
             sorted_primary_location_frequency.values(),
             color=plt.cm.viridis(np.linspace(0, 1, len(sorted_primary_location_frequency.values()))),
             label=label_list,
             tick_label=alphabet_list)
    ax6.set_title("Frequency of Publishers")
    ax6.set_ylabel("Publisher")
    ax6.set_xlabel("Frequency")
    plt.figtext(0.01,
                0.01,
                f'Excludes {len(primary_location_none_list)} items with None value '
                f'out of {len(primary_location_dictionary)} total items',
                horizontalalignment='left',
                size='x-small')
    y_max = len(sorted_primary_location_frequency)
    plt.ylim(-1, y_max)
    ax6.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax6.legend(reverse=True, loc='lower right', framealpha=1, fontsize='x-small')
    ax6.bar_label(ax6.containers[0], label_type='edge', padding=0.5)
    # plt.show()

    return fig6, sorted_primary_location_frequency, primary_location_none_list


def create_keyword_frequency_plot(keywords_dictionary: dict):
    """
    Creates frequency plot for keywords.

    :param keywords_dictionary: dictionary of keywords for DOIs from OpenAlex
    :return: plot of keyword frequency, sorted frequency dictionary, and list of items with keyword None.
    """
    keyword_list = []
    keyword_none_list = []
    for doi_key, response_value in keywords_dictionary.items():
        if response_value is None:
            keyword_none_list.append(doi_key)
        else:
            for sub_item in response_value:
                keyword_list.append(sub_item["display_name"])

    keyword_frequency = Counter(keyword_list)
    sorted_keyword_frequency = dict(sorted(keyword_frequency.items(), key=lambda x: (x[1], x[0])))

    fig_height = max(6.0, len(sorted_keyword_frequency) * 0.25)
    fig_width = max(4.0, fig_height * 1)

    fig4, ax4 = plt.subplots(figsize=(fig_width, fig_height), layout="constrained")
    ax4.barh(list(sorted_keyword_frequency.keys())[-25:], list(sorted_keyword_frequency.values())[-25:])
    ax4.set_title("Most Frequent of Keywords\n")
    plt.figtext(0.01,
                0.01,
                f'Excludes {len(keyword_none_list)} items with None value '
                f'out of {len(keywords_dictionary)} total items',
                horizontalalignment='left',
                size='x-small')
    ax4.set_ylabel("Keyword")
    ax4.set_xlabel("Frequency")
    ax4.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    y_max = len(sorted_keyword_frequency)
    plt.ylim(-1, 25)
    ax4.bar_label(ax4.containers[0], label_type='edge', padding=0.5)
    # plt.show()
    return fig4, sorted_keyword_frequency, keyword_none_list


def create_concepts_frequency_plot(concepts_dictionary: dict):
    """
    Creates frequency plot for most and least frequent concepts.

    :param concepts_dictionary: dictionary of concepts for DOIs from OpenAlex
    :return: plot of concept frequency, sorted frequency dictionary, and list of items with concept None.
    """
    concepts_list = []
    concepts_none_list = []
    for doi_key, response_value in concepts_dictionary.items():
        if response_value is None:
            concepts_none_list.append(doi_key)
        else:
            for sub_item in response_value:
                concepts_list.append(sub_item["display_name"])

    concepts_frequency = Counter(concepts_list)
    sorted_concepts_frequency = dict(sorted(concepts_frequency.items(), key=lambda x: (x[1], x[0])))

    fig_width = 6.0
    fig_height = 5.0

    fig5, ax1 = plt.subplots(figsize=(fig_width, fig_height), layout="tight")
    plt.figtext(0.01,
                0.01,
                f'Excludes {len(concepts_none_list)} items with None value '
                f'out of {len(concepts_dictionary)} total items',
                horizontalalignment='left',
                size='x-small')
    ax1.barh(list(sorted_concepts_frequency.keys())[-20:], list(sorted_concepts_frequency.values())[-20:])
    ax1.set_title("Twenty Most Frequent Concepts\n(with alphabetical ordering)")
    ax1.set_ylabel("Concept")
    ax1.set_xlabel("Frequency")
    ax1.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax1.tick_params(axis='x', labelbottom=True)
    ax1.tick_params(axis='y', labelsize='x-small')
    ax1.set_ylim(-1, 20)
    ax1.bar_label(ax1.containers[0], label_type='edge', padding=0.5)
    # plt.show()

    return fig5, sorted_concepts_frequency, concepts_none_list


def main():
    print("Reading input list...")
    input_list = read_input_file(filename="data/zotero-export.txt")
    print("Input list read.")
    print("Cleaning input list...")
    cleaned_input_list = clean_input_list(input_list)
    print("Input list cleaned.")
    print("Querying OpenAlex...")
    authorships_dictionary, concepts_dictionary, keywords_dictionary, topics_dictionary, type_dictionary, \
        publication_year_dictionary, primary_location_dictionary, identifier_with_error_list \
        = query_open_alex(cleaned_input_list)
    print("OpenAlex queried.")
    if len(identifier_with_error_list) != 1:
        print(f"{len(identifier_with_error_list)} DOIs with errors: {identifier_with_error_list}")
    else:
        print(f"{len(identifier_with_error_list)} DOI with errors: {identifier_with_error_list}")

    print("Creating visualizations ...")
    type_frequency_plot, type_frequency_pie_chart = \
        create_type_frequency_plot(type_dictionary, primary_location_dictionary)[0:2]
    year_frequency_plot = create_year_frequency_plot(publication_year_dictionary)[0]
    keyword_frequency_plot = create_keyword_frequency_plot(keywords_dictionary)[0]
    concepts_frequency_plot = create_concepts_frequency_plot(concepts_dictionary)[0]
    primary_location_frequency_plot = create_primary_location_frequency_plot(primary_location_dictionary)[0]
    print("Visualizations created.")

    type_frequency_plot.show()
    type_frequency_pie_chart.show()
    year_frequency_plot.show()
    keyword_frequency_plot.show()
    concepts_frequency_plot.show()
    primary_location_frequency_plot.show()


if __name__ == '__main__':
    main()
