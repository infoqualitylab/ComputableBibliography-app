from shiny import App, render, ui, reactive, req
from query_open_alex import *
# import shinyswatch


def ui_card(title, *args):
    return (
        ui.div(
            {"class": "card mb-4"},
            ui.div(title, class_="card-header"),
            ui.div({"class": "card-body"}, *args),
        ),
    )


app_ui = ui.page_fluid(
    ui.panel_title(ui.h1("Computable Bibliography"), window_title="Computable Bibliography"),

    ui.h3("Created by the Information Quality Lab"),
    ui.div(
    ui.markdown(
        """
        ### What this application does:
        This application queries [OpenAlex](https://openalex.org/) for information about submitted publications, 
        then returns text versions of the information retrieved as well as visualizations comparing the submitted publications 
        in aggregate. An example use case can be seen below.
        
        ### How to use this application:
        ##### 1. Create a text file (.txt file) of [Digital Object Identifiers (DOIs)](https://en.wikipedia.org/wiki/Digital_object_identifier) for all publications you would like to compare.
        In a citation manager such as [Zotero](https://www.zotero.org/), you can create this by:
        1. exporting a library or collection to .csv format
        2. copying the DOI column of the .csv file
        3. pasting the DOI column into a text editor such as [Notepad](https://apps.microsoft.com/detail/9msmlrh6lzf3?hl=en-us&gl=US) 
        (Windows) or [TextEdit](https://support.apple.com/guide/textedit/welcome/mac) (Mac)
        4. saving the resulting file
        
        You can also manually copy and paste DOIs into a text file using text editor such as [Notepad](https://apps.microsoft.com/detail/9msmlrh6lzf3?hl=en-us&gl=US) 
        (Windows) or [TextEdit](https://support.apple.com/guide/textedit/welcome/mac) (Mac). 
        
        PLEASE NOTE: 
        - DOIs can be in the following formats:
          - https://doi.org/10.XXX/XXXX or
          - doi:10.XXXX/XXXX or
          - 10.XXXX/XXXX
        - The app will ignore blank/empty lines
        
        ##### 2. On the webpage, click "Browse..." and select the text file you created. 
        Functionality for files other than text/.txt is forthcoming.
        
        ##### 3. Review information listed in "Input data". This will show cleaned versions of the DOIs you submitted
        
        ##### 4. Hit the button to query OpenAlex
        This will query the OpenAlex API for each DOI you submit. Large requests can take some time.
        
        ##### 5. View results
        You will be able to copy identifiers that had errors when querying OpenAlex and python dictionaries used to create the 
        visualizations shown. Code to create the visualizations is stored on the [Information Quality Lab GitHub](https://github.com/infoqualitylab/ComputableBibliography-app)
        """
        )),

    ui.panel_well(
        ui.h2("Upload a DOI file:"),

        ui.input_file("user_file", "Choose a file to upload:", multiple=False),
        ui.input_radio_buttons("type", "Type:", ["Text", "Other"]),
    ),

    ui.panel_well(
        ui.h2("Input data"),
        ui.output_text_verbatim("app_clean_input_list"),
        ui.h2("Query OpenAlex"),
        ui.input_action_button("query_button", "Query OpenAlex")
    ),

    ui.panel_well(
        ui.h2("Query result dictionaries"),

        ui_card(
            ui.h3("Identifiers with errors:"),
            ui.output_text_verbatim("app_query_errors")
        ),

        ui_card(
            ui.h3("Results for identifiers without errors:"),
            ui.output_text_verbatim("app_query_result")
        ),
    ),

    ui.panel_well(
        ui.h2("Plots"),
        ui.output_plot("type_frequency", height='90vh', width='90vw'),
        ui.output_plot("type_frequency_pie", height='90vh', width='90vw'),
        ui.output_plot("year_frequency", height='90vh', width='90vw'),
        ui.output_plot("keyword_frequency", height='90vh', width='90vw'),
        ui.output_plot("concepts_frequency", height='90vh', width='90vw'),
        ui.output_plot("primary_location_frequency", height='90vh', width='90vw')
    )

    # Available themes:
    #  cerulean, cosmo, cyborg, darkly, flatly, journal, litera, lumen, lux,
    #  materia, minty, morph, pulse, quartz, sandstone, simplex, sketchy, slate,
    #  solar, spacelab, superhero, united, vapor, yeti, zephyr
    # # theme=shinyswatch.theme.pulse()
)


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
        fig4, sorted_keyword_frequency, keyword_none_list = create_keyword_frequency_plot(app_query()['keywords_dictionary'])
        return fig4

    @output
    @render.plot
    def concepts_frequency():
        fig5, sorted_concepts_frequency, concepts_none_list = create_concepts_frequency_plot(app_query()['concepts_dictionary'])
        return fig5

    @output
    @render.plot
    def primary_location_frequency():
        fig6, sorted_primary_location_frequency, primary_location_none_list = \
            create_primary_location_frequency_plot(app_query()['primary_location_dictionary'])
        return fig6

app = App(app_ui, server, debug=False)
