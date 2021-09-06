import "htmx.org";
import "trix";
import { MeiliSearch } from "meilisearch";

import Alpine from "alpinejs";

function instantSearch() {
  const client = new MeiliSearch({
    host: "http://127.0.0.1:7700",
  });
  const questionsIndex = client.index("questions");

  return {
    searchQuery: "",
    searchResults: [],
    fetchResults(e) {
      const query = e.target.value;
      if (query === "") {
        this.searchResults = [];
      } else {
        questionsIndex.search(query, { limit: 5 }).then((response) => {
          this.searchResults = response["hits"];
        });
      }
    },
  };
}

window.instantSearch = instantSearch;

window.Alpine = Alpine;
Alpine.start();
