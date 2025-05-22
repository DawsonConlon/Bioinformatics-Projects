

import requests
from typing import Optional, Dict

def get_gene_info(gene_name: str, organism: str) -> Optional[Dict[str, str]]: #optinal is saying either return a dictinary of strings or a None 
    """
    Fetch gene information from public NCBI.
    Searches for alternative names using NCBI Entrez API.
    Entrez is a NCBI service that bassicly a search engine for genetic info. 



    Parameters:
    gene_name (str): The name of the gene (e.g., "BRCA1")
    organism (str): The name of the organism (e.g., "Homo sapiens")

    Returns:
    dict: Gene information including sequence and alternative names.
    """
    
    #The URL that will be used to search within the function. 
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    # Step 1: Search for the gene ID
    #/esearch.fcgi is a tool from ncbi that searches databases and returns the IDs that match the request 
    #in this case it will return gene Id's
    search_url = f"{base_url}/esearch.fcgi"
    
    #Define parameters for the search query (a request of specif info from a database)
    search_params = {
        "db": "gene", # Search in the gene database
        "term": f"{gene_name}[Gene Name] AND {organism}[Organism]", #Search the gene name for the given organism
        "retmode": "json" #return the results in the JSON format.
                        #We use JSON format becuase it returns a python dictinary that is easy to read 
                        #It will return a name, description and organism.
    }


    #send the get request to NCBI to search for the gene.
    search_response = requests.get(search_url, params=search_params)

    #Raise an error if requst to NCBI failed.
    search_response.raise_for_status()

    #convert the responce into a JSON text.
    # this allows te responce to be converted into a dictinary. 
    search_data = search_response.json()


    #if no Gene ID is found within the esearch return none 
    if not search_data["esearchresult"]["idlist"]:
        return None  

#get the 1st gene Id from the search result 
    gene_id = search_data["esearchresult"]["idlist"][0]

    
    
    # Step 2: Fetch gene summary

    #This creates the url the computer will use to akwire the summary info on the gene. 
    #esummary.fcgi is a tool that takes a geen id and returns summary info.
    #This is a F string which has been usd multiple times in this script. 
    #It allows me to include bariables within strings.
    summary_url = f"{base_url}/esummary.fcgi"

    #Define the parameters for the search querry 
    summary_params = {
        "db": "gene", #Search in gene database 
        "id": gene_id, #Use the gene Id from earlyer 
        "retmode": "json" #Retuen in JSON format 
    }

    #Send the get request to get gene summary 
    summary_response = requests.get(summary_url, params=summary_params)

    #If request fails raise an error
    summary_response.raise_for_status()
    
    #Convert responce into JSON format
    summary_data = summary_response.json()

    #Create a variable called doc to easily store data.
    #Summary data is are dictinary of data 
    #Result grabs just the results from the dictinary and gene id is saying give e the results for this specific gene 
    doc = summary_data["result"][gene_id]


    #Store the information in the form of a dictinary.
    #I use .get on the doc variabel to akwire the data I want 
    #store this information in a dictinary so it is easy to read 
    #the N/As ae there in the case the function can not get the info requested 
    #and instead of crashing the whole function it will just return a N/A
    gene_info = {
        "Official Symbol": doc.get("name", "N/A"), 
        "Description": doc.get("description", "N/A"),
        "Other Aliases": doc.get("otheraliases", "N/A"),
        "Summary": doc.get("summary", "N/A")
    }

    return gene_info

#usage:
if __name__ == "__main__":  #If you sre running the script directly and not importing the results to a file (allows me to run the code in the command line) 
    gene_data = get_gene_info("hox1", "Burkholderia stagnalis")     #Get gene info on this gene and this organism 
    if gene_data:   #If data is returned 
        for key, value in gene_data.items():    #For each key and its  value within the dictinary 
            print(f"{key}: {value}")    #Print the key and the value 
    else:
        print("Gene not found.")    #If failed print no gene found 

