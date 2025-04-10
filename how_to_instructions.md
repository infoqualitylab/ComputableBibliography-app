# How to use the Computable Bibliography
### What this application does:
This application queries [OpenAlex](https://openalex.org/) for information about publications submitted in a DOI file, 
which is described below. It then returns text versions of the information retrieved and visualizations comparing the publications 
in aggregate. Specifically it uses the OpenAlex [Work object](https://docs.openalex.org/api-entities/works/work-object),
parsing JSON files for each publication queried.

<hr style="border:2px solid gray">

### How to use this application:

##### 1. Create a DOI file, which is a text file (.txt file) of [Digital Object Identifiers (DOIs)](https://en.wikipedia.org/wiki/Digital_object_identifier) for all publications you would like to compare.

*Formatting guidelines:*
  - One DOI per line in the text (.txt) file.
  - DOIs can be in any of the following formats:
    - https://doi.org/10.XXX/XXXX
    - doi:10.XXXX/XXXX
    - 10.XXXX/XXXX
  - The app will ignore blank/empty lines. 

In a citation manager such as [Zotero](https://www.zotero.org/), you can create a DOI file by:
1. Exporting a library or collection to .csv format.
2. Copying the DOI column of the .csv file.
3. Pasting the DOI column into a text editor such as [Notepad](https://apps.microsoft.com/detail/9msmlrh6lzf3?hl=en-us&gl=US) 
(Windows) or [TextEdit](https://support.apple.com/guide/textedit/welcome/mac) (Mac).
4. Saving the resulting file. Blank lines do not need to be removed.
  
You can also manually copy and paste DOIs into a text file using text editor such as [Notepad](https://apps.microsoft.com/detail/9msmlrh6lzf3?hl=en-us&gl=US) 
(Windows) or [TextEdit](https://support.apple.com/guide/textedit/welcome/mac) (Mac). 

---

##### 2. On the webpage, click "Browse..." and select the text file you created.
Functionality for files other than text (.txt) is forthcoming.

---

##### 3. Review information listed under "Input data". 
This will show cleaned and standardized versions of the DOIs you submitted

---

##### 4. Hit the button "Query OpenAlex"
This will query the OpenAlex API for each DOI you submit. Large requests can take some time.

---
  
##### 5. View results
You will be able to copy the identifiers that had errors when querying OpenAlex and the Python dictionaries used to create 
visualizations shown. Code to create the visualizations is stored on the [Information Quality Lab GitHub](https://github.com/infoqualitylab/ComputableBibliography-app)

<hr style="border:2px solid gray">

### A note on usage:
  Some errors in OpenAlex metadata have been observed. If OpenAlex metadata is inaccurate, the visualizations and text returned
  will also be inaccurate.

*Examples of inaccurate metadata*
 - Publication https://doi.org/10.18653/v1/P18-1017
    - OpenAlex lists the publication's primary location as "Proceedings of the **60th** Annual Meeting of the Association for Computational
    Linguistics (Volume 1: Long Papers)". Querying "https://api.openalex.org/works/https://doi.org/10.18653/v1/P18-1017"
    - Actual primary location (from following DOI) is "Proceedings of the **56th** Annual Meeting of the Association for
    Computational Linguistics (Volume 1: Long Papers) 
 - Publication https://doi.org/10.1000/182
    - OpenAlex lists publication as "Algorithms based on k-mers for ancient oral metagenomics", a dissertation. Querying
    "https://api.openalex.org/works/https://doi.org/10.1000/182"
    - Actual publication (from following DOI) is *The DOI Handbook* published by the DOI Foundation.