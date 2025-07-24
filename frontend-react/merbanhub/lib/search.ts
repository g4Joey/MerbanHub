// search.ts
import type { SearchFilters, SearchResponse, SearchResult } from "@/lib/search"; // Ensure SearchResult is imported if defined in lib/search

export async function searchDocuments(
  filters: SearchFilters
): Promise<SearchResponse> {
  console.log("Sending filters to backend for search:", filters); // Log filters being sent

  try {
    const url = "http://localhost:8080/api/documents/search";
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(filters),
    });

    if (!response.ok) {
      // If the response is not OK (e.g., 4xx, 5xx), try to get an error message
      let errorDetail = `HTTP error! Status: ${response.status}`;
      try {
        const errorBody = await response.json();
        if (errorBody && errorBody.message) {
          errorDetail = errorBody.message;
        } else {
          errorDetail = JSON.stringify(errorBody);
        }
      } catch (e) {
        // If parsing JSON fails, just use status text
        errorDetail = response.statusText;
      }
      console.log("API call failed:", errorDetail);
      throw new Error(`Failed to fetch documents: ${errorDetail}`);
    }

    const data: SearchResponse = await response.json();
    console.log("Received data from backend:", data); // Log the actual data received

    // Basic validation to ensure 'documents' array exists
    if (!data || !Array.isArray(data.documents)) {
      console.error(
        "API response missing 'documents' array or is malformed:",
        data
      );
      throw new Error("Invalid response format: 'documents' array is missing.");
    }

    return data;
  } catch (error: any) {
    console.error(
      "Error during document search API call:",
      error.message || error
    );
    // Re-throw to be caught by react-query, which will set `error` state
    throw error;
  }
}

// NOTE: All commented-out mock data and mock function definitions have been removed
// from this file for clarity and to prevent accidental re-introduction of unreachable code.
// Keep your actual types (SearchFilters, SearchResponse, SearchResult) in "@/lib/search"
// as they are referenced here.
