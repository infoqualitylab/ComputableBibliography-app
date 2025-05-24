import os

from shiny import App, render, ui, reactive
from server import *


def ui_card(title, *args):
    return (
        ui.div(
            {"class": "card mb-4"},
            ui.div(title, class_="card-header"),
            ui.div({"class": "card-body"}, *args),
        ),
    )


home_page = ui.page_fluid(
    ui.markdown(
        """
        ### What this application does:
          This application queries [OpenAlex](https://openalex.org/) for information about publications submitted in a
          DOI file. It then returns text versions of the information retrieved and visualizations comparing the 
          publications in aggregate. Specifically it uses the OpenAlex 
          [Work object](https://docs.openalex.org/api-entities/works/work-object),
          parsing JSON files for each publication queried.

          See the "How to use this app" and "Example usage" pages for more information.
          
        #### A note on usage and limitations:
          Some errors in OpenAlex metadata have been observed. If OpenAlex metadata is inaccurate or missing, the 
          visualizations and text returned by the Computable Bibliography will also be inaccurate. Further, only 
          publications with a valid DOI generate results, which excludes many types of academic works. 
        """
    ),

    ui.panel_well(
        ui.h3("Upload a DOI file:"),

        ui.input_file("user_file", "Choose a file to upload:", multiple=False),
        ui.input_radio_buttons("type", "Type:", ["Text", "Other"]),
    ),

    ui.panel_well(
        ui.h3("Input data"),
        ui.output_text_verbatim("app_clean_input_list"),
        ui.h3("Query OpenAlex"),
        ui.input_action_button("query_button", "Query OpenAlex")
    ),

    ui.panel_well(
        ui.h3("Query result dictionaries"),

        ui_card(
            ui.h4("Identifiers with errors:"),
            ui.output_text_verbatim("app_query_errors")
        ),

        ui_card(
            ui.h4("Results for identifiers without errors:"),
            ui.output_text_verbatim("app_query_result")
        ),
    ),

    ui.panel_well(
        ui.h3("Plots"),
        ui.output_plot("type_frequency", height='90vh', width='90vw'),
        ui.output_plot("type_frequency_pie", height='90vh', width='90vw'),
        ui.output_plot("year_frequency", height='90vh', width='90vw'),
        ui.output_plot("primary_location_frequency", height='90vh', width='90vw'),
        ui.output_plot("keyword_frequency", height='90vh', width='90vw'),
        ui.output_plot("concepts_frequency", height='90vh', width='90vw'),
    )
)

with open('how_to_instructions.md', 'r') as file:
    how_to_markdown_file = file.read()
how_to_page = ui.markdown(how_to_markdown_file)

with open('example_page.md', 'r') as file:
    example_markdown_file = file.read()
example_page = ui.page_fluid(
    ui.markdown(example_markdown_file)
)

app_ui = ui.page_navbar(
    ui.nav_spacer(),
    ui.nav_panel("Home", home_page),
    ui.nav_panel("How to use this app", how_to_page),
    ui.nav_panel("Example usage", example_page),
    title=ui.TagList(
            ui.h1("Computable Bibliography"),
            ui.a(f"Created by the Information Quality Lab", href="https://infoqualitylab.org/")
        ),
    window_title="Computable Bibliography"
)

app = App(ui=app_ui, server=server, debug=False)
