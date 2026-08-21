# ::WARNING:: will get rate limited if using Wikipedia / DuckDuckGo too much

# calls query to Wikipedia, DuckDuckGo
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
# calls API for Wikipedia
from langchain_community.utilities import WikipediaAPIWrapper
# allows custom tool build
from langchain.tools import Tool
# calls date and time
from datetime import datetime

# custom tool for writing output to .txt file
def save_to_txt(data: str, filename: str = "research_output.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"

    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)

    return f"Data successfully saved to {filename}"

save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Save structured reseach data to a text file.",
)

# search tool
search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    func=search.run,
    description="Search the web for information",
)

# Wikipedia tool
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100) # larger chars max can trigger rate limiting
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)