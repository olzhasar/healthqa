import "htmx.org";
import "trix";
import { MeiliSearch } from "meilisearch";

import Alpine from "alpinejs";

function instantSearch() {
  const meiliURL =
    window.location.protocol + "//" + window.location.hostname + ":7700";
  const client = new MeiliSearch({
    host: meiliURL,
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
