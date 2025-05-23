from shiny import App, render, ui, reactive
from query_open_alex import *


def server(input, output, session):
    @reactive.calc
    def app_read_input_file():
        if (input.type() == "Text") & (bool(input.user_file())):
            file = input.user_file()
            input_list = read_input_file(file[0]["datapath"])
            cleaned_input_list = clean_input_list(input_list)
            return {'clean_input_list': cleaned_input_list}
        else:
            return {'clean_input_list': 'Input file is invalid.'}

    @output
    @render.text
    def app_clean_input_list():
        return f"{app_read_input_file()['clean_input_list']}"

    @reactive.calc
    @reactive.event(input.query_button)
    def app_query():
        p = ui.Progress()
        p.set(message="Computing, please wait...")
        query_input = app_read_input_file()['clean_input_list']

        authorships_dictionary, \
            concepts_dictionary, \
            keywords_dictionary, \
            topics_dictionary, \
            type_dictionary, \
            publication_year_dictionary, \
            primary_location_dictionary, \
            identifier_with_error_list = query_open_alex(query_input)
        p.close()

        return {'authorships_dictionary': authorships_dictionary,
                'concepts_dictionary': concepts_dictionary,
                'keywords_dictionary': keywords_dictionary,
                'topics_dictionary': topics_dictionary,
                'type_dictionary': type_dictionary,
                'publication_year_dictionary': publication_year_dictionary,
                'primary_location_dictionary': primary_location_dictionary,
                'identifier_with_error_list': identifier_with_error_list}

    @output
    @render.text
    def app_query_errors():
        if len(app_query()['identifier_with_error_list']) != 1:
            return f"{len(app_query()['identifier_with_error_list'])} DOIs with errors: \n \
                {app_query()['identifier_with_error_list']}"
        else:
            return f"{len(app_query()['identifier_with_error_list'])} DOI with errors: \n \
                {app_query()['identifier_with_error_list']}"

    @output
    @render.text
    def app_query_result():
        return (f"Authorships: {app_query()['authorships_dictionary']} \n"
                f"Concepts: {app_query()['concepts_dictionary']} \n"
                f"Keywords: {app_query()['keywords_dictionary']} \n"
                f"Topics: {app_query()['topics_dictionary']} \n"
                f"Type: {app_query()['type_dictionary']} \n"
                f"Publication Year: {app_query()['publication_year_dictionary']} \n"
                f"Primary Location: {app_query()['primary_location_dictionary']} \n")

    @output
    @render.plot
    def type_frequency():
        fig1, fig2, sorted_type_frequency, type_none_list = \
            create_type_frequency_plot(app_query()['type_dictionary'], app_query()['primary_location_dictionary'])
        return fig1

    @output
    @render.plot
    def type_frequency_pie():
        fig1, fig2, sorted_type_frequency, type_none_list = \
            create_type_frequency_plot(app_query()['type_dictionary'], app_query()['primary_location_dictionary'])
        return fig2

    @output
    @render.plot
    def year_frequency():
        fig3, sorted_year_frequency = create_year_frequency_plot(app_query()['publication_year_dictionary'])
        return fig3

    @output
    @render.plot
    def keyword_frequency():
        fig4, sorted_keyword_frequency, keyword_none_list = create_keyword_frequency_plot(
            app_query()['keywords_dictionary'])
        return fig4

    @output
    @render.plot
    def concepts_frequency():
        fig5, sorted_concepts_frequency, concepts_none_list = create_concepts_frequency_plot(
            app_query()['concepts_dictionary'])
        return fig5

    @output
    @render.plot
    def primary_location_frequency():
        fig6, sorted_primary_location_frequency, primary_location_none_list = \
            create_primary_location_frequency_plot(app_query()['primary_location_dictionary'])
        return fig6